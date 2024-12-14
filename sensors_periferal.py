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

