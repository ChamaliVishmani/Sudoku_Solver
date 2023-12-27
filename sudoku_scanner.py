import cv2 as cv
import numpy as np

from utils import preProcessImg, stackImages, findBiggestContour, reoderPoints, splitImgToBoxes, initializePredectionModel

imgPath = "sudokuImages/1.jpg"
imgHeight = 450
imgWidth = 450
digitsClassModel = initializePredectionModel()

# prepare image
img = cv.imread(imgPath)
img = cv.resize(img, (imgHeight, imgWidth))  # Resize the image
blankImg = np.zeros((imgHeight, imgWidth, 3), np.uint8)  # Create a blank image
imgThreshold = preProcessImg(img)  # Preprocess the image

# find contours
imgContours = img.copy()  # Copy the image - all contours
imgBigContours = img.copy()  # Copy the image - biggest contour
contours, hierarchy = cv.findContours(
    imgThreshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # Find all contours - external
cv.drawContours(imgContours, contours, -1, (0, 255, 0), 3)  # Draw all contours

# find biggest contour
biggestContourPoints, maxArea = findBiggestContour(contours)
print("biggest contour", biggestContourPoints)

if biggestContourPoints.size != 0:
    biggestContourPoints = reoderPoints(biggestContourPoints)
    print("reordered contour", biggestContourPoints)

    # draw biggest contour
    cv.drawContours(imgBigContours, biggestContourPoints, -1, (0, 0, 255), 25)

    # get sudoku using warp perspective
    sourcePoints = np.float32(biggestContourPoints)
    destinationPoints = np.float32(
        [[0, 0], [imgWidth, 0], [0, imgHeight], [imgWidth, imgHeight]])
    transformMatrix = cv.getPerspectiveTransform(
        sourcePoints, destinationPoints)
    imgWarpColored = cv.warpPerspective(
        img, transformMatrix, (imgWidth, imgHeight))
    imgWarpColored = cv.cvtColor(imgWarpColored, cv.COLOR_BGR2GRAY)

    # split image and find digits
    imgSolvedDigits = blankImg.copy()
    boxes = splitImgToBoxes(imgWarpColored)
    # print(len(boxes))
    # cv.imshow("Sample Box", boxes[0])


# stack images
imgArray = ([img, imgThreshold, imgContours],
            [imgBigContours, imgWarpColored, blankImg])
stackedImg = stackImages(imgArray, 0.8)
cv.imshow("Stacked Images", stackedImg)
cv.waitKey(0)
