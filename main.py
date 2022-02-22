import random
from button import button
import pygame
from queue import PriorityQueue
import time

"""make a blank 800x600 window with a grid of squares 15x7"""
pygame.init()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
WIDTH = 900
HEIGHT = 420

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

    def is_open(self):
        return self.color == GREEN

    def is_close(self):
        return self.color == RED

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == BLUE

    def is_end(self):
        return self.color == TURQUOISE

    def make_open(self):
        self.color = GREEN

    def make_close(self):
        self.color = RED

    def make_start(self):
        self.color = BLUE
        self.dirtiness = 0

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def reset(self):
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


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    costo = 0
    while current in came_from:
        current = came_from[current]
        current.make_path()
        costo += 1
        draw()
    print("El costo total del camino es: ", costo)


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_close()

    return False


def make_grid_m(rows, col, width, height):
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


def make_grid(rows, col, width, height):
    grid = []
    gap = width // col
    gap2 = height // rows
    for i in range(col):
        grid.append([])
        for j in range(rows):
            value = random.uniform(0, 1)
            spot = Spot(i, j, gap, gap2, col, rows, value)
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
    clock = pygame.time.Clock()
    clock.tick(15)
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


background = pygame.image.load("background.jpg")
secuencial_button = button((255, 255, 255), 550, 120, 200, 50, "Secuencial")
random_button = button((255, 255, 255), 550, 220, 200, 50, "Aleatorio")
cool_algo = button((255, 255, 255), 550, 320, 200, 50, "Dijkstra")


def draw_menu_buttons(win):
    font = pygame.font.SysFont("franklingothicmedium", 30)
    text = font.render("INTELIGENCIA ARTIFICIAL", 1, (255, 255, 255))
    win.blit(text, (487, 50))
    secuencial_button.draw(win, (255, 255, 255))
    random_button.draw(win, (255, 255, 255))
    cool_algo.draw(win, (255, 255, 255))
    pygame.display.update()


def main(win, width, height):
    ROWS = 7
    COLS = 15
    grid = make_grid_m(ROWS, COLS, width, height)
    started = False
    secuencial = False
    aleatorio = False
    roomba = None
    end = None
    djikstra = False
    clock = pygame.time.Clock()

    start = None
    path = []

    cont = -1
    whole = True
    menu = True
    while whole:
        while menu:
            win.blit(background, (0, 0))
            draw_menu_buttons(win)
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    secuencial = False
                    menu = False
                    whole = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if secuencial_button.isOver(pos):
                        menu = False
                        secuencial = True
                        grid = make_grid_m(ROWS, COLS, width, height)
                        roomba = None
                    if random_button.isOver(pos):
                        menu = False
                        aleatorio = True
                        grid = make_grid_m(ROWS, COLS, width, height)
                        roomba = None

                    if cool_algo.isOver(pos):
                        menu = False
                        djikstra = True
                        aleatorio = False
                        grid = make_grid(ROWS, COLS, width, height)

            pygame.display.update()

        while secuencial:
            draw(win, grid, COLS, ROWS, width, height)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    secuencial = False
                    whole = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, COLS, width, height)
                    roomba = grid[row][col]
                    if not started:
                        roomba = grid[0][0]
                        roomba.make_start()
                        roomba.clean()
                    else:
                        continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and roomba and not started:

                        started = True
                        for i in range(COLS):
                            a = i

                            for j in range(ROWS):
                                b = j + 1
                                if b == 7:
                                    b = 6


                                else:

                                    draw(win, grid, COLS, ROWS, width, height)
                                    grid[i][j].reset()
                                    grid[i][j].clean()
                                    grid[a][b].make_start()
                                if b == 6 and a <= 14:
                                    grid[a][b].reset()
                                if b == 6 and a == 14:
                                    grid[a][b].make_start()
                    if event.key == pygame.K_b:
                        secuencial = False
                        menu = True
                        started = False
            pygame.display.update()

        while aleatorio:
            draw(win, grid, COLS, ROWS, width, height)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    secuencial = False
                    whole = False
                    aleatorio = False

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
                    spot.reset()
                    spot.clean()
                    if spot == roomba:
                        roomba = None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and roomba and not started:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbors(grid)
                        equisde = True
                        aux_cont = 0

                        while equisde:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    secuencial = False
                                    whole = False
                                    equisde = False
                                    aleatorio = False
                                if event.type == pygame.KEYDOWN:

                                    if event.key == pygame.K_b:
                                        secuencial = False
                                        aleatorio = False
                                        menu = True
                                        equisde = False

                                if started:
                                    continue
                            if roomba.is_start():
                                temp = []
                                for neighbor in roomba.neighbors:
                                    temp.append(neighbor.dirtiness)
                                max_dirt = max(temp)
                                if max_dirt == 0:
                                    aux_cont += 1
                                if aux_cont >= 4:
                                    trigger = 1
                                    for row in grid:
                                        if trigger == 0:
                                            break
                                        for spot in row:
                                            if aux_cont >= 4:
                                                if spot.dirtiness > 0:
                                                    roomba.clean()
                                                    roomba.reset()
                                                    roomba = spot
                                                    roomba.make_start()
                                                    draw(win, grid, COLS, ROWS, width, height)
                                                    aux_cont = 0

                                            else:
                                                trigger = 0
                                                break

                                else:
                                    for values in roomba.neighbors:
                                        if values.dirtiness == max_dirt:
                                            roomba.reset()
                                            roomba.clean()
                                            roomba = values
                                            roomba.make_start()
                                            draw(win, grid, COLS, ROWS, width, height)
                        draw(win, grid, COLS, ROWS, width, height)


            pygame.display.update()
        while djikstra:
            draw(win, grid, COLS, ROWS, width, height)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    djikstra = False
                    whole = False
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, COLS, width, height)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif spot != end and spot != start:
                        spot.make_barrier()

                elif pygame.mouse.get_pressed()[2]:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, COLS, width, height)
                    spot = grid[row][col]
                    spot.reset()
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and start and end:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbors(grid)

                        algorithm(lambda: draw(win, grid, COLS, ROWS, width, height), grid, start, end)

                    if event.key == pygame.K_b:
                        djikstra = False
                        secuencial = False
                        menu = True
                        grid = make_grid_m(ROWS, COLS, width, height)
                        roomba = None
                        start = None
                        end = None

                    if event.key == pygame.K_c:
                        start = None
                        end = None
                        grid = make_grid(ROWS, COLS, width, height)
                pygame.display.update()

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main(WIN, WIDTH, HEIGHT)
