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
    #initiating counter to check days
    count=0
    while True:
        count+=1
        now=dt.datetime.now()
        current_touched = cap.touched()
        print ("Waiting for mouse....")
        #starts new text file and switches spouts if not on day 1
        log=SPT.data_logger(cage,txtspacer)
        #changes the spouts if day counter is not one 
        if count != 1:
            mice_dic.spout_swtich()
            print('Spout Switched')
        else:
            pass
        #if within same day, the main loop is ran
        while dt.datetime.now()-now < dt.timedelta(minutes=hours*60):
            #Waiting for a tag to be read
            if RFIDTagReader.globalTag == 0:
            #
                try: 
                    vs.stop_record()
                    print('camera stopped')
                except Exception:
                    pass
                sleep (0.2)
            else:
             #tag just been read, starting video and logging events 
                tag = RFIDTagReader.globalTag
                #import pdb; pdb.set_trace()
                filename=vs.record(tag)

                log.event_outcome(mice_dic.mice_config,str(tag),'VideoStart',filename)
                #if at SPT level 0, an entry reward is given, if not pass 
                '''
                if mice_dic.mice_config[str(tag)]['SPT_level']== 0:
                    probability=np.random.choice([0,1],p=[0.5,0.5])
                    if int(probability)==1:
                        selenoid_LW.activate(0.7)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward_L')
                        pass
                    
                    elif int(probability)==0:
                        selenoid_RW.activate(0.7)
                        log.event_outcome(mice_dic.mice_config,str(tag),'Entered','Entry_Reward_R')
                        pass
                
                else:
                '''
                log.event_outcome(mice_dic.mice_config,str(tag),'Entered','No_Entry_Reward')
        
                lick_count_R=0
                lick_count_L=0
                #loop for tag read and in range
                while RFIDTagReader.globalTag == tag:
                    last_touched = cap.touched()
                    while GPIO.input(tag_in_range_pin) == GPIO.HIGH:
                        #creates a temporary tag for reference, temp tag is recorded if not tag is not zero,globaltag is reset to 0 each time
                        if tag !=0:
                            temp_tag=tag
                        else:
                            pass
                 #the spt task at three different levels 
                        for i in range(2):
                            current_touched = cap.touched()
                            pin_bit = 1 << i
                            if current_touched & pin_bit and not last_touched & pin_bit:
                                if i==1:
                                    lick_count_R+=1
                                    if lick_count_R%2 == 0:
                                        if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                            selenoid_RW.activate(0.035)
                                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                        elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                selenoid_RW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                #speaker on 
                                                #print('Speaker on\n')
                                                #buzzer.buzz()
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                        elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                selenoid_RS.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Sucrose_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                selenoid_RW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                    else:
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                elif i==0:
                                    lick_count_L+=1
                                    if lick_count_L%2 == 0:
                                        if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                            selenoid_LW.activate(0.035)
                                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                        elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                #print('Speaker on\n')
                                                #buzzer.buzz()
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','No_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                selenoid_LW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                        elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                selenoid_LW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                selenoid_LS.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Sucrose_Reward')
                                    else:
                                        log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-leftside','No_Reward')
                                else:
                                    pass
                        last_touched = current_touched
                        sleep(0.05)
                    # tag just went out of range, loop for grace period
                    if GPIO.input(tag_in_range_pin) == GPIO.LOW: 
                    #starts the grace timer, within the grace period the task still continues and waits for the tag to return
                        grace_start=time()
                        print('GracePeriod Starts')
                        while GPIO.input(tag_in_range_pin) == GPIO.LOW and time()-grace_start<gracePeriod:
                            #last_touched = cap.touched()
                     #the spt task at three different levels 
                            for i in range(2):
                                current_touched = cap.touched()
                                pin_bit = 1 << i
                                if current_touched & pin_bit and not last_touched & pin_bit:
                                    if i==1:
                                        lick_count_R+=1
                                        print(lick_count_R)
                                        if lick_count_R%2 == 0:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                                selenoid_RW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                    selenoid_RW.activate(0.2)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                    #speaker on 
                                                    #print('Speaker on\n')
                                                    #buzzer.buzz()
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                    selenoid_RS.activate(0.035)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Sucrose_Reward')
                                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                    selenoid_RW.activate(0.035)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','Water_Reward')
                                        else:
                                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Rightside','No_Reward')
                                    elif i==0:
                                        lick_count_L+=1
                                        print(lick_count_L)
                                        if lick_count_L%2 == 0:
                                            if mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==0:
                                                selenoid_LW.activate(0.035)
                                                log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==1:
                                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                    #print('Speaker on\n')
                                                    #buzzer.buzz()
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','No_Reward')
                                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                    selenoid_LW.activate(0.2)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                            elif mice_dic.mice_config[str(temp_tag)]['SPT_level'] ==2:
                                                if mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='R':
                                                    selenoid_LW.activate(0.035)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Water_Reward')
                                                elif mice_dic.mice_config[str(temp_tag)]['SPT_Pattern']=='L':
                                                    selenoid_LS.activate(0.035)
                                                    log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','Sucrose_Reward')
                                        else:
                                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'licked-Leftside','No_Reward')
                                else:
                                    pass
                            last_touched = current_touched
                            sleep(0.05)
                       #When tag returns (tag read is the same as temp tag), assigns the gloablTag to temp the tag read and returns to the previous loop
                            tag = RFIDTagReader.globalTag
                            if tag == temp_tag:
                                RFIDTagReader.globalTag=temp_tag
                            else:
                                RFIDTagReader.globalTag=tag
                       #add loop/condition to break if new tag != temp tag; breaks out of loop and stop video recording and assigns new mice entry and video start
                       #if the time passes the grace period,stops recording and logs events then breaks out of the loop to get back the previous loop
                        if GPIO.input(tag_in_range_pin) == GPIO.LOW and time()-grace_start>=gracePeriod:   
                            print('grace period expired')
                            vs.stop_record()
                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'VideoEnd',filename)
                            sleep(0.05)
                            log.event_outcome(mice_dic.mice_config,str(temp_tag),'Exit','None')
                            print('Waiting for mouse')
                            #break to get back in loop 2 
                            break
#Running the script with some settings read from json file
if __name__ == '__main__':
    task_name=input('Enter the task name: ')
    task_settings=load_settings(task_name)
    #mice interference
    gracePeriod=0.7
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
        cap = mpr121.MPR121(i2c,address=0x5A)
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
            #the SPT option manual for SPT, currently just a template
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
