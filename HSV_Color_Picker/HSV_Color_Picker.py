from flask import Flask,Response, render_template, request
import cv2
import numpy as np
from picamera2 import Picamera2 


app = Flask(__name__, template_folder='Web')

cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
cam.start() 

h_l = 0
s_l = 179
v_l = 0 

h_u = 255
s_u = 0
v_u = 255 



def get_frame():
    frame = cam.capture_array()
    frame = process_frame(frame)
    return frame

def process_frame(frame, h_l,s_l,v_l, h_u, s_u, v_u ):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_color = np.array([h_l, s_l, v_l])
    upper_color = np.array([h_u, s_u, v_u])
    mask = cv2.inRange(hsv, lower_color, upper_color)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result 


def encode_frame():
    while True: 

        frame = get_frame()
        h_l, s_l, v_l, h_u, s_u, v_u = color_range()
        mask = process_frame(frame, h_l, s_l, v_l, h_u, s_u, v_u)
        ret, buffer = cv2.imencode('.jpg', mask)
        print("Encoding")

        if ret is not True:
            raise Exception("Encoding failed")
        else: 
            mask = buffer.tobytes()
            print("Encoding Sucess")
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture')
def capture():
    processed_frame = encode_frame()
    return Response(processed_frame, mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/color_range', methods=['POST'])
def color_range():
    h_l = int(request.form['h_l'])
    s_l = int(request.form['s_l'])
    v_l = int(request.form['v_l'])

    h_u = int(request.form['h_u'])
    s_u = int(request.form['s_u'])
    v_u = int(request.form['v_u'])

    return h_l, s_l, v_l, h_u, s_u, v_u, 'Track Bar Updated'


def main():
    frame = get_frame()
    process_frame(frame)
    print("Step 1")

    app.run(host='0.0.0.0', port=5000)
