# GreenhouseControl
This software is used to detect and control small greenhouse with 4 growing spots for greens
the main folder is the heart of the comunication with database but is not functional with second python script yolov8_detection.py
the second file is using traint CNN (convolutional neural network) with train weights "best.py"

## Output from detection by large model weights
![image](https://github.com/DaverSVK/GreenhouseControl/assets/100283209/f2f515c5-e37a-4fd3-aaac-91d1004513cd)

## Output with just data that we are interested in
![image](https://github.com/DaverSVK/GreenhouseControl/assets/100283209/71758910-fe09-4c0c-94d3-9f5ab29bcf9e)

## Running the script
As it said earlier these two files dont work together for now and are meat to run seperatelly. 
With connected raspberry pi to the greenhouse is ready physicaly for all the tasks but the code supports just recieving data and comunicating with the database.
For the first script (main) you will need tu instal dependencies 
```
$ sudo pip3 install pyrebase
$ sudo pip3 install adafruit-circuitpython-bmp280
$ sudo pip3 install adafruit-circuitpython-bh1750
$ sudo pip3 install adafruit-circuitpython-ads1x15
```
and for converter follow:
https://github.com/adafruit/Adafruit_Python_ADS1x15

Inside the code, if you are planning to use own firebase, you will need to change url adresses and firebase configuration

## Running the detection
For the second file (yolov8 detection) you will need to install two dependencies 
```
$ sudo apt-get install python3-opencv
$ sudo pip3 install ultralitycs
```
for the weights you can use best.pt or use large size model: https://drive.google.com/file/d/1LdEyukCS0CqZ2FG1tri3nHbERxlxsT4a/view?usp=sharing
