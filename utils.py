import cv2 as cv
import numpy as np
from tensorflow.keras.models import load_model


def preProcessImg(img):
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert to grayscale
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)  # Add Gaussian blur
    imgThreshold = cv.adaptiveThreshold(
        imgBlur, 255, 1, 1, 11, 2)  # Apply adaptive threshold
    return imgThreshold

# stack images in one window


def stackImages(imgArray, scale):
    rows = len(imgArray)
    cols = len(imgArray[0])
    # check if imgArray[0] is a list
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:  # if imgArray[0] is a list
        for x in range(0, rows):
            for y in range(0, cols):
                # resize the image
                imgArray[x][y] = cv.resize(
                    imgArray[x][y], (0, 0), None, scale, scale)
                # check if the image is grayscale
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv.cvtColor(
                        imgArray[x][y], cv.COLOR_GRAY2BGR)
        # create a blank image
        imgBlank = np.zeros((height, width, 3), np.uint8)
        # create a horizontal stack of images
        hor = [imgBlank]*rows
        # create a vertical stack of images
        hor_con = [imgBlank]*rows
        for x in range(0, rows):
            # horizontal concatenation
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        # vertical concatenation
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:  # if imgArray[0] is not a list
        for x in range(0, rows):
            # resize the image
            imgArray[x] = cv.resize(imgArray[x], (0, 0), None, scale, scale)
            # check if the image is grayscale
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv.cvtColor(imgArray[x], cv.COLOR_GRAY2BGR)
        # horizontal concatenation
        hor = np.hstack(imgArray)
        hor_con = np.concatenate(imgArray)
        # vertical concatenation
        ver = hor
    return ver

# find the biggest contour


def findBiggestContour(contours):
    biggestContour = np.array([])
    maxArea = 0
    for contour in contours:
        area = cv.contourArea(contour)
        if area > 50:  # ignore small contours - noise
            perimeter = cv.arcLength(contour, True)
            # approximate the shape - find the vertices
            approx = cv.approxPolyDP(contour, 0.02*perimeter, True)
            # select the biggest contour with 4 vertices
            if area > maxArea and len(approx) == 4:
                biggestContour = approx
                maxArea = area
    return biggestContour, maxArea

# reorder the points


def reoderPoints(points):
    points = points.reshape((4, 2))  # reshape the array to 4x2 matrix
    orderedPoints = np.zeros((4, 1, 2), np.int32)
    xyAddition = points.sum(1)  # sum of x and y coordinates of all points

    # top-left corner - minimum sum
    orderedPoints[0] = points[np.argmin(xyAddition)]
    # bottom-right corner - maximum sum
    orderedPoints[3] = points[np.argmax(xyAddition)]

    xyDifference = np.diff(points, axis=1)  # difference of x and y coordinates

    # top-right corner - minimum difference
    orderedPoints[1] = points[np.argmin(xyDifference)]
    # bottom-left corner - maximum difference
    orderedPoints[2] = points[np.argmax(xyDifference)]

    return orderedPoints

# split the image into 81 boxes


def splitImgToBoxes(img):
    rows = np.vsplit(img, 9)  # split the image into 9 rows
    boxes = []
    for row in rows:
        cols = np.hsplit(row, 9)  # split each row into 9 columns
        for box in cols:
            boxes.append(box)
    return boxes

# initialize the model


def initializePredectionModel():
    # load the model
    model = load_model('digits_classification/model_trained.h5')
    return model

# get the prediction of each box


def getPrediction(boxes, model):
    result = []
    for image in boxes:
        # prepare the image
        img = np.asarray(image)
        img = img[4:img.shape[0]-4, 4:img.shape[1]-4]  # remove the border
        img = cv.resize(img, (28, 28))
        img = img/255
        img = img.reshape(1, 28, 28, 1)

        # predict
        predictions = model.predict(img)
        classIndex = np.argmax(predictions)
        probabilityValue = np.amax(predictions)

        # check if probability is above threshold
        threshold = 0.8
        if probabilityValue > threshold:
            result.append(classIndex)
        else:
            result.append(0)
    return result
