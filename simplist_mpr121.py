import time 
import board
import busio
import adafruit_mpr121 as mpr121
import datetime as dt
from SPT import SPT
i2c=busio.I2C(board.SCL, board.SDA)

lickdector=mpr121.MPR121(i2c,address=0x5A)
selenoid_RW=SPT.selenoid(20)
while True:
	if lickdector[2].value:
		print(dt.datetime.now().strftime('%Y-%m-%d %H-%m-%s')+'Input 1 touched!')
		selenoid_RW.activate(0.05)
		time.sleep(0.5)
                #time.sleep(0.5)
                #selenoid_RW.activate(0.5)

