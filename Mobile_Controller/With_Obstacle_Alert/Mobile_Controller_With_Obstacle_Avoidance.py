from RPi_Robot_Hat_Lib import RobotController 
import BlynkLib
import time
from Ultrasonic_sens import Ultrasonic 
from IRSens import IRsens 
AUTH = "thhcE_N3Hi7WQTq-K2jHJQC-5x1ng-jZ"



Motor = RobotController()
print("Motor Controller Initialized")
blynk = BlynkLib.Blynk(AUTH) 
print("Blynk Connection Established")
Motor.Brake()
obstacleSens = Ultrasonic(debug=False)
ReverseSens = IRsens()
print("Initialising Obstacle Detection")

Freq = 0
blynk.virtual_write(4,Freq)

@blynk.on("connected")
def blynk_connected():
	print("Blynk server Conected")

	@blynk.on("V4")
	def v4_write_handler(value):
		global Freq
		print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		Freq = VPin
		return Freq
		
	@blynk.on("V0")
	def v0_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Motor.Forward(Freq)
			if VPin == 0:
				Motor.Brake()
		else:
			pass
	
	@blynk.on("V1")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None: 
				if VPin == 1 : 
					Motor.Backward(Freq)	
				else:
					Motor.Brake()
		else:
			pass
	@blynk.on("V2")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Motor.Horizontal_Left(Freq)
			if VPin == 0 :
				Motor.Brake()
		else:
			pass
	@blynk.on("V3")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Motor.Horizontal_Right(Freq)
			if VPin == 0 :
				Motor.Brake()
		else:
			pass
	@blynk.on("V5")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Motor.move(speed=0, turn=Freq)
			if VPin == 0 :
				Motor.Brake()
		else:
			pass
	@blynk.on("V6")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Motor.move(speed=0, turn=-Freq)
			if VPin == 0 :
				Motor.Brake()
		else:
			pass
	blynk.sync_virtual(0,1,2,3,4)

def main():
	
	while True: 
		blynk.run()
		left,front,right = obstacleSens.distances()
		Reverse = ReverseSens.status() 
		# print("Reverse: "+ str(Reverse))

		# print("Left: %.2f, Front: %.2f, Right: %.2f" % (left, front, right))
		
		# print ("Left: %.2f, Front: %.2f, Right: %.2f" % (left, front, right))
		if (left and  front and right) is not None:
			if front < 20 or left < 20 or right < 20 or Reverse == 1 :
				Motor.Brake()
				if front < 20:
					print("CAUTION OBSTACLE AT THE FRONT")
					print("DISTANCE: "+ str(front))
				if left < 20:
					print("CAUTION OBSTACLE AT THE LEFT")
					print("DISTANCE: "+ str(left))  
				if right < 20:
					print("CAUTION OBSTACLE AT THE RIGHT")
					print("DISTANCE: "+ str(right))	
				if Reverse == 1:
					print("CAUTION OBSTACLE AT THE BACK")	
		else:
			print("Error Fetching Sensor Value")
			Motor.Brake()

		# time.sleep(0.2)
		blynk.virtual_write(8, Freq)
		status = blynk.state
		if status == 0: 
			print("Reconnecting...")
			Motor.Brake()
			time.sleep(2)
			blynk.connect()
		else:
			pass
			
			

	




try:
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
  print("Interrupt received (Ctrl+C). Exiting...")
  Freq = 0 
  blynk.virtual_write(4, Freq)
  blynk.virtual_write(8, Freq)
  Motor.cleanup()
  obstacleSens.cleanup()



	

  

