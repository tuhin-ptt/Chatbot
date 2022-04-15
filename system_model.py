from __future__ import print_function
import datetime
import pickle
import os.path
import os
import time
import pytz
import subprocess

import wikipedia
import re
import datetime
import uuid
import os
import wmi
from win32com.client import GetObject #for getting current brightness
import ctypes
import pyautogui
import psutil
import re


def wikipedia_search(text):
    text = text.replace("wikipedia", "")
    text = text.replace("tell me about", "")
    text = text.replace("what is", "")
    text = text.replace("who is", "")
    text = text.replace('nstu', 'noakhali science and technology university')
    text = text.replace('ai', 'artificial intelligence')
    text = text.replace('search', "")
    try:
        results = wikipedia.summary(text, sentences=1)
        results = re.sub(re.compile('\((.*?)\)'), "", results)  # removes everything within brackets
        return results
    except Exception as e:
        return False



def say_time():
    hour = datetime.datetime.now().hour
    min = datetime.datetime.now().minute
    if hour < 12:
        res = f'The time is {hour}:{min} AM'
        return res
    elif hour == 12:
        res = f'The time is {hour}:{min} PM'
        return res
    else:
        hour = hour - 12
        res = f'The time is {hour}:{min} PM'
        return res



def brightness(text):
    objWMI = GetObject('winmgmts:\\\\.\\root\\WMI').InstancesOf('WmiMonitorBrightness')
    for obj in objWMI:
        if obj.CurrentBrightness != None:
            current_brightness = int(obj.CurrentBrightness)
        else:
            current_brightness = 0

    if 'decrease' in text or 'reduce' in text or 'down' in text or 'minimize' in text or 'decrement' in text:
        amount = current_brightness - 30
        if amount < 0:
            amount = 0
        dec = wmi.WMI(namespace='wmi')
        methods = dec.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(amount, 0)
        return True
    elif 'increase' in text or 'rise' in text or 'increment' in text or 'raise' in text or 'imporove' in text or 'grow' in text:
        amount = current_brightness + 30
        if amount > 100:
            amount = 100
        ins = wmi.WMI(namespace='wmi')
        methods = ins.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(amount, 0)
        return True
    elif 'adjust' in text:
        adj = wmi.WMI(namespace='wmi')
        methods = adj.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(50, 0)
        return True
    else:
        return False


def retrieve_remeber():
    with open('note.txt', 'r') as f:
        return f.readlines()

    
def battery_condition():
    battery = psutil.sensors_battery()
    plugged = battery.power_plugged
    percent = int(battery.percent)
    secs = battery.secsleft
    h = int(secs / 3600)
    secs = secs % 3600
    m = int(secs / 60)
    if percent < 30 and plugged == "False":
        temp = 'Please connect the charger'
    else:
        temp = ""
    return f'{percent} parcent charge remaining. \n{h} hour {m} minutes left. \n{temp}'







def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service
