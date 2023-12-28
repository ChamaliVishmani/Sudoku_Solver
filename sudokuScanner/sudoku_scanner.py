import cv2 as cv
import numpy as np

from utils import preProcessImg, stackImages, findBiggestContour, reoderPoints, splitImgToBoxes, initializePredectionModel, predictDigits, displayDigitsOnImg, drawSudokuGrid

import sudoku_solver_for_scanner as sudokuSolver

imgPath = "../sudokuImages/1.jpg"
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
    print("----predicting digits----")
    detectedDigits = predictDigits(boxes, digitsClassModel)
    print(detectedDigits)
    imgDetectedDigits = blankImg.copy()
    imgDetectedDigits = displayDigitsOnImg(
        imgDetectedDigits, detectedDigits, color=(255, 0, 255))

    detectedDigits = np.array(detectedDigits)
    posArray = np.where(detectedDigits > 0, 0, 1)
    print("posArray :", posArray)

    puzzleLines = [' '.join(map(str, detectedDigits[i:i+9]))
                   for i in range(0, len(detectedDigits), 9)]

    # print(puzzleLines)
    print("----solving sudoku----")
    try:
        solvedSudoku = sudokuSolver.sudokuSolver(puzzleLines)
    except:
        print("Error in solving sudoku")
        pass

    print("solved", solvedSudoku)

    # convert to flat list
    flatList = []
    for sublist in solvedSudoku:
        for item in sublist:
            flatList.append(int(item))

    print("flat", flatList)

    # display solved digits
    # make puzzle values 0
    solvedDigits = flatList * posArray
    imgSolvedDigits = displayDigitsOnImg(
        imgSolvedDigits, solvedDigits, color=(0, 255, 0))

    # overlay solved digits onto original image
    bigContourPts = np.float32(biggestContourPoints)
    puzzleConers = np.float32(
        [[0, 0], [imgWidth, 0], [0, imgHeight], [imgWidth, imgHeight]])
    # create perspective transform matrix
    transformMatrix = cv.getPerspectiveTransform(puzzleConers, bigContourPts)

    imgInvWarpColored = img.copy()
    imgInvWarpColored = cv.warpPerspective(
        imgSolvedDigits, transformMatrix, (imgWidth, imgHeight))

    solutionBlendedImg = cv.addWeighted(imgInvWarpColored, 1, img, 0.5, 1)

    imgDetectedDigits = drawSudokuGrid(imgDetectedDigits)
    imgSolvedDigits = drawSudokuGrid(imgSolvedDigits)

    # stack images
    imgArray = ([img, imgThreshold, imgContours],
                [imgBigContours, imgWarpColored, imgDetectedDigits], [imgSolvedDigits, imgInvWarpColored, solutionBlendedImg])
    stackedImg = stackImages(imgArray, 0.5)
    cv.imshow("Stacked Images", stackedImg)

else:
    print("No sudoku found")

cv.waitKey(0)
