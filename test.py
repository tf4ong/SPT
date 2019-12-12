from time import time, sleep
import board
import busio
from SPT import SPT
import RFIDTagReader
from RFIDTagReader import TagReader
import RPi.GPIO as GPIO 
import datetime as dt
import adafruit_mpr121 as mpr121
'''
Default/temp variables 
need to integrate in json files to read settings
'''
res=[1080,720]
serialPort = '/dev/ttyUSB0'
tag_in_range_pin=18
selenoid_pin_LW=26
selenoid_pin_LS=13
selenoid_pin_RW=21
selenoid_pin_RS=12
i2c=busio.I2C(board.SCL,board.SDA)
lickdector=mpr121.MPR121(i2c,address=0x5A)
selenoid_RW=SPT.selenoid(selenoid_pin_RW)
selenoid_RS=SPT.selenoid(selenoid_pin_RS)
selenoid_LW=SPT.selenoid(selenoid_pin_LS)
selenoid_LS=SPT.selenoid(selenoid_pin_LW)
globalReader = None
globalTag = 0
vid_folder='/home/Documents/'
mice={801010565:{'SPT_level':1,'SPT_pattern':'R'}}
"""
Main loop for SPT 
Need to think of open design for tunnel
"""
vs=SPT.piVideoStream(folder='/home/pi/Documents')
vs.cam_setup()
def main ():
    global globalReader
    global globalTag
    globalReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    globalReader.installCallback (tag_in_range_pin)
    cage=input('cage?')
    txtspacer=input('txt spacer?')
    log=SPT.data_logger(cage,txtspacer)
    print ("Waiting for mouse....")
    while True:
        try:
            while RFIDTagReader.globalTag == 0:
                sleep (0.02)
            tag = RFIDTagReader.globalTag
            filename=vs.record(tag)
            log.event_outcome(mice,str(tag),'VideoStart',filename)
            if mice[tag]['SPT_level']== 0:
                if mice[tag]['SPT_pattern']=='R':
                    selenoid_LW.activate(0.5)
                    log.event_outcome(mice,str(tag),'Entered','Entry_Reward')
                elif mice[tag]['SPT_pattern']=='L':
                    selenoid_RW.activate(0.5)
                    log.event_outcome(mice,str(tag),'Entered','Entry_Reward')
            else:
                log.event_outcome(mice,str(tag),'Entered','No_Entry_Reward')
            while RFIDTagReader.globalTag == tag:
                while GPIO.input(tag_in_range_pin) == GPIO.HIGH:
                    if lickdector[0].value:
                        if mice[tag]['SPT_pattern']=='R':
                            selenoid_LW.activate(0.2)
                            log.event_outcome(mice,str(tag),'licked-Rightside','Sucrose_Reward')
                        elif mice[tag]['SPT_pattern']=='L':
                            selenoid_RW.activate(0.2)
                            sleep(0.02)
                            log.event_outcome(mice,str(tag),'licked-Rightside','Water_Reward')
                    elif lickdector[1].value:
                        if mice[tag]['SPT_pattern']=='R':
                            selenoid_LW.activate(0.2)
                            log.event_outcome(mice,str(tag),'licked-Leftside','Water_Reward')
                        elif mice[tag]['SPT_pattern']=='L':
                            selenoid_LS.activate(0.2)
                            log.event_outcome(mice,str(tag),'licked-Leftside','Sucrose_Reward')
                    else:
                        sleep(0.05)
                vs.stop_record()
                log.event_outcome(mice,str(tag),'VideoEnd',filename)
            sleep(0.02)
            log.event_outcome(mice,str(tag),'Exit','None')
            print('Waiting for mouse')
        except KeyboardInterrupt:
            del globalReader
            print ("Quitting")
            break
if __name__ == '__main__':
   main()
