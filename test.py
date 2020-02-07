from time import time, sleep
import board
import busio
import numpy as np
from SPT import SPT 
import RFIDTagReader
from RFIDTagReader import TagReader
import RPi.GPIO as GPIO 
import datetime as dt
import adafruit_mpr121 as mpr121
import sys
import os
from _thread import start_new_thread
'''
Hardware variables to be read by json file
'''
def load_settings(task_name):
    task_settings=SPT.task_settings(task_name)
    try:
        task_settings.task_config
    except AttributeError:
        print('Creating new task settings file')
        task_settings.write_new_settings()
    else: 
        pass
    return  task_settings
####default settings used while building the setup 
'''
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
buzzer_pin=24
serialPort = '/dev/ttyUSB0'
globalReader = None
globalTag = 0
vid_folder='/home/Documents/'
k_day_hour=19
'''
'''
sample mice dic for json
SPT_levels
    0: with entry reward (dispensed 50% at either right or left), with both sides just giving out water
    1: no entry reward, water dispensed at one side, while the other produces a negative feedback
    2. no entry, SPT
'''
#mice={801020013:{'SPT_level':1,'SPT_pattern':'R'}}
"""
Main loop for SPT 
"""
#Start of main function to run SPT
def main():
    global globalReader
    global globalTag
    global cage
    global log
    global GPIO
    global mice_dic 
    globalReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    globalReader.installCallback (tag_in_range_pin)
    #Starting loop to check time passed
    #After n hours (in json file), the SPT spouts are switched from each sides
    now=dt.datetime.now()
    #reads the mouse dict file
    mice_dic=SPT.mice_dict(cage)
    #the text spacer: comma for csv
    txtspacer=input('txt spacer?')
    #loop to check time
    while True:
        now=dt.datetime.now()
        print ("Waiting for mouse....")
        #starts new text file and switches spouts
        log=SPT.data_logger(cage,txtspacer)
        mice_dic.spout_swtich()
        #if within same day, the main loop is ran
        while dt.datetime.now()-now < dt.timedelta(minutes=hours*60):
            #Waiting for a tag to be read
            if RFIDTagReader.globalTag == 0:
                sleep (0.02)
            else:
             #tag just been read, starting video and logging events 
                tag = RFIDTagReader.globalTag
                #import pdb; pdb.set_trace()
                filename=vs.record(tag)
                print(mice_dic.mice_config)
                print(str(tag))
                print(filename)
                log.event_outcome(mice_dic.mice_config,str(tag),'VideoStart',filename)
                #if at SPT level 0, an entry reward is given, if not pass 
                if mice_dic.mice_config[str(tag)]['SPT_level']== 0:
                    probability=np.random.choice([0,1],p=[0.5,0.5])
                    if int(probability)==1:
                        selenoid_LW.activate(0.5)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward_L')
                        pass
                    elif int(probability)==0:
                        selenoid_RW.activate(0.5)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward_R')
                        pass
                else:
                    log.event_outcome(mice_dic.mice_config,str(tag),'Entered','No_Entry_Reward')
                #loop for tag read and in range
                while RFIDTagReader.globalTag == tag:
                    while GPIO.input(tag_in_range_pin) == GPIO.HIGH:
                        #creates a temporary tag for reference, temp tag is recorded if not tag is not zero,globaltag is reset to 0 each time
                        if tag !=0:
                            temp_tag=tag
                        else:
                            pass
                 #the spt task at three different levels 
                        if lickdector[0].value:
                            if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                selenoid_RW.activate(0.1)
                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                    selenoid_RW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                    #speaker on 
                                    print('Speaker on\n')
                                    buzzer.buzz()
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                    sleep(0.2)
                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                    selenoid_RW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Sucrose_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                    selenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                        elif lickdector[1].value:
                            if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                selenoid_LW.activate(0.1)
                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                    print('Speaker on\n')
                                    buzzer.buzz()
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-leftside','No_Reward')
                                    sleep(0.2)
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                    selenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                    selenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                    selenoid_LS.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Sucrose_Reward')
                        else:
                            sleep(0.02)
                    # tag just went out of range, loop for grace period
                    if GPIO.input(tag_in_range_pin) == GPIO.LOW: 
                    #starts the grace timer, within the grace period the task still continues and waits for the tag to return
                        grace_start=time()
                        while GPIO.input(tag_in_range_pin) == GPIO.LOW and time()-grace_start<gracePeriod:
                            print ("loop5....")
                            print(gracePeriod)
                            print(temp_tag)
                            if lickdector[0].value:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                    selenoid_RW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                    if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                        selenoid_RW.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                    elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                        #speaker on 
                                        print('Speaker on\n')
                                        buzzer.buzz()
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                        sleep(0.2)
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                    if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                        selenoid_RW.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Sucrose_Reward')
                                    elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                        selenoid_LW.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                            elif lickdector[1].value:
                                if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                    selenoid_LW.activate(0.1)
                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                    if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                        print('Speaker on\n')
                                        buzzer.buzz()
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-leftside','No_Reward')
                                        sleep(0.2)
                                    elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                        selenoid_LW.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                    if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                        selenoid_LW.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                    elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                        selenoid_LS.activate(0.1)
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Sucrose_Reward')
                            sleep(0.02)
                       #When tag returns (tag read is the same as temp tag), assigns the gloablTag to temp the tag read and returns to the previous loop
                            tag = RFIDTagReader.globalTag
                            print(tag,RFIDTagReader.globalTag)
                            if tag == temp_tag:
                                RFIDTagReader.globalTag=tag
                       #if the time passes the grace period,stops recording and logs events then breaks out of the loop to get back the previous loop
                        if GPIO.input(tag_in_range_pin) == GPIO.LOW and time()-grace_start>=gracePeriod:   
                            print('grace period expired')
                            vs.stop_record()
                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'VideoEnd',filename)
                ###sleep time must match reward and buzzer sleep time
                            sleep(0.05)
                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'Exit','None')
                            print('Waiting for mouse')
                            #break to get back in loop 2 
                            break

#Running the script with some settings read from json file
if __name__ == '__main__':
    task_name=input('Enter the task name: ')
    task_settings=load_settings(task_name)
    gracePeriod=5
    try: 
        tag_in_range_pin=task_settings.task_config['tag_in_range_pin']
        selenoid_pin_LW=task_settings.task_config['selenoid_pin_LW']
        selenoid_pin_LS=task_settings.task_config['selenoid_pin_LS']
        selenoid_pin_RW=task_settings.task_config['selenoid_pin_RW']
        selenoid_pin_RS=task_settings.task_config['selenoid_pin_RS']
        buzzer_pin=task_settings.task_config['buzzer_pin']
        vid_folder=task_settings.task_config['vid_folder']
        hours=task_settings.task_config['hours']
        serialPort = '/dev/ttyUSB0'
        i2c=busio.I2C(board.SCL,board.SDA)
        lickdector=mpr121.MPR121(i2c,address=0x5A)
        selenoid_RW=SPT.selenoid(selenoid_pin_RW)
        selenoid_RS=SPT.selenoid(selenoid_pin_RS)
        selenoid_LW=SPT.selenoid(selenoid_pin_LS)
        selenoid_LS=SPT.selenoid(selenoid_pin_LW)
        globalReader = None
        globalTag = 0
        vs=SPT.piVideoStream(folder=vid_folder)
        vs.cam_setup()
        buzzer=SPT.buzzer(buzzer_pin,1500,50)
    except Exception as e: 
        print(e)
        print('Error in iniatializing hardware, please check wiring and task settings')
        print('System shuting down')
        sys.exit()
    cage=input('cage?')
    if not os.path.exists(cage+'/'):
        os.mkdir(cage+'/')
        print(cage+' Dictionary created')
    mice_dic=SPT.mice_dict(cage)      
    while True:
        try:
            if not os.path.exists(cage+'/'):
                os.mkdir(cage+'/')
                print(cage+' Dictionary created')
            mice_dic=SPT.mice_dict(cage)
            try: 
                main()
            #the SPT option manual for SPT
            except KeyboardInterrupt:
                #print('1')
                inputStr = '\n************** SPT Manager ********************\nEnter:\n'
                inputStr += '1 to change SPT level for mice\n'
                inputStr += '2 to change SPT task settings\n'
                inputStr += '3 to add mice\n'
                inputStr += '4 to remove mice\n'
                inputStr += 'R to Return to head fix trials\n'
                inputStr += 'Q to quit\n:'
                event = input(inputStr)
                if event == 'r' or event == "R":
                    pass
                elif event == 'q' or event == 'Q':
                    sys.exit()
        except Exception as anError:
            print('SPT error:' + str(anError))
            raise anError
        finally:
            print('Quitting SPT run')
            GPIO.cleanup()
            sys.exit()
