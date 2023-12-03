import time

# Input matrix
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

# Print the matrix array


def printPuzzle():
    for i in range(0, 9):
        for j in range(0, 9):
            print(str(puzzle[i][j]), end=" ")
        print()


# Method to check if the inserted element is safe
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
# If there is no element in the
# element: index of the element to be inserted
# elements: list of elements to be inserted
# row: index of the row to be inserted
# rows: list of row index where element could be inserted


def solvePuzzle(element, elements, row, rows):
    possibleCols = list(possiblePositions[elements[element]][rows[row]])
    for col in possiblePositions[elements[element]][rows[row]]:
        if puzzle[rows[row]][col] > 0:  # If the position is already filled
            continue
        # Add the element to the position
        puzzle[rows[row]][col] = elements[element]
        if safeToAddAtPos(rows[row], col):
            if row < len(rows) - 1:
                if solvePuzzle(element, elements, row + 1, rows):
                    return True
                else:
                    # Backtrack if the element cannot be inserted in the position
                    puzzle[rows[row]][col] = 0
                    continue
            else:  # Last row
                if element < len(elements) - 1:
                    # Next element
                    nextElementRows = list(possiblePositions[
                        elements[element + 1]].keys())
                    if solvePuzzle(element + 1, elements, 0, nextElementRows):
                        return True
                    else:
                        # Backtrack
                        puzzle[rows[row]][col] = 0
                        continue
                return True
        # Backtrack
        puzzle[rows[row]][col] = 0
    return False


# Fill the pos and rem dictionary. It will be used to build graph
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

    # Fill the elements not present in input matrix. Example: 1 is missing in input matrix
    for row in range(1, 10):
        if row not in elementPositions:
            elementPositions[row] = []
        if row not in countLeft:
            countLeft[row] = 9

# Build the graph


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
    print('firstElementRows', firstElementRows)
    solvePuzzle(0, elements, 0, firstElementRows)

    printPuzzle()

    # Record the end time
    endTime = time.time()
    print('Time taken to solve: ', endTime - startTime, 'seconds')
