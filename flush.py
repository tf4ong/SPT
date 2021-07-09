from time import time, sleep 
import board 
import busio 
import numpy as np 
from SPT import SPT 
from RFIDTagReader import TagReader 
import RPi.GPIO as GPIO 
import datetime as dt 
import adafruit_mpr121 as mpr121 
import sys 
import os 
from _thread import start_new_thread 
import argparse 
import pdb

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
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('-task',metavar='task_name',type=str,help='Task settings to run SPT',default='none')
    args=parser.parse_args()
    if args.task is 'none':
        task_name=input('Enter the task name: ')
    else:
        task_name=args.task
    task_settings=load_settings(task_name)
    selenoid_pin_LW=task_settings.task_config['selenoid_pin_LW']
    selenoid_pin_LS=task_settings.task_config['selenoid_pin_LS'] 
    selenoid_pin_RW=task_settings.task_config['selenoid_pin_RW']
    selenoid_pin_RS=task_settings.task_config['selenoid_pin_RS']
    selenoid_RW=SPT.selenoid(selenoid_pin_RW)
    selenoid_RS=SPT.selenoid(selenoid_pin_RS)
    selenoid_LW=SPT.selenoid(selenoid_pin_LW)
    selenoid_LS=SPT.selenoid(selenoid_pin_LS)
    count=0
    now=dt.datetime.now()
    while True:
        try:
            #count+=1
            #selenoid_LS.flush()
            #selenoid_RS.flush()
            selenoid_LW.flush()
            selenoid_RW.flush()
            sleep(0.07)
            #selenoid_LS.close()
            #selenoid_RS.close()
            #selenoid_LW.close()
            #selenoid_RW.close()
            #print(count)
            count+=1
            #sleep(0.1)
        except KeyboardInterrupt:
            selenoid_LS.close()
            selenoid_RS.close()
            selenoid_LW.close()
            selenoid_RW.close()
            now2=dt.datetime.now()
            total_seconds=(now2-now).total_seconds()
            print(count)
            print(total_seconds)
            print('Finished Flushing')
            sys.exit()

