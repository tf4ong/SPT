                             
#setup script
#!/bin/bash
# This script should completely set up SPT on a blank Raspberry pi.
#$ sudo chmod 777 AFH_script.sh
#$ ./AFH_script.sh

mkdir SPT
cd SPT


#updates pi, bypassing y/n prompts, clears out unused packages
sudo apt-get update && sudo apt-get upgrade -y && apt-get autoremove && apt-get autoclean



echo "cloning pulsedThread and building makefile"
git clone https://github.com/jamieboyd/pulsedThread.git
cd pulsedThread
sudo make
sudo make install
python3 setup_ptGreeter.py install
python3 setup_pyPTpyFuncs.py install
cd ..

echo "Cloning and installing pyaudio and dependencies"
sudo git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get install python-dev
cd pyaudio
sudo python3 setup.py install
cd ..

echo "Cloning GPIO_Thread"
git clone https://github.com/jamieboyd/GPIO_Thread.git
cd GPIO_Thread
#maybe use for a later type of cage if interesting in body weight 
echo "Installing Autoweight dependency HX711"
python3 HX711_setup.py install 

python3 SimpleGPIO_setup.py install
python3 StepperMotor_setup.py install 
python3 leverThread_setup.py install 
python3 PWM_thread_setup.py install
cd ..


echo "cloning rfid reader"
git clone https://github.com/jamieboyd/RFIDTagReader.git
cd RFIDTagReader
python3 RFIDTagReader_setup.py install
cd ..


echo "cloning adafruit circuit python-mpr121 & blinka dependency"
sudo pip3 install blinka
sudo pip3 install adafruit-circuitpython-mpr121


echo "cloning adafruit GPIO"
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git 
cd Adafruit_Python_GPIO
sudo python3 setup.py install
cd ..

echo "installing pypy and remaining modules (mysql-server, php-mysql, pymysql)"
sudo apt-get install pypy mysql-server php-mysql -y
python3 -m pip install PyMySQL 


echo "setting up database"

sudo apt-get install libatlas-base-dev -y 
sudo apt-get install python3-scipy -y
sudo pip3 install imreg_dft
sudo pip3 install matplotlib
sudo pip3 install pynput
sudo pip3 install pandas
sudo pip3 install h5py
sudo pip3 install pandas 
sudo pip3 install h5py #Not a typo. Sometimes needs to be run twice
sudo apt-get install libhdf5-dev -y







