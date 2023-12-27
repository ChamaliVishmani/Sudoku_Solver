import numpy as np
import cv2 as cv
import os
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator    # Data augmentation
from keras.utils import to_categorical    # One hot encoding
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.optimizers import Adam
import pickle

dataPath = "data"
testRatio = 0.2  # 20% of data used for testing
validationRatio = 0.2
imageDimensions = (32, 32, 3)

# model parameters
batchSize = 50
epochsVal = 30

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
        img = cv.resize(img, (imageDimensions[0], imageDimensions[1]))
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
X_train, X_validation, y_train, y_validation = train_test_split(
    X_train, y_train, test_size=validationRatio)

print("Shape of training data: ", X_train.shape)
print("Shape of testing data: ", X_test.shape)
print("Shape of validation data: ", X_validation.shape)

numOfSamplesPerClass = []
# Check if number of samples for each class is balanced
for classNum in range(0, noOfClasses):
    numOfSamplesPerClass.append(len(np.where(y_train == classNum)[0]))
print("Number of samples for each class: ", numOfSamplesPerClass)

# Plot bar graph of number of images for each class
plt.figure(figsize=(10, 5))
plt.bar(range(0, noOfClasses), numOfSamplesPerClass)
plt.title("Number of images for each class")
plt.xlabel("Class ID - Digit")
plt.ylabel("Number of images")
plt.show()


def preProcessingImg(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.equalizeHist(image)  # equalize histogram to improve contrast
    image = image/255  # normalize image 0-1
    return image


X_train = np.array(list(map(preProcessingImg, X_train)))
# img = X_train[30]
# img = cv.resize(img, (300, 300))
# cv.imshow("Preprocessed image", img)
# cv.waitKey(0)

X_test = np.array(list(map(preProcessingImg, X_test)))
X_validation = np.array(list(map(preProcessingImg, X_validation)))

# Add depth to images for CNN
X_train = X_train.reshape(
    X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
X_test = X_test.reshape(
    X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
X_validation = X_validation.reshape(
    X_validation.shape[0], X_validation.shape[1], X_validation.shape[2], 1)

# Data augmentation
dataGenerator = ImageDataGenerator(width_shift_range=0.1,
                                   height_shift_range=0.1,
                                   zoom_range=0.2,
                                   shear_range=0.1,
                                   rotation_range=10)
dataGenerator.fit(X_train)

# One hot encoding
y_train = to_categorical(y_train, noOfClasses)
y_test = to_categorical(y_test, noOfClasses)
y_validation = to_categorical(y_validation, noOfClasses)


def createModel():
    noOfFilters = 60
    sizeOfFilter1 = (5, 5)
    sizeOfFilter2 = (3, 3)
    sizeOfPool = (2, 2)
    noOfNodes = 500

    model = Sequential()

    # add convolutional layer
    model.add((Conv2D(noOfFilters, sizeOfFilter1, input_shape=(
        imageDimensions[0], imageDimensions[1], 1), activation='relu')))
    model.add((Conv2D(noOfFilters, sizeOfFilter1, activation='relu')))
    # add pooling layer
    model.add(MaxPooling2D(pool_size=sizeOfPool))
    # add convolutional layer
    model.add((Conv2D(noOfFilters//2, sizeOfFilter2, activation='relu')))
    model.add((Conv2D(noOfFilters//2, sizeOfFilter2, activation='relu')))
    # add pooling layer
    model.add(MaxPooling2D(pool_size=sizeOfPool))
    # add dropout layer to prevent overfitting
    model.add(Dropout(0.5))
    # add flatten layer
    model.add(Flatten())
    # add dense layer
    model.add(Dense(noOfNodes, activation='relu'))
    # add dropout layer
    model.add(Dropout(0.5))
    # add dense layer
    model.add(Dense(noOfClasses, activation='softmax'))

    model.compile(Adam(lr=0.001), loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


model = createModel()
print("model summary ", model.summary())

stepsPerEpoch = len(X_train)//batchSize
# train model
history = model.fit_generator(dataGenerator.flow(X_train, y_train, batch_size=batchSize),
                              steps_per_epoch=stepsPerEpoch, epochs=epochsVal, validation_data=(X_validation, y_validation), shuffle=1)

# plot accuracy and loss

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('Loss')
plt.xlabel('epoch')

plt.figure(2)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['training', 'validation'])
plt.title('Accuracy')
plt.xlabel('epoch')

plt.show()

# evaluate model
score = model.evaluate(X_test, y_test, verbose=0)
print('Test score: ', score[0])
print('Test accuracy: ', score[1])

# save model
pickleOut = open("model_trained.p", "wb")
pickle.dump(model, pickleOut)
pickleOut.close()
