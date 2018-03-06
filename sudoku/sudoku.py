import random


def read_sudoku(filename):
    """ Прочитать Судоку из указанного файла """
    digits = [c for c in open(filename).read() if c in '123456789.']
    grid = group(digits, 9)
    return grid


def display(values):
    """Вывод Судоку """
    width = 2
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in range(9):
        print(''.join(values[row][col].center(width) + ('|' if str(col) in '25' else '') for col in range(9)))
        if str(row) in '25':
            print(line)
    print()


def group(values, n):
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов

    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    count = 0
    a = [[0] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            a[i][j] = values[count]
            count += 1
    return a


def get_row(values, pos):
    """ Возвращает все значения для номера строки, указанной в pos
    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    return values[pos[0]]


def get_col(values, pos):
    """ Возвращает все значения для номера столбца, указанного в pos

    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    a = [values[i][pos[1]] for i in range(9)]
    return a

def get_block(values, pos):
    """ Возвращает все значения из квадрата, в который попадает позиция pos """
    start = [0, 0]
    for i in range(2):
        if pos[i] == 0 or pos[i] == 1 or pos[i] == 2:
            start[i] = 0
        else:
            if pos[i] == 3 or pos[i] == 4 or pos[i] == 5:
                start[i] = 3
            else:
                start[i] = 6
    a = [values[i][j] for i in range(start[0], start[0] + 3) for j in range(start[1], start[1] + 3)]
    return a


def find_empty_positions(grid):
    """ Найти первую свободную позицию в пазле
    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    for i in range(len(grid)):
        for j in range(len(grid)):
            if grid[i][j] == '.':
                return (i, j)
    return(-1, -1)


def find_possible_values(grid, pos):
    """ Вернуть все возможные значения для указанной позиции """
    variants = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    return variants - set(get_row(grid, pos)) - set(get_col(grid, pos)) - set(get_block(grid, pos))


def check_solution(solution):
    """ Если решение solution верно, то вернуть True, в противном случае False """
    for i in range(9):
        variants = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
        if len(variants - set(get_row(grid, (i, 0)))) != 0:
            return False

    for i in range(9):
        variants = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
        if len(variants - set(get_col(grid, (i, 0)))) != 0:
            return False
        
    for i in range(3):
        for j in range(3):
            variants = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
            if len(variants - set(get_block(grid, (i, 0)))) != 0:
                return False
    return True


def solve(grid):
    """ Решение пазла, заданного в grid """
    """ Как решать Судоку?
        1. Найти свободную позицию
        2. Найти все возможные значения, которые могут находиться на этой позиции
        3. Для каждого возможного значения:
            3.1. Поместить это значение на эту позицию
            3.2. Продолжить решать оставшуюся часть пазла
    """
    pos = find_empty_positions(grid)
    if pos == (-1, -1):
        return grid
    a = find_possible_values(grid, pos)
    variants = []
    for value in a:
        variants.append(value)
    while len(variants) != 0:
        value = random.choice(variants)
        variants.remove(value)
        grid[pos[0]][pos[1]] = value
        solution = solve(grid)
        if (solution is not None) and (find_empty_positions(solution) == (-1, -1)):
            return solution
    grid[pos[0]][pos[1]] = '.'
    return None


def generate_sudoku(n):
    grid = [['.'] * 9 for i in range(9)]
    sudoku = solve(grid)
    count = 0
    if n > 81:
        n = 81
    while count != (81 - n):
        i = random.randint(0, 8)
        j = random.randint(0, 8)
        if sudoku[i][j] != '.':
            sudoku[i][j] = '.'
            count += 1
    return grid


if __name__ == '__main__':
    for fname in ['puzzle1.txt', 'puzzle2.txt', 'puzzle3.txt']:
        grid = read_sudoku(fname)
        display(grid)
        solution = solve(grid)
        display(solution)
