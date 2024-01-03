import cv2 as cv
import numpy as np
import sys

from utils import askUserForPuzzleType, preProcessImg, stackImages, findBiggestContour, reoderPoints, splitImgToBoxes, initializePredectionModel, predictDigits, displayDigitsOnImg, drawSudokuGrid, validateParameters

import sudoku_solver as sudokuSolver

imgHeight_9by9 = 450
imgWidth_9by9 = 450
imgHeight_16by16 = 800
imgWidth_16by16 = 800
digitsClassModel = initializePredectionModel()
isHexadoku = False


def main(parameters):
    imgPath = validateParameters(parameters)

    # Get user input for puzzle type
    isHexadoku = askUserForPuzzleType()

    # prepare image
    img = cv.imread(imgPath)
    imgHeight = imgHeight_16by16 if isHexadoku else imgHeight_9by9
    imgWidth = imgWidth_16by16 if isHexadoku else imgWidth_9by9
    img = cv.resize(img, (imgHeight, imgWidth))  # Resize the image
    blankImg = np.zeros((imgHeight, imgWidth, 3),
                        np.uint8)  # Create a blank image
    imgThreshold = preProcessImg(img)  # Preprocess the image

    # find contours
    imgContours = img.copy()  # Copy the image - all contours
    imgBigContours = img.copy()  # Copy the image - biggest contour
    contours, hierarchy = cv.findContours(
        imgThreshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # Find all contours - external
    cv.drawContours(imgContours, contours, -1,
                    (0, 255, 0), 3)  # Draw all contours

    # find biggest contour
    biggestContourPoints, maxArea = findBiggestContour(contours)

    if biggestContourPoints.size != 0:
        biggestContourPoints = reoderPoints(biggestContourPoints)

        # draw biggest contour
        cv.drawContours(
            imgBigContours, biggestContourPoints, -1, (0, 0, 255), 25)

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
        boxes = splitImgToBoxes(imgWarpColored, isHexadoku)
        # cv.imshow("Sample Box", boxes[0])

        print("----predicting digits----")
        detectedDigits = predictDigits(boxes, digitsClassModel)
        imgDetectedDigits = blankImg.copy()
        imgDetectedDigits = displayDigitsOnImg(
            imgDetectedDigits, detectedDigits, color=(255, 0, 255), isHexadoku=isHexadoku)

        detectedDigits = np.array(detectedDigits)
        # print("detectedDigits :", detectedDigits)
        posArray = np.where(detectedDigits > 0, 0, 1)

        puzzleLen = 16 if isHexadoku else 9
        puzzleLines = [' '.join(map(str, detectedDigits[i:i+puzzleLen]))
                       for i in range(0, len(detectedDigits), puzzleLen)]

        # save puzzle in text file
        with open('puzzle.txt', 'w') as file:
            for line in puzzleLines:
                file.write(line + '\n')

        imgArray = ([img, imgThreshold, imgContours],
                    [imgBigContours, imgWarpColored, imgDetectedDigits])
        stackedImg = stackImages(imgArray, 0.4)
        cv.imshow("Stacked Images Before Solving", stackedImg)
        cv.waitKey(0)

        # print(puzzleLines)
        print("----solving sudoku----")
        try:
            solvedSudoku = sudokuSolver.sudokuSolver(puzzleLines)
        except:
            sys.exit("Error in solving sudoku")

        # print("solved", solvedSudoku)

        # convert to flat list
        flatList = []
        for sublist in solvedSudoku:
            for item in sublist:
                flatList.append(int(item))

        # display solved digits
        # make puzzle values 0
        solvedDigits = flatList * posArray
        imgSolvedDigits = displayDigitsOnImg(
            imgSolvedDigits, solvedDigits, color=(0, 255, 0), isHexadoku=isHexadoku)

        # overlay solved digits onto original image
        bigContourPts = np.float32(biggestContourPoints)
        puzzleConers = np.float32(
            [[0, 0], [imgWidth, 0], [0, imgHeight], [imgWidth, imgHeight]])
        # create perspective transform matrix
        transformMatrix = cv.getPerspectiveTransform(
            puzzleConers, bigContourPts)

        imgInvWarpColored = img.copy()
        imgInvWarpColored = cv.warpPerspective(
            imgSolvedDigits, transformMatrix, (imgWidth, imgHeight))

        solutionBlendedImg = cv.addWeighted(imgInvWarpColored, 1, img, 0.5, 1)

        imgDetectedDigits = drawSudokuGrid(imgDetectedDigits, isHexadoku)
        imgSolvedDigits = drawSudokuGrid(imgSolvedDigits, isHexadoku)

        # stack images
        imgArray = ([img, imgThreshold, imgContours, imgWarpColored],
                    [imgDetectedDigits, imgSolvedDigits, imgInvWarpColored, solutionBlendedImg])
        scaleSize = 0.45 if isHexadoku else 0.5
        stackedImg = stackImages(imgArray, scaleSize)
        cv.imshow("Stacked Images", stackedImg)

    else:
        print("No sudoku found")

    cv.waitKey(0)


if __name__ == "__main__":
    main(sys.argv)
