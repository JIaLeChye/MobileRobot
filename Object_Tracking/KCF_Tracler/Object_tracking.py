import cv2
import numpy as np
from RPi_Robot_Hat_Lib import RobotController
from picamera2 import Picamera2
from libcamera import controls, Transform 
import time

tracker = cv2.TrackerKCF_create() 
frame_width = 640  
frame_height = 480
cap = Picamera2()
cap.configure(cap.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)},transform=Transform(vflip=1)))
cap.set_controls({"AfMode": controls.AfModeEnum.Continuous})
cap.start()

Motor = RobotController()
# enc = Encoder()

vertical = 2
horizontal = 1
Motor.set_servo(vertical, 180)
Motor.set_servo(horizontal, 90)
# All process should be start after the servo @ camera position is set !
time.sleep(1)





def tracking(frame, x,y,w,h):
    
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame, "Tracking", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to quit", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, f"X:{x} , Y: {y}", (x ,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # Calculate the center of Bounding Box 
    center_x = x + w // 2
    center_y = y + h // 2
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Draw a circle at the center
    # Tracking Logic 
    # Frame is 640x480. 
    # center_x: 320 is middle. Deadzone is 300 to 340.
    # center_y: 0 is top (far), 480 is bottom (close).
    
    # 1. Object is far away (y between 100 and 240) -> Move faster
    if 100 < center_y < 240:
        if center_x < 300:
            print("Far: Turn Left")
            Motor.move(speed=0, turn=-20) 
        elif center_x > 340:
            print("Far: Turn Right")
            Motor.move(speed=0, turn=20)
        else:
            print("Far: Forward")
            Motor.Forward(20)
            
    # 2. Object is closer (y between 240 and 440) -> Slow approach        
    elif 240 <= center_y < 440:
        if center_x < 300:
            print("Close: Turn Left")
            Motor.move(speed=0, turn=-10)
        elif center_x > 340:
            print("Close: Turn Right")
            Motor.move(speed=0, turn=10)
        else:
            print("Close: Forward")
            Motor.Forward(10)
            
    # 3. Object is very close (y > 440) or too high up (y < 100) -> Stop
    else:
        print("Stopping Break") 
        Motor.Brake()
    
    

def main(): 
    global tracker
    cv2.namedWindow('Tracking_Area')
    
    print("\n" + "="*58)
    print("1. Camera feed starting... Position your object in view.")
    print("2. Press ENTER or 's' to pause the feed and enter selection mode.")
    print("3. Drag a box around the object.")
    print("4. Press SPACE or ENTER to confirm and start tracking.")
    print("5. Press 'q' at any time to quit.")
    print("="*58 + "\n")
    
    # Phase 1: Live feed so user can position the object
    while True:
        frame = np.ascontiguousarray(cap.capture_array())
        
        # Draw instructions on a copy so we don't mess up the clean frame
        disp_frame = frame.copy()
        cv2.putText(disp_frame, "Press ENTER to select target", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow('Tracking_Area', disp_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return
        elif key == 13 or key == ord('s'):  # 13 is ENTER key
            break
            
    # Phase 2: Selection Mode (Frame is frozen)
    # The last captured 'frame' is used for selectROI
    bbox = cv2.selectROI('Tracking_Area', frame, showCrosshair=True, fromCenter=False)
 
    # Check if a valid ROI was selected before passing to tracker
    if bbox == (0, 0, 0, 0):
        print("No ROI selected. Exiting...")
        return

    # Extract the template image for automatic recovery later
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    templates = [frame[y:y+h, x:x+w].copy()]
    frame_counter = 0

    # Initialize tracker with first frame and bounding box
    tracker.init(frame, bbox)
    print("Tracking started! Press 'q' to stop.")
    
    # Phase 3: Tracking Loop
    while True:
        frame = np.ascontiguousarray(cap.capture_array())  # Read frame
        
        # Tracking mode: update the tracker and draw the tracked bounding box
        success, box = tracker.update(frame)

        if success:
            (x, y, w, h) = [int(v) for v in box]
            tracking(frame, x,y,w,h)
            
            # Periodically save a new template to adapt to scale/rotation changes
            frame_counter += 1
            if frame_counter % 30 == 0:
                new_template = frame[max(0,y):y+h, max(0,x):x+w].copy()
                if new_template.size > 0:
                    templates.append(new_template)
                    # Keep the original (index 0) + up to 3 most recent templates
                    if len(templates) > 4:
                        templates.pop(1)
        else:
            Motor.Brake() 
            cv2.putText(frame, "Lost object. Searching...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # --- Automatic Recovery using Multi-Template Matching ---
            best_val = 0
            best_loc = None
            best_template = None
            
            for tmpl in templates:
                res = cv2.matchTemplate(frame, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val > best_val:
                    best_val = max_val
                    best_loc = max_loc
                    best_template = tmpl
            
            # If we find a good match (confidence > 0.6)
            if best_val > 0.6:
                recovery_x, recovery_y = best_loc
                th, tw = best_template.shape[:2]
                recovered_bbox = (recovery_x, recovery_y, tw, th)
                
                # Re-initialize tracker with the newly found location
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, recovered_bbox)
                print(f"Object recovered! (Confidence: {best_val:.2f}, Templates: {len(templates)})")
            else:
                # Still lost, ask user if they want to manually re-select
                cv2.putText(frame, "Press 'r' to manually reselect", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        cv2.imshow('Tracking_Area', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Tracker is lost, let user manually re-draw the box
            Motor.Brake()
            print("\nRe-entering selection mode...")
            bbox = cv2.selectROI('Tracking_Area', frame, showCrosshair=True, fromCenter=False)
            if bbox != (0, 0, 0, 0):
                # Update our recovery templates list completely
                x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                templates = [frame[y:y+h, x:x+w].copy()]
                frame_counter = 0
                
                # Must create a fresh tracker instance to clear old tracking memory
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, bbox)
                print("Tracking resumed!")

try:
    if __name__ == '__main__':
        main()
except KeyboardInterrupt:
    print("KeyboardInterrupt")
    
finally:
    Motor.cleanup()
    # enc.stop()
    cap.stop()
    cv2.destroyAllWindows()
    print("Program Terminated \nExiting....")
