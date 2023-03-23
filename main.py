from picamera import PiCamera
from datetime import datetime
from time import sleep
import requests
import os
import pyrebase
import board
import busio
import adafruit_bmp280
import adafruit_bh1750
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime, timedelta

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)
ads.gain = 1
# Lux sensor
sensor = adafruit_bh1750.BH1750(i2c)
# temp/bar sensor
sensor2 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

urlData = "https://greenhouseapp-a928f-default-rtdb.firebaseio.com/data"
url2 = "https://greenhouseapp-a928f-default-rtdb.firebaseio.com/settings"
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

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()
camera = PiCamera()
timer = 0
now = datetime.now()
nextLog = now
lastLog = now


def authenticate():
    response = auth.sign_in_with_email_and_password("piunit@unit.sk", "12345678")
    token = response['idToken']
    print(token)
    return token;


def getDataValues(chan, chan1, chan2, chan3, sensor, sensor2, now):
    #     Sensor svetla
    lux = round(sensor.lux, 2)
    #     Sensor press/bar
    temperature = round(sensor2.temperature, 2)
    pressure = round(sensor2.pressure, 2)
    altitude = round(sensor2.altitude, 2)

    #     dole pravý
    water = int(100 - (100 / 1.366 * (chan.voltage - 0.806)))
    #     hore lavý
    water2 = int(100 - (100 / 1.358 * (chan1.voltage - 0.796)))
    #     horny pravý
    water3 = int(100 - (100 / 1.348 * (chan2.voltage - 0.844)))
    #     dolny lavý
    water4 = int(100 - (100 / 1.398 * (chan3.voltage - 0.768)))
    data = {"date": str(now), "water": water, "water2": water2, "water3": water3, "water4": water4, "lux": lux,
            "temperature": temperature, "pressure": pressure, "altitude": altitude}
    return data;


def storePicture(x, now):
    filename1 = "cam-" + now.strftime("%Y-%m-%d_%H.%M.%S.jpg")
    filename = "/home/pi/Desktop/" + filename1
    camera.start_preview()
    sleep(5)
    camera.capture(filename)
    camera.stop_preview()
    print(filename + " saved")
    storage.child(filename1).put(filename)
    print("Image sent")
    os.remove(filename)
    print("File Removed")
    return x;


url2 = "https://greenhouseapp-a928f-default-rtdb.firebaseio.com/settings"
token = authenticate()

while True:

    try:
        now = datetime.now()
        begin = now.replace(hour=8, minute=0, second=0, microsecond=0)
        stop = now.replace(hour=22, minute=0, second=0, microsecond=0)
        r = requests.get(url2 + ".json?auth=" + token)
        data = r.json()
        x = data['sampling_time']
        print(x)
        if now < stop and now > begin:
            if now >= nextLog:
                lastLog = now
                print(nextLog)
                store = storePicture(x, now)
                data = getDataValues(chan, chan1, chan2, chan3, sensor, sensor2, now)
                requests.post(urlData + ".json", json=data)
        nextLog = lastLog + timedelta(seconds=int(x))




    except:
        print(now)
        token = authenticate()

    sleep(1)