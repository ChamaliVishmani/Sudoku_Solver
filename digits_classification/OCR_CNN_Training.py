import numpy as np
import cv2 as cv
import os
from sklearn.model_selection import train_test_split

dataPath = "data"
testRatio = 0.2  # 20% of data used for testing
validationRatio = 0.2

dataList = os.listdir(dataPath)

noOfClasses = len(dataList)
print("Total number of classes detected: ", noOfClasses)

images = []
classNums = []

print("Importing images...")

for imageClass in range(0, noOfClasses):
    imageSetList = os.listdir(dataPath+"/"+str(imageClass))
    for image in imageSetList:
        img = cv.imread(dataPath+"/"+str(imageClass)+"/"+image)
        # current size too large for CNN so resize
        img = cv.resize(img, (32, 32))
        images.append(img)
        classNums.append(imageClass)
    print(imageClass, end=" ")
print(" ")

print("Total number of images: ", len(images))
print("Total number of classes: ", len(classNums))

images = np.array(images)
classNums = np.array(classNums)

print("Shape of images: ", images.shape)

# Split data into training and testing and validation sets
X_train, X_test, y_train, y_test = train_test_split(
    images, classNums, test_size=testRatio)
X_train, X_Validation, y_train, y_validation = train_test_split(
    X_train, y_train, test_size=validationRatio)

print("Shape of training data: ", X_train.shape)
print("Shape of testing data: ", X_test.shape)

print("Shape of validation data: ", X_Validation.shape)
