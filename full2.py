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
import sensors_periferal

# Yolo detection
from ultralytics import YOLO

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)
ads.gain = 1
#Lux sensor
sensor_bh1750, is_bh1750_availible = sensors_periferal.initBH1750(i2c)

#temp/bar sensor
sensor_bmp280, is_bmp280_availible = sensors_periferal.initBMP280(i2c)

#temp/bar sensor
sensor_ahtx0, is_ahtx0_availible = sensors_periferal.initAHTx0(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

#----light--------
GPIO.setmode(GPIO.BCM)
GPIO.setup(12,GPIO.OUT)
servoLight = GPIO.PWM(12,50)
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

def authenticate():
    response = auth.sign_in_with_email_and_password("piunit@unit.sk","12345678")
    token = response['idToken']
    print(token)
    return token;

def getDataValues(chan,chan1,chan2,chan3,sensor_bh1750,sensor_bmp280,sensor_ahtx0,now):
    
    lux = 0.0
    temperature = 0.0
    pressure = 0.0
    altitude = 0.0
    temperature2 = 0.0
    humidity = 0.0
    
    if(is_bh1750_availible):
        # Sensor svetla   
        lux = round(sensor_bh1750.lux, 2)
    if(is_bmp280_availible):
        # Sensor press/bar   
        temperature = round(sensor_bmp280.temperature, 2)
        pressure = round(sensor_bmp280.pressure, 2)
        altitude = round(sensor_bmp280.altitude, 2)
    if(is_ahtx0_availible):
        # Sensor TEMP up
        temperature2 = round(sensor_ahtx0.temperature, 2)
        humidity = round(sensor_ahtx0.relative_humidity, 2)

    # dole pravý
    water = int(100-(100/1.366*(chan.voltage-0.806)))
    # hore lavý
    water2 = int(100-(100/1.358*(chan1.voltage-0.796)))
    # horny pravý
    water3 = int(100-(100/1.348*(chan2.voltage-0.844)))
    # dolny lavý
    water4 = int(100-(100/1.398*(chan3.voltage-0.768)))
    data={"date": str(now),"water": water, "water2": water2, "water3": water3, "water4": water4, "lux": lux, "temperature": temperature,"temperature2": temperature2, "pressure": pressure,"humidity": humidity, "altitude": altitude}
    return data;

def startWatering(watering):
    if(int(watering) > 0):
        print("Watering")
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.HIGH)
        sleep(2)
        GPIO.output(6, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        sleep(5)
        print("pump off")
    return True;

def toggleLight(wantedState):
    servoLight = GPIO.PWM(12,50)
    servoLight.start(0)
    if(wantedState==True):
        servoLight.ChangeDutyCycle(6.6)
        sleep(2)
        lightState = False;

    else:
        servoLight.ChangeDutyCycle(5)
        sleep(2)
        lightState = True;

    servoLight.ChangeDutyCycle(0)
    sleep(0.5)
    servoLight.stop()
    return lightState;

def toggleFan(wantedState):
    if(wantedState == True):
        fan.ChangeDutyCycle(40)
        fanStateChange = True
    else:
        fan.ChangeDutyCycle(0)
        fanStateChange = False
    return True

def toggleHeating(tempSetpoint,sensor_bmp280):
    tempCurrent = round(sensor_bmp280.temperature, 2)
    print(tempCurrent)
    if(tempCurrent > float(tempSetpoint)+2):
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)
        print("heating off")
    if (tempCurrent < float(tempSetpoint)-2):
        GPIO.output(19, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        print("heating on")
    return True;
#___________________________________________________
    
    
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
    return x;

url2="https://greenhouseapp-a928f-default-rtdb.firebaseio.com/settings"
token =authenticate()

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
        toggleFan(True)
    if int(fanSett) == 0:
        toggleFan(False)

    if now > stop and lightState == True:
        lightState = toggleLight(True)
    if now < stop and now > begin and lightState == False:
        lightState = toggleLight(False)
    toggleHeating(temp,sensor_bmp280)
    startWatering(watering)
    print(x)
    if now < stop and now > begin:
        if now >= nextLog:
            lastLog = now
            print(nextLog)
            store = storePicture(x,now)
            data = getDataValues(chan,chan1,chan2,chan3,sensor_bh1750,sensor_bmp280,sensor_ahtx0,now)
            requests.post(urlData + ".json", json=data)
    nextLog = lastLog + timedelta(seconds=int(x))
    # except:
    #     print(now)
    #     token = authenticate()
    #     print("err")
    sleep(1)
