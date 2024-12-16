import board
import busio
import RPi.GPIO as GPIO
from time import sleep

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
    return True


def toggleLight(wantedState):
    servoLight = GPIO.PWM(12,50)
    servoLight.start(0)
    if(wantedState==True):
        servoLight.ChangeDutyCycle(6.6)
        sleep(2)
        lightState = False

    else:
        servoLight.ChangeDutyCycle(5)
        sleep(2)
        lightState = True

    servoLight.ChangeDutyCycle(0)
    sleep(0.5)
    servoLight.stop()
    return lightState

def toggleFan(wantedState,fan,DutyFan):
    if(wantedState == True):
        fan.ChangeDutyCycle(DutyFan)
        return True
    else:
        fan.ChangeDutyCycle(0)
        return False
    
    
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
    return True