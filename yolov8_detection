from ultralytics import YOLO
import cv2
import numpy

#label the important stuff
def labelMaker(x,y,x1,y1,name,r,g,b):
    cv2.rectangle(img, (int(x), int(y)), (int(x1), int(y1)), (r, g, b), 2)
    (w, h), _ = cv2.getTextSize(
        name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(img, (int(x-1), int(y) - 25), (int(x+w+2), int(y)), (r, g, b), -1)
    cv2.putText(img, name, (int(x), int(y) - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    print(name)

# Load the model
model = YOLO('bestL.pt')
# Perform inference
output = model.predict(source='campick4.jpg', conf=0.5, save=False)
outPlot = output[0].plot()
cv2.imshow("result", outPlot)
cv2.waitKey()
img = cv2.imread("campick4.jpg")
print(output)
# # Print the result
print(output[0].numpy())
print(output[0].boxes.xyxy)

pocetSlabych = 0
pocetPoskodenych = 0
pocetChorych = 0
pocetMrtvych = 0

loop = 0
for mark in output[0].boxes.cls:
    x = output[0].boxes.xyxy[loop, 0].numpy()
    y = output[0].boxes.xyxy[loop, 1].numpy()
    x1 = output[0].boxes.xyxy[loop, 2].numpy()
    y1 = output[0].boxes.xyxy[loop, 3].numpy()
    if mark == 1:
        pocetSlabych += 1
        labelMaker(x,y,x1,y1,'Slabe',204,0,255)
    if mark == 2:
        pocetPoskodenych += 1
        labelMaker(x, y, x1, y1, 'Poskodene', 0, 102, 255)
    if mark == 3:
        pocetChorych += 1
        labelMaker(x, y, x1, y1, 'Chore', 255, 153, 0)
    if mark == 4:
        pocetMrtvych += 1
        labelMaker(x, y, x1, y1, 'Mrtve', 128, 0, 0)
    loop += 1
print("Pocet Slabých: " + str(pocetSlabych) + "\nPocet Poškodených: " + str(pocetPoskodenych) + "\nPocet Slabých: " + str(pocetChorych) + "\nPocet Mŕtvych: " + str(pocetMrtvych))
cv2.imshow("result2", img)
cv2.waitKey()

