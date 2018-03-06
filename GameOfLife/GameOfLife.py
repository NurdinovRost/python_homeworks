import pygame
import random
from pygame.locals import *


class GameOfLife:
    def __init__(self, width = 640, height = 480, cell_size = 10, speed = 10):
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

        #
        self.rects = self.cell_list(randomize=True)

    def draw_grid(self):
        # http://www.pygame.org/docs/ref/draw.html#pygame.draw.line
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                (0, y), (self.width, y))

    def get_neighbours(self, cell):
        """
        Вернуть список соседних клеток для клетки cell.
        Соседними считаются клетки по горизонтали,
        вертикали и диагоналям, то есть во всех
        направлениях.
        """
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 == j):
                    continue
                neighbours.append(((cell[0] + i) % self.cell_height,
                            (cell[1] + j) % self.cell_width))
        return neighbours

    def update_cell_list(self):
        """
        Обновление состояния клеток
        """
        copy_rects = [[0] * self.cell_width for i in range(self.cell_height)]
        for i in range(self.cell_height):
            for j in range(self.cell_width):
                value = 0
                neighbours = self.get_neighbours((i, j))  # находим соседей
                for cell in neighbours:
                    if self.rects[cell[0]][cell[1]] == 1:
                        value += 1   # подсчет живых клеток
                if self.rects[i][j] == 0:
                    copy_rects[i][j] = 0
                    if value == 3:
                        copy_rects[i][j] = 1
                if self.rects[i][j] == 1:
                    copy_rects[i][j] = 1
                    if (value != 2) and (value != 3):
                        copy_rects[i][j] = 0
        self.rects = copy_rects
        return copy_rects

    def draw_cell_list(self, rects):
        """
        Отображение списка клеток 'rects' с закрашиванием их в
        соответствующе цвета
        """
        cell_width = self.width // self.cell_size
        for i in range(self.cell_height):
            for j in range(self.cell_width):
                if rects[i][j] == 0:
                    pygame.draw.rect(self.screen, pygame.Color('white'),
                                     (1 + j * self.cell_size, 1 + i * self.cell_size,
                                     self.cell_size - 1, self.cell_size - 1))
                else:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     (1 + j * self.cell_size, 1 + i * self.cell_size,
                                     self.cell_size - 1, self.cell_size - 1))

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.draw_grid()
            self.draw_cell_list(self.rects)
            self.update_cell_list()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def cell_list(self, randomize=False):
        """
        Создание списка клеток.
        Клетка считается живой, если ее значение равно 1.
        В противном случае клетка считается мертвой, то
        есть ее значение равно 0.
        Если параметр randomize = True, то создается список, где
        каждая клетка может быть равновероятно живой или мертвой.
        """
        if randomize:
            matrix_states = [[0] * self.cell_width for i in range(self.cell_height)]
            for i in range(self.cell_height):
                for j in range(self.cell_width):
                    matrix_states[i][j] = random.randint(0, 1)
            return matrix_states
        else:
            return [[0] * self.cell_width for i in range(self.cell_height)]

if __name__ == '__main__':
    game = GameOfLife(640, 480, 10)
    game.run()
