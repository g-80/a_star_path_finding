from queue import PriorityQueue
import pygame

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* path finding")

RED = (204, 81, 81)
GREEN = (130, 220, 105)
BLUE = (0, 152, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (157, 157, 157)
ORANGE = (240, 165, 0)


class Node:
    def __init__(self, row, column, width, total_rows):
        self.row = row
        self.column = column
        self.x = row * width
        self.y = column * width
        self.width = width
        self.total_rows = total_rows
        self.f_score = float("inf")
        self.g_score = float("inf")
        self.came_from = None
        self.neighbours = []
        self.colour = WHITE

    def get_pos(self):
        return (self.row, self.column)

    def is_barrier(self):
        return self.colour == BLACK

    def is_start(self):
        return self.colour == GREY

    def is_end(self):
        return self.colour == GREEN

    def make_path(self):
        self.colour = BLUE

    def make_barrier(self):
        self.colour = BLACK

    def make_start(self):
        self.colour = GREY
        self.f_score = 0
        self.g_score = 0

    def make_open(self):
        self.colour = GREEN

    def make_closed(self):
        self.colour = RED

    def make_end(self):
        self.colour = ORANGE

    def update_neighbours(self, grid):
        self.neighbours = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.column])

        # Up
        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.column])

        # Right
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.column + 1])

        # Left
        if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.column - 1])

    def draw(self, win):
        pygame.draw.rect(win, self.colour,
                         (self.x, self.y, self.width, self.width))

    def reset(self):
        if self.is_start():
            self.f_score = float("inf")
            self.g_score = float("inf")
        self.colour = WHITE


def calc_heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def draw_shortest_path(came_from, current, draw_func):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw_func()


def algorithm(draw_func, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = calc_heuristic(start.get_pos(), end.get_pos())
    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            draw_shortest_path(came_from, end, draw_func)
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + \
                    calc_heuristic(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw_func()

        if current != start:
            current.make_closed()
    return False


def make_grid(rows, width):
    grid = []
    node_width = width // rows
    for row in range(rows):
        grid.append([])
        for column in range(rows):
            node = Node(row, column, node_width, rows)
            grid[row].append(node)
    return grid


def draw_grid_lines(win, rows, width):
    node_width = width // rows
    for row in range(rows):
        # draw horizontal lines
        pygame.draw.line(win, GREY, (0, row * node_width),
                         (width, row * node_width))
        for column in range(rows):
            # draw vertical lines
            pygame.draw.line(win, GREY, (column * node_width, 0),
                             (column * node_width, width))


def draw_grid(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.display.update()


def get_click_pos(pos, rows, width):
    node_width = width // rows
    y, x = pos
    row = y // node_width
    column = x // node_width
    return row, column


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start_node = None
    end_node = None

    run = True
    while run:
        draw_grid(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # LMB
                pos = pygame.mouse.get_pos()
                row, column = get_click_pos(pos, ROWS, width)
                node = grid[row][column]
                if not start_node and node != end_node:
                    start_node = node
                    start_node.make_start()
                elif not end_node and node != start_node:
                    end_node = node
                    end_node.make_end()
                elif node != end_node and node != start_node:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RMB
                pos = pygame.mouse.get_pos()
                row, column = get_click_pos(pos, ROWS, width)
                node = grid[row][column]
                node.reset()
                if node == start_node:
                    start_node = None
                if node == end_node:
                    end_node = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_node and end_node:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    algorithm(lambda: draw_grid(win, grid, ROWS,
                                                width), grid, start_node, end_node)

                if event.key == pygame.K_c:
                    start_node = None
                    end_node = None
                    grid = make_grid(ROWS, width)
    pygame.quit()


main(WIN, WIDTH)
