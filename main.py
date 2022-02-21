import random

import pygame
import time

"""make a blank 800x600 window with a grid of squares 15x7"""

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WIDTH = 900
HEIGHT = 420
GREEN = (0, 255, 0)

BIT_DIRTY = (232, 228, 201)
MID_DIRTY = (162, 129, 82)
DIRTY = (119, 83, 39)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("INTELIGENCIA ARTIFICIAL")


class Spot:
    def __init__(self, row, col, width, height, total_rows, total_cols, dirtiness):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.height = height
        self.total_cols = total_cols
        self.dirtiness = dirtiness

    def is_clean(self):
        return self.color == WHITE

    def is_dirty(self):
        if 0 <= self.dirtiness <= 0.3:
            return self.color == BIT_DIRTY
        elif 0.3 < self.dirtiness <= 0.6:
            return self.color == MID_DIRTY
        elif 0.6 < self.dirtiness <= 1:
            return self.color == DIRTY

    def make_dirty(self):
        if 0 <= self.dirtiness <= 0.3:
            self.color = BIT_DIRTY
        elif 0.3 < self.dirtiness <= 0.6:
            self.color = MID_DIRTY
        elif 0.6 < self.dirtiness <= 1:
            self.color = DIRTY

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == BLUE

    def reset(self):
        return self.color == WHITE

    def make_start(self):
        self.color = BLUE
        self.dirtiness = 0

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = GREEN

    def make_reset(self):
        self.color = WHITE

    def clean(self):
        self.dirtiness = 0

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_cols - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def make_grid(rows, col, width, height):
    grid = []
    gap = width // col
    gap2 = height // rows
    for i in range(col):
        grid.append([])
        for j in range(rows):
            value = random.uniform(0, 1)
            spot = Spot(i, j, gap, gap2, col, rows, value)
            spot.make_dirty()
            grid[i].append(spot)
    return grid


def draw_grid(win, rows, col, height, width):
    gap = width // rows
    gap2 = height // col
    for i in range(rows):
        pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, height))
        for j in range(col):
            pygame.draw.line(win, BLACK, (0, j * gap2), (width, j * gap2))


def draw(win, grid, rows, col, width, height):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, col, height, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, col, width, height):
    gap = width // col
    gap2 = height // rows
    y, x = pos
    row = y // gap
    col = x // gap2
    return row, col


# (1,1)
# [right, left, down, up]
# for (1,1) -> [(2,1), (0,1), (1,2), (1,0)]
# [0, 1, 2, 3]
def sol(grid, path):
    for row in grid:
        for spot in row:
            if spot.is_start():
                temp = []
                for neighbor in spot.neighbors:
                    temp.append(neighbor.dirtiness)
                    max_dirt = max(temp)
                    for values in spot.neighbors:
                        if values.dirtiness == max_dirt:
                            path.append(values)
    return path


def main(win, width, height):
    ROWS = 7
    COLS = 15
    grid = make_grid(ROWS, COLS, width, height)
    run = True
    roomba = None
    started = False
    path = []

    cont = -1

    while run:
        draw(win, grid, COLS, ROWS, width, height)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, COLS, width, height)

                spot = grid[row][col]

                if not roomba:
                    roomba = spot
                    spot.make_start()

                elif not spot.is_start():
                    spot.clean()
                    spot.make_barrier()


            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, COLS, width, height)
                spot = grid[row][col]
                spot.make_reset()
                spot.clean()
                if spot == roomba:
                    roomba = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and roomba and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)


    pygame.quit()


if __name__ == '__main__':
    main(WIN, WIDTH, HEIGHT)
