import numpy as np
import cv2 as cv
import pickle

width = 640
height = 480
threshold = 0.65  # minimum probability to classify

capture = cv.VideoCapture(0)
capture.set(3, width)
capture.set(4, height)

pickleIn = open("model_trained.p", "rb")
model = pickle.load(pickleIn)


def preProcessingImg(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.equalizeHist(image)  # equalize histogram to improve contrast
    image = image/255  # normalize image 0-1
    return image


while True:
    success, imgCaptured = capture.read()
    img = np.asarray(imgCaptured)
    img = cv.resize(img, (32, 32))
    img = preProcessingImg(img)
    img = img.reshape(1, 32, 32, 1)

    # Predict
    predictions = model.predict(img)
    # print("predictions : ", predictions)
    classIndex = np.argmax(predictions)
    probabilityValue = np.amax(predictions)
    print("Class index : ", classIndex, "Probability : ",
          probabilityValue)

    if probabilityValue > threshold:
        cv.putText(imgCaptured, str(classIndex) + " " + str(probabilityValue),
                   (50, 50), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

    cv.imshow("Captured Image", imgCaptured)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
