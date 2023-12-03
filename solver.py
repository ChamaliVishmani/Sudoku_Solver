import time

# Sudoku puzzle to be solved
puzzle = [
    [3, 0, 6, 5, 0, 8, 4, 0, 0],
    [5, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 8, 7, 0, 0, 0, 0, 3, 1],
    [0, 0, 3, 0, 1, 0, 0, 8, 0],
    [9, 0, 0, 8, 6, 3, 0, 0, 5],
    [0, 5, 0, 0, 9, 0, 6, 0, 0],
    [1, 3, 0, 0, 0, 0, 2, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 7, 4],
    [0, 0, 5, 2, 0, 6, 3, 0, 0]
]

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

# Print the puzzle


def printPuzzle():
    for i in range(0, 9):
        for j in range(0, 9):
            print(str(puzzle[i][j]), end=" ")
        print()


# Method to check if the inserted element is safe by checking if the element is present in the same row, column or the 3x3 sub matrix
# row: row index
# col: column index
def safeToAddAtPos(row, col):

    num = puzzle[row][col]
    for i in range(0, 9):
        # Check if the element is present in the same row or column other than the current row and column
        if i != col and puzzle[row][i] == num:
            return False
        if i != row and puzzle[i][col] == num:
            return False

    # Check if the element is present in the same 3x3 sub matrix
    rowStart = int(row / 3) * 3
    rowEnd = rowStart + 3

    colStart = int(col / 3) * 3
    colEnd = colStart + 3

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
    for row in range(0, 9):
        for col in range(0, 9):
            # If a number is present in the position
            if puzzle[row][col] > 0:
                if puzzle[row][col] not in elementPositions:
                    # Add the element to the elementPositions dictionary
                    elementPositions[puzzle[row][col]] = []
                # Add the position of the element to the elementPositions dictionary
                elementPositions[puzzle[row][col]].append([row, col])
                if puzzle[row][col] not in countLeft:
                    # Add max count of the element to the countLeft dictionary
                    countLeft[puzzle[row][col]] = 9
                # Reduce the count of the element by 1
                countLeft[puzzle[row][col]] -= 1

    # Add Max count of the elements to the countLeft dictionary for the elements that are not present in the puzzle
    for row in range(1, 10):
        if row not in elementPositions:
            elementPositions[row] = []
        if row not in countLeft:
            countLeft[row] = 9

# Find the possible positions of the elements to be filled
# If row and column of the element is already present in the elementPositions dictionary, then skip the position. If not present and position is empty, then add the position to the possiblePositions dictionary


def findPossiblePositions():
    for element, positions in elementPositions.items():
        if element not in possiblePositions:
            possiblePositions[element] = {}

        possibleRows = list(range(0, 9))
        possibleCols = list(range(0, 9))

        for currentPosition in positions:
            possibleRows.remove(currentPosition[0])
            possibleCols.remove(currentPosition[1])

        if len(possibleRows) == 0 or len(possibleCols) == 0:
            continue

        for r in possibleRows:
            for c in possibleCols:
                if puzzle[r][c] == 0:  # If the position is not filled
                    if r not in possiblePositions[element]:
                        possiblePositions[element][r] = []
                    possiblePositions[element][r].append(c)


if __name__ == "__main__":
    # Record the start time
    startTime = time.time()

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
    solvePuzzle(0, elements, 0, firstElementRows)

    print('Solved Puzzle:')
    printPuzzle()

    # Record the end time
    endTime = time.time()
    print('Time taken to solve: ', endTime - startTime, 'seconds')
