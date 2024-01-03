# Sudoku Solving Algorithm
# 19/ENG/108

import sys
import os.path
import time

attemptCount = 0

# increment the number of attempts by 1 each time a potential value is assigned to a cell. Used to check the puzzle difficulty.


def IncreaseAttemptCount():
    global attemptCount
    attemptCount += 1

# get the number of attempts


def getAttempts():
    return attemptCount

# emptySpace class represents an empty cell in the puzzle. Each empty cell has a row number, a column number, a submatrix number, a value and a set of potential values.


class emptySpace:
    def __init__(self, rowIndex, colIndex):
        self.row = rowIndex
        self.col = colIndex
        self.subMatrix = findSubmatrixNo(rowIndex, colIndex)
        self.value = '0'
        self.potentialVals = set()

    def setPotentialVals(self, potentialVals):
        self.potentialVals = potentialVals

    def setValue(self, value):
        self.value = value

    # compare the number of potential values of two empty cells - for sorting
    def __lt__(self, other):
        if len(self.potentialVals) < len(other.potentialVals):
            return True


def sudokuSolver(puzzle):
    print('------Sudoku Solver------')
    # print("Validating parameters...")
    # validateParameters(parameters)
    # print("Loading puzzle...")
    # print("puzzle", puzzle)
    loadedPuzzle = loadPuzzle(puzzle)
    # print("Finding available values...")
    availableVals = findAvailbleVals(loadedPuzzle)
    puzzleMatrix = createSudokuMatrix(loadedPuzzle)
    # print("puzzleMatrix: " + str(puzzleMatrix))
    rowValSets = createRowValSets(puzzleMatrix)
    colValSets = createColValSets(puzzleMatrix)
    subMatrixSets = createSubMatrixSets(puzzleMatrix)
    emptyCells = createEmptyCells(puzzleMatrix)

    # print sudoku puzzle
    print('___Sudoku Puzzle___')
    printSudoku(puzzleMatrix)

    # record the start time
    startTime = time.time()

    # solve the puzzle
    if puzzleIsSolved(emptyCells, rowValSets, colValSets, subMatrixSets, availableVals):
        # record the end time
        endTime = time.time()
        timeTaken = endTime - startTime
        print('Sudoku solved!')
        noOfAttempts = getAttempts()
        print('Number of attempts: ' + str(noOfAttempts))
        print('Time taken to solve: ' + str(timeTaken) + ' seconds')
        solvedSudoku = puzzleMatrix

        # empty cells have solved values for initial empty cells in the puzzle
        for emptyCell in emptyCells:
            # fill the solved values into the puzzle matrix
            solvedSudoku[emptyCell.row][emptyCell.col] = emptyCell.value
        print('___Solved Sudoku___')
        printSudoku(solvedSudoku)
        print(solvedSudoku)
        return solvedSudoku
        # write the solved puzzle to output file
        # writeSolutionToFile(parameters, solvedSudoku, isSolved=True)
    else:
        # writeSolutionToFile(parameters, solvedSudoku=None, isSolved=False)
        print('No solution!')
        print(solvedSudoku)
        return None


# check whether the input parameters are valid. If the number of parameters is not 2, or the input file is not a .txt file, or the input file does not exist, the program will exit with an error message.
# arguments: input arguments


# def validateParameters(arguments):
#     global inputFile
#     # validate number of arguments
#     if len(arguments) != 2:
#         sys.exit('Requires exactly one argument (input.txt)')

#     inputFile = arguments[1]

#     # validate argument type
#     if not inputFile.endswith('.txt'):
#         sys.exit('input file must be a .txt file')

#     # check if input file exists
#     if not os.path.isfile(inputFile):
#         sys.exit('input file not found: ' + inputFile)

# load puzzle from input file. If the format of sudoku is not i 9x9 or 16x16, the program will exit with an error message. If the format is 16`x16, the program will set isHexadoku to True, otherwise, set isHexadoku to False.
# returns a list of strings, each string represents a line in the input file
# filename: input file name


def loadPuzzle(puzzleLines):
    global isHexadoku
    # inputFile = open(filename, 'r')
    # remove trailing whitespace from each line
    # puzzleLines = [line.rstrip() for line in puzzle]
    # inputFile.close()
    print("puzzleLines: " + str(puzzleLines))
    print(len(puzzleLines))
    # validate the format of sudoku
    if len(puzzleLines) != 16 and len(puzzleLines) != 9:
        sys.exit('The input file has invalid format. Need 9 or 16 lines. But found ' +
                 str(len(puzzleLines)) + ' lines.')

    if len(puzzleLines) == 16:
        isHexadoku = True
    else:
        isHexadoku = False

    for i, line in enumerate(puzzleLines):
        # split values based on whitespace
        values = line.split()
        if isHexadoku:
            if len(values) != 16:
                sys.exit('The input file has invalid format. Need 16 characters per line. But found ' + str(
                    len(values)) + ' characters on line ' + str(i + 1) + '.')
        else:
            if len(values) != 9:
                sys.exit('The input file has invalid format. Need 9 characters per line. But found ' + str(
                    len(values)) + ' characters on line ' + str(i + 1) + '.')
    return puzzleLines

# find all available values in the puzzle. If the puzzle is 9x9, the available values are 1 to 9. If the puzzle is 16x16, the available values are 0 to 16. If the puzzle contains any other values, the program will exit with an error message.
# returns a set of available values
# lines: a list of strings, each string represents a line in the input file


def findAvailbleVals(lines):
    availableVals = set()
    for line in lines:
        # split values based on whitespace
        values = line.split()
        for val in values:
            # print("val: " + val)
            if val != '0':
                # add val to availableVals if cell is not empty and val is not already in availableVals
                availableVals.add(val)
    if isHexadoku and len(availableVals) != 16:
        sys.exit("Hexadoku puzzle should have 16 unique symbols, found " +
                 str(len(availableVals)) + ": " + ', '.join(sorted(availableVals)))
    elif not isHexadoku and len(availableVals) != 9:
        sys.exit("Sudoku puzzle should have 9 unique symbols, found " +
                 str(len(availableVals)) + ": " + ', '.join(sorted(availableVals)))
    # print("Available values: " + ', '.join(sorted(availableVals)))
    return availableVals

# create a 2D puzzle matrix from the list of strings. Each string represents a line in the input file.
# returns a 2D puzzle matrix
# lines: a list of strings, each string represents a line in the input file


def createSudokuMatrix(lines):
    matrix = []
    for line in lines:
        row = []
        # split values based on whitespace
        values = line.split()
        for val in values:
            row.append(val)
        matrix.append(row)
    return matrix

# create a list of sets, each set contains all values in a row. If the puzzle contains any duplicate values in a row, the program will exit with an error message.
# returns a list of sets, each set contains all values in a row
# puzzle: a 2D puzzle matrix


def createRowValSets(puzzle):
    valsInRows = []
    for index, row in enumerate(puzzle):
        valsInRow = set()
        for val in row:
            if val != '0':
                if val in valsInRow:
                    sys.exit("Invalid puzzle: found duplicate value " +
                             val + " in row " + str(index + 1))
                else:
                    valsInRow.add(val)
        valsInRows.append(valsInRow)
    return valsInRows

# create a list of sets, each set contains all values in a column. If the puzzle contains any duplicate values in a column, the program will exit with an error message.
# returns a list of sets, each set contains all values in a column
# puzzle: a 2D puzzle matrix


def createColValSets(puzzle):
    valsInCols = []
    puzzleLength = 16 if isHexadoku else 9

    for col in range(puzzleLength):
        valsInCol = set()
        for row in range(puzzleLength):
            if puzzle[row][col] != '0':
                if puzzle[row][col] in valsInCol:
                    sys.exit('Invalid puzzle: found duplicate value ' +
                             puzzle[row][col] + ' in column ' + str(col + 1))
                else:
                    valsInCol.add(puzzle[row][col])
        valsInCols.append(valsInCol)
    return valsInCols

# create a list of sets, each set contains all values in a submatrix. If the puzzle contains any duplicate values in a submatrix, the program will exit with an error message.
# returns a list of sets, each set contains all values in a submatrix
# puzzle: a 2D puzzle matrix


def createSubMatrixSets(puzzle):
    subMatrixes = []
    puzzleLength = 16 if isHexadoku else 9
    for n in range(puzzleLength):
        # create a set for each submatrix
        subMatrixes.append(set())
    for row in range(puzzleLength):
        for col in range(puzzleLength):
            if puzzle[row][col] != '0':
                subMatrixNo = findSubmatrixNo(row, col)
                if puzzle[row][col] in subMatrixes[subMatrixNo]:
                    sys.exit('Invalid puzzle: found duplicate value ' +
                             puzzle[row][col] + ' in submatrix ' + str(subMatrixNo))
                else:
                    # add value to the set of the submatrix
                    subMatrixes[subMatrixNo].add(puzzle[row][col])
    return subMatrixes

# find the submatrix number of a cell in the puzzle. If the puzzle is 9x9, there are 9 submatrixes, numbered from 0 to 8. If the puzzle is 16x16, there are 16 submatrixes, numbered from 0 to 15.
# returns the submatrix number of a cell
# row: row number of the cell
# col: column number of the cell


def findSubmatrixNo(row, col):
    if isHexadoku:
        if 0 <= row <= 3:
            if 0 <= col <= 3:
                return 0
            elif 4 <= col <= 7:
                return 1
            elif 8 <= col <= 11:
                return 2
            elif 12 <= col <= 15:
                return 3
        elif 4 <= row <= 7:
            if 0 <= col <= 3:
                return 4
            elif 4 <= col <= 7:
                return 5
            elif 8 <= col <= 11:
                return 6
            elif 12 <= col <= 15:
                return 7
        elif 8 <= row <= 11:
            if 0 <= col <= 3:
                return 8
            elif 4 <= col <= 7:
                return 9
            elif 8 <= col <= 11:
                return 10
            elif 12 <= col <= 15:
                return 11
        elif 12 <= row <= 15:
            if 0 <= col <= 3:
                return 12
            elif 4 <= col <= 7:
                return 13
            elif 8 <= col <= 11:
                return 14
            elif 12 <= col <= 15:
                return 15
    else:
        if 0 <= row <= 2:
            if 0 <= col <= 2:
                return 0
            elif 3 <= col <= 5:
                return 1
            elif 6 <= col <= 8:
                return 2
        elif 3 <= row <= 5:
            if 0 <= col <= 2:
                return 3
            elif 3 <= col <= 5:
                return 4
            elif 6 <= col <= 8:
                return 5
        elif 6 <= row <= 8:
            if 0 <= col <= 2:
                return 6
            elif 3 <= col <= 5:
                return 7
            elif 6 <= col <= 8:
                return 8

# create a list of empty cells in the puzzle.
# returns a list of empty cells
# puzzle: a 2D puzzle matrix


def createEmptyCells(puzzle):
    emptyCells = []
    puzzleLength = 16 if isHexadoku else 9
    for row in range(puzzleLength):
        for col in range(puzzleLength):
            if puzzle[row][col] == '0':
                # add empty cell to the list
                emptyCells.append(emptySpace(row, col))
    return emptyCells

# print the sudoku puzzle
# puzzleMatrix: a 2D puzzle matrix


def printSudoku(puzzleMatrix):
    subMatrixLength = 4 if isHexadoku else 3
    for rowIndex, row in enumerate(puzzleMatrix):
        if rowIndex % subMatrixLength == 0 and rowIndex != 0:
            if isHexadoku:
                print('|------------------------------------------------|')
            else:
                print('|-------|-------|-------|')
        print('|', end=' ')
        for colIndex, val in enumerate(row):
            if colIndex % subMatrixLength == 0 and colIndex != 0:
                print('|', end=' ')
            print(val, end=' ')
        print('|')

# Solve the puzzle.
# first check if each empty cell has at least one potential value. If not, the puzzle is not solvable.
# then pops the first empty cell from the list, and assign a potential value to it and check if the puzzle is solved. If not, assign another potential value to it and check again recursivly until the puzzle is solved or all potential values are checked.
# if the puzzle is solved, restore the empty cell to the list for backtracking.
# returns True if the puzzle is solved, otherwise returns False
# emptyCells: a list of empty cells
# rowValSets: a list of sets, each set contains all values in a row
# colValSets: a list of sets, each set contains all values in a column
# subMatrixSets: a list of sets, each set contains all values in a submatrix
# availableVals: a set of available values in the puzzle


def puzzleIsSolved(emptyCells, rowValSets, colValSets, subMatrixSets, availableVals):
    if allCellsHavePotentialVals(emptyCells, rowValSets, colValSets, subMatrixSets, availableVals):
        emptyCell = emptyCells.pop(0)
        for potentialVal in emptyCell.potentialVals:
            # assign potential value to the empty cell
            emptyCell.setValue(potentialVal)
            # increase the number of checks by 1
            IncreaseAttemptCount()
            addToAvailableValsSets(
                emptyCell, rowValSets, colValSets, subMatrixSets)
            if isPuzzleSolved(rowValSets, colValSets, subMatrixSets):
                # restore the empty cell to the list for backtracking
                emptyCells.insert(0, emptyCell)
                return True
            else:
                if emptyCells:
                    # solve the next empty cell
                    if puzzleIsSolved(emptyCells, rowValSets, colValSets, subMatrixSets, availableVals):
                        # restore the empty cell to the list for backtracking
                        emptyCells.insert(0, emptyCell)
                        return True
                    else:
                        # the current potential value is not valid, remove it from the available values sets
                        removeFromAvailableValsSets(emptyCell, rowValSets,
                                                    colValSets, subMatrixSets)
                        emptyCell.setValue('0')
                # all empty cells are considered, the puzzle is not solvable
                else:
                    # the current potential value is not valid, remove it from the available values sets
                    removeFromAvailableValsSets(emptyCell, rowValSets,
                                                colValSets, subMatrixSets)
                    emptyCell.setValue('0')
        # restore the empty cell to the list for backtracking
        emptyCells.insert(0, emptyCell)
        # there are no potential values for at least one empty cell, the puzzle is not solvable
        return False
    # there are no potential values for at least one empty cell, the puzzle is not solvable
    else:
        return False

# find the potential values for each empty cell in the puzzle. Then sort the empty cells by the number of potential values in ascending order.
# returns True if all empty cells have at least one potential value, otherwise returns False
# emptyCells: a list of empty cells
# rowValSets: a list of sets, each set contains all values in a row
# colValSets: a list of sets, each set contains all values in a column
# subMatrixSets: a list of sets, each set contains all values in a submatrix
# availableVals: a set of available values in the puzzle


def allCellsHavePotentialVals(emptyCells, rowValSets, colValSets, subMatrixSets, availableVals):
    for emptyCell in emptyCells:
        # get the existing values in the row, column and submatrix that the empty cell is in
        existingValsInRowColSubMatrix = rowValSets[emptyCell.row] | colValSets[
            emptyCell.col] | subMatrixSets[emptyCell.subMatrix]

        potentialVals = availableVals - existingValsInRowColSubMatrix
        if potentialVals:
            emptyCell.setPotentialVals(potentialVals)
        else:
            return False
    # print("before sort: ")
    # for cell in emptyCells:
    #     print(len(cell.potentialVals))
    emptyCells.sort()
    # print("after sort: ")
    # for cell in emptyCells:
    #     print(len(cell.potentialVals))
    return True

# add the value of an empty cell to the row, column and submatrix sets which contain available values for row, column and submatrix that the empty cell is in.
# emptyCell: an empty cell
# rowValSets: a list of sets, each set contains all values in a row
# colValSets: a list of sets, each set contains all values in a column
# subMatrixSets: a list of sets, each set contains all values in a submatrix


def addToAvailableValsSets(emptyCell, rowValSets, colValSets, subMatrixSets):
    rowValSets[emptyCell.row].add(emptyCell.value)
    colValSets[emptyCell.col].add(emptyCell.value)
    subMatrixSets[emptyCell.subMatrix].add(emptyCell.value)

# check if the puzzle is solved. If all rows, columns and submatrixes contain 16 unique values, the puzzle is solved.
# returns True if the puzzle is solved, otherwise returns False
# rowValSets: a list of sets, each set contains all values in a row
# colValSets: a list of sets, each set contains all values in a column
# subMatrixSets: a list of sets, each set contains all values in a submatrix


def isPuzzleSolved(rowValSets, colValSets, subMatrixSets):
    puzzleLength = 16 if isHexadoku else 9
    # check if all rows, columns and submatrixes contain 16 unique values
    for rowValSet in rowValSets:
        if len(rowValSet) != puzzleLength:
            return False
    for colValSet in colValSets:
        if len(colValSet) != puzzleLength:
            return False
    for subMatrixValSet in subMatrixSets:
        if len(subMatrixValSet) != puzzleLength:
            return False
    return True

# remove the value of an empty cell from the row, column and submatrix sets which contain available values for row, column and submatrix that the empty cell is in.
# emptyCell: an empty cell
# rowValSets: a list of sets, each set contains all values in a row
# colValSets: a list of sets, each set contains all values in a column
# subMatrixSets: a list of sets, each set contains all values in a submatrix


def removeFromAvailableValsSets(emptyCell, rowValSets, colValSets, subMatrixSets):
    rowValSets[emptyCell.row].discard(emptyCell.value)
    colValSets[emptyCell.col].discard(emptyCell.value)
    subMatrixSets[emptyCell.subMatrix].discard(emptyCell.value)

# write the solution to the output file
# parameters: input arguments
# solvedSudoku: a 2D puzzle matrix with solved values
# isSolved: True if the puzzle is solved, otherwise False


def writeSolutionToFile(parameters, solvedSudoku, isSolved):
    outputFile = f"{parameters[1].split('.')[0]}_output.txt"
    with open(outputFile, 'w') as file:
        if isSolved:
            for row in solvedSudoku:
                file.write(' '.join(map(str, row)) + '\n')
        else:
            file.write('No Solution')
