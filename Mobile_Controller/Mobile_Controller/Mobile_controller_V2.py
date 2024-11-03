from RPi_Robot_Hat_Lib import RobotController 
import BlynkLib
import time
import sys

AUTH = "thhcE_N3Hi7WQTq-K2jHJQC-5x1ng-jZ"


	
Robot = RobotController()
print("Robot Controller Connection Established")
blynk = BlynkLib.Blynk(AUTH) 
print("Blynk Connection Established")
Freq = 0
blynk.virtual_write(4,0)
Robot.Brake() 
print("Robot Stopped") 
		 






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
				Robot.Forward(Freq)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	
	@blynk.on("V1")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Robot.Backward(Freq)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	@blynk.on("V2")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Robot.Horizontal_Left(Freq)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	@blynk.on("V3")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Robot.Horizontal_Right(Freq)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	@blynk.on("V5")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Robot.move(speed=0, turn=-10)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	@blynk.on("V6")
	def v1_write_handler(value):
		# print('Current slider value: {}'.format(value[0]))
		VPin = int(value[0])
		if VPin is not None:
			if VPin == 1 :
				Robot.move(speed=0, turn=10)
			if VPin == 0 :
				Robot.Brake()
		else:
			pass
	blynk.sync_virtual(0,1,2,3,4)

	while True: 
		blynk.run()
		blynk.virtual_write(8, Freq)
		 
		# time.sleep(0.2)
		status = blynk.state
		if status == 0:
			print("Reconnecting...")
			Robot.Brake()
			time.sleep(2)
			blynk.connect()
			
			

	




try:
	if __name__ == "__main__":
		blynk_connected()
except KeyboardInterrupt:
  print("Interrupt received (Ctrl+C). Exiting...")
  Freq = 0 
  blynk.virtual_write(4, Freq)
  blynk.virtual_write(8, Freq)
  Robot.Brake()
#   enc.stop()
  sys.exit(0)

	

  

