import adafruit_bh1750
import adafruit_bmp280
import adafruit_ahtx0

def initBH1750(i2c):
    try:
        sensor = adafruit_bh1750.BH1750(i2c)
        print("BH1750 detected and initialized!")
        return sensor, True
    except ValueError as e:
        print("BH1750 not detected. Check wiring and address.")
        return None, False

def initBMP280(i2c):
    try:
        sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        print("BMP280 detected and initialized!")
        return sensor, True
    except ValueError as e:
        print("BMP280 not detected. Check wiring and address.")
        return None, False

def initAHTx0(i2c):
    try:
        sensor = adafruit_ahtx0.AHTx0(i2c)
        print("AHTx0 detected and initialized!")
        return sensor, True
    except ValueError as e:
        print("AHTx0 not detected. Check wiring and address.")
        return None, False

def getDataValues(chan,chan1,chan2,chan3,sensor_bh1750,sensor_bmp280,sensor_ahtx0,now,is_bh1750_availible,is_bmp280_availible,is_ahtx0_availible):
    
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
    return data

def getBMP280(sensor_bmp280,is_bmp280_availible):
    pressure = 0.0
    altitude = 0.0
    temperature2 = 0.0
    if(is_bmp280_availible):
        # Sensor press/bar   
        temperature2 = round(sensor_bmp280.temperature, 2)
        pressure = round(sensor_bmp280.pressure, 2)
        altitude = round(sensor_bmp280.altitude, 2)
    return temperature2