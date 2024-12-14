import os
import cv2
import numpy

# Server Coms
from datetime import datetime, timedelta
from time import sleep
import requests
import pyrebase

# Sensors
import board
import busio
import RPi.GPIO as GPIO
import adafruit_bmp280
import adafruit_bh1750
import adafruit_ahtx0
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Local LIBS
import sensors_periferal
import hardware_control

# Yolo detection
from ultralytics import YOLO

# Functions
def authenticate():
    response = auth.sign_in_with_email_and_password("piunit@unit.sk","12345678")
    token = response['idToken']
    print(token)
    return token

def storePicture(x,now):
    filename1 = "cam-" + now.strftime("%Y-%m-%d_%H.%M.%S.jpg")
    filename = "/home/pi/Desktop/"+filename1
    cap = cv2.VideoCapture(0)
    # Perform inference
    ret,frame = cap.read()
    out = cv2.imwrite(filename, frame)
    output = model.predict(source=filename, conf=0.5, save=False)
    outPlot = output[0].plot()
    cv2.imwrite(filename,outPlot)
    print(filename +" saved")
    storage.child(filename1).put(filename)
    print("Image sent")
    os.remove(filename)
    print("File Removed")
    return x
#___________________________________________________

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)
ads.gain = 1

sensor_bh1750, is_bh1750_availible = sensors_periferal.initBH1750(i2c) # Lux sensor
sensor_bmp280, is_bmp280_availible = sensors_periferal.initBMP280(i2c) # temp/bar sensor
sensor_ahtx0, is_ahtx0_availible = sensors_periferal.initAHTx0(i2c) # temp/bar sensor

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

#----light--------
GPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
servoLight = None
lightState = False

#----heater--------
GPIO.setup(26,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)

#----heater--------
GPIO.setup(6,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)

#----fan--------
GPIO.setup(23,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.output(23, GPIO.LOW)
fan = GPIO.PWM(18,50)
fan.start(0)
fanLoop = False
fanState = False
fanStateChange = False

urlData="https://greenhouseapp-a928f-default-rtdb.firebaseio.com/data"
url2="https://greenhouseapp-a928f-default-rtdb.firebaseio.com/settings"
print(url2)

firebaseConfig = {
  'apiKey': "AIzaSyCqiYMhVnBFlwBuboCePIiYuKYirI1O6Vk",
  'authDomain': "greenhouseapp-a928f.firebaseapp.com",
  'databaseURL': "https://greenhouseapp-a928f-default-rtdb.firebaseio.com",
  'projectId': "greenhouseapp-a928f",
  'storageBucket': "greenhouseapp-a928f.appspot.com",
  'messagingSenderId': "770211079525",
  'appId': "1:770211079525:web:0f03c44ca33a0ae056ed8c",
  'measurementId': "G-S2CLPJ09XP"
}

model = YOLO('bestL.pt')
firebase = pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
storage = firebase.storage()
timer = 0
now = datetime.now()
nextLog = now
lastLog = now

token = authenticate()

while True:
    # try:
    r= requests.get(url2 + ".json?auth="+token)
    data=r.json()
    
    x=data['sampling_time']
    timeStart = data['light_start']
    timeDur = data['light_duration']
    temp = data['temperature']
    watering = data['watering']
    fanSett = data['fan_state']
    print(fanSett)
    
    now = datetime.now()
    begin = now.replace(hour=int(timeStart), minute=0, second=0, microsecond=0)
    stop = now.replace(hour=(int(timeStart)+int(timeDur)), minute=0, second=0, microsecond=0)
#        print(stop)
#         print(begin)
    if int(fanSett) == 1:
        hardware_control.toggleFan(True,fan)
    if int(fanSett) == 0:
        hardware_control.toggleFan(False,fan)

    if now > stop and lightState == True:
        lightState = hardware_control.toggleLight(True)
    if now < stop and now > begin and lightState == False:
        lightState = hardware_control.toggleLight(False)
    
    hardware_control.toggleHeating(temp,sensor_bmp280)
    hardware_control.startWatering(watering)
    print(x)
    
    if now < stop and now > begin:
        if now >= nextLog:
            lastLog = now
            print(nextLog)
            store = storePicture(x,now)
            data = sensors_periferal.getDataValues(chan,chan1,chan2,chan3,sensor_bh1750,sensor_bmp280,sensor_ahtx0,now,is_bh1750_availible,is_bmp280_availible,is_ahtx0_availible)
            requests.post(urlData + ".json", json=data)
    nextLog = lastLog + timedelta(seconds=int(x))
    # except:
    #     print(now)
    #     token = authenticate()
    #     print("err")
    sleep(1)
