echo "Installing required libraries and dependencies"  
pip install -r requirements.txt 

echo "Replacing RPi.GPIO" to "rpi-lgpio" 
pip uninstall -y RPi.GPIO rpi-gpio rpi-lgpio
sudo apt remove python3-rpi.gpio
sudo apt remove RPi.GPIO
pip install rpi_lgpio==0.6 

echo "Checking all installed Libraries"
pip list  

echo "Installation and Setup complete" 