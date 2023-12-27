import time
import sys

# Dictionary to store the positions of the elements to be filled
# elementPositions = {element : [[row1, col1], [row2, col2]]}
elementPositions = {}

# Dictionary to store the count of the elements to be filled
# countLeft = { element: count }
countLeft = {}

# Dictionary to store the possible positions of the elements to be filled
# possiblePositions = {
# element: { row1: [col1,col2], row2: [col1,col2] }
# }
possiblePositions = {}

puzzleLength = 9  # Default puzzle length 9x9 sudoku
subMatrixLength = 3  # Default sub matrix length 3x3

# Print the puzzle


def printPuzzle():
    for i in range(0, puzzleLength):
        for j in range(0, puzzleLength):
            print(str(puzzle[i][j]), end=" ")
        print()


# Method to check if the inserted element is safe by checking if the element is present in the same row, column or the 3x3 sub matrix
# row: row index
# col: column index
def safeToAddAtPos(row, col):

    num = puzzle[row][col]
    for i in range(0, puzzleLength):
        # Check if the element is present in the same row or column other than the current row and column
        if i != col and puzzle[row][i] == num:
            return False
        if i != row and puzzle[i][col] == num:
            return False

    # Check if the element is present in the same sub matrix
    rowStart = int(row / subMatrixLength) * subMatrixLength
    rowEnd = rowStart + subMatrixLength

    colStart = int(col / subMatrixLength) * subMatrixLength
    colEnd = colStart + subMatrixLength

    for currentRow in range(rowStart, rowEnd):
        for currentCol in range(colStart, colEnd):
            if currentRow != row and currentCol != col and puzzle[currentRow][currentCol] == num:
                return False
    return True

# Recursively fill the puzzle
# Loop through each possible positions of the element in the puzzle matrix and if empty, add element to the position and check if it is safe. If safe, then if more possible rows are present, then recursively call the method with next row and if no more possible rows are present, then if more elements are present, then recursively call the method with next element and if no more elements are present, then return True. If not safe, then backtrack and try next position of the element. If no more positions are present, then return False.
# elementIndex: index of the element to be inserted
# elements: list of elements to be inserted
# rowIndex: index of the row to be inserted
# possibleRows: list of row index where element could be inserted


def solvePuzzle(elementIndex, elements, rowIndex, possibleRows):
    if rowIndex >= len(possibleRows):
        return False

    possibleCols = list(
        possiblePositions[elements[elementIndex]][possibleRows[rowIndex]])
    for col in possibleCols:
        if puzzle[possibleRows[rowIndex]][col] > 0:  # If the position is already filled
            continue
        # Add the element to the position
        puzzle[possibleRows[rowIndex]][col] = elements[elementIndex]
        if safeToAddAtPos(possibleRows[rowIndex], col):
            if rowIndex < len(possibleRows) - 1:
                if solvePuzzle(elementIndex, elements, rowIndex + 1, possibleRows):
                    return True
                else:
                    # Backtrack if the element cannot be inserted in the position
                    puzzle[possibleRows[rowIndex]][col] = 0
                    continue
            else:  # Last row
                if elementIndex < len(elements) - 1:
                    # Next element
                    nextElementRows = list(possiblePositions[
                        elements[elementIndex + 1]].keys())
                    if solvePuzzle(elementIndex + 1, elements, 0, nextElementRows):
                        return True
                    else:
                        # Backtrack
                        puzzle[possibleRows[rowIndex]][col] = 0
                        continue
                return True
        # Backtrack
        puzzle[possibleRows[rowIndex]][col] = 0
    return False


# Record the positions of the elements to be filled and the count of the elements to be filled
def recordPostionsAndCountLeft():
    for row in range(0, puzzleLength):
        for col in range(0, puzzleLength):
            # If a number is present in the position
            if puzzle[row][col] > 0:
                if puzzle[row][col] not in elementPositions:
                    # Add the element to the elementPositions dictionary
                    elementPositions[puzzle[row][col]] = []
                # Add the position of the element to the elementPositions dictionary
                elementPositions[puzzle[row][col]].append([row, col])
                if puzzle[row][col] not in countLeft:
                    # Add max count of the element to the countLeft dictionary
                    countLeft[puzzle[row][col]] = puzzleLength
                # Reduce the count of the element by 1
                countLeft[puzzle[row][col]] -= 1

    # Add Max count of the elements to the countLeft dictionary for the elements that are not present in the puzzle
    for row in range(1, puzzleLength + 1):
        if row not in elementPositions:
            elementPositions[row] = []
        if row not in countLeft:
            countLeft[row] = puzzleLength

# Find the possible positions of the elements to be filled
# If row and column of the element is already present in the elementPositions dictionary, then skip the position. If not present and position is empty, then add the position to the possiblePositions dictionary


def findPossiblePositions():
    for element, positions in elementPositions.items():
        if element not in possiblePositions:
            possiblePositions[element] = {}

        possibleRows = list(range(0, puzzleLength))
        possibleCols = list(range(0, puzzleLength))

        for currentPosition in positions:
            if currentPosition[0] in possibleRows:
                possibleRows.remove(currentPosition[0])
            if currentPosition[1] in possibleCols:
                possibleCols.remove(currentPosition[1])

        if len(possibleRows) == 0 or len(possibleCols) == 0:
            continue

        for r in possibleRows:
            for c in possibleCols:
                if puzzle[r][c] == 0:  # If the position is not filled
                    if r not in possiblePositions[element]:
                        possiblePositions[element][r] = []
                    possiblePositions[element][r].append(c)

# Write the solution to the output file
# outputFile: output file name


def writeSolutionToFile(outputFile, isSolved):
    with open(outputFile, 'w') as file:
        if isSolved:
            for row in puzzle:
                file.write(' '.join(map(str, row)) + '\n')
        else:
            file.write('No Solution')


def isHexadoku():
    # check if length of puzzle is 16 and all rows are of length 16
    return (len(puzzle) == 16 and all(len(row) == 16 for row in puzzle))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('To run the sudoku solver: python sudoku_solver.py <input_file>')
        sys.exit(1)

    # Read the sudoku puzzle from the input file
    inputFile = sys.argv[1]
    try:
        with open(inputFile, 'r') as file:
            # Sudoku puzzle as a 2D array
            puzzle = [[int(num) for num in line.split()]
                      for line in file.readlines()]
    except FileNotFoundError:
        print(f"File '{inputFile}' not found.")
        sys.exit(1)
    except ValueError:
        print(
            "Invalid content in the input file.")
        sys.exit(1)

    # Record the start time
    startTime = time.time()

    if isHexadoku():
        puzzleLength = 16
        subMatrixLength = 4
        print('Hexadoku puzzle')

    printPuzzle()

    recordPostionsAndCountLeft()
    # print('elementPositions', elementPositions)
    # print('countLeft', countLeft)

    # Sort the countLeft dictionary based on the count of the elements for optimization - ascending order
    countLeft = {element: count for element, count in sorted(
        countLeft.items(), key=lambda item: item[1])}
    # print('countLeft sorted', countLeft)

    findPossiblePositions()
    # print('possiblePositions', possiblePositions)

    elements = list(countLeft.keys())
    # print('elements', elements)

    firstElementRows = list(possiblePositions[elements[0]].keys())
    # print('firstElementRows', firstElementRows)
    isSolved = solvePuzzle(0, elements, 0, firstElementRows)

    outputFile = f"{inputFile.split('.')[0]}_output.txt"
    writeSolutionToFile(outputFile, isSolved)

    print(f"Solution written to {outputFile}")

    # Record the end time
    endTime = time.time()
    print('Time taken to solve: ', endTime - startTime, 'seconds')
