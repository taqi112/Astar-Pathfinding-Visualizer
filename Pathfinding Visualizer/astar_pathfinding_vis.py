from operator import ne
import pygame
import math
from queue import PriorityQueue
import sys



WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("A* Path Finding Visualizer")

# All these colors will be used in the grid to represent what role each node (square) has. For example: Green = open node, Red = closed node, Orange = start node, Purple = path etc.  

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

# The Node class is full of different methods to set the state of each node, what color should it be and what does the color represent. 
# 
class Node: 
    # the self variable represents the instance of the object itself
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
    
    def get_position(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

# ALL THE TURN METHODS ARE GOING TO ACTUALLY TURN THE NODE TO THE RESPECTIVE COLOR. 
    def turnto_closed(self):
        self.color = RED

    def turnto_open(self):
        self.color = GREEN
    
    def turnto_barrier(self):
        self.color = BLACK
    
    def turnto_end(self):
        self.color = TURQUOISE
    
    def turnto_path(self):
        self.color = PURPLE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # Down
            self.neighbors.append(grid[self.row + 1][self.col])
        
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # Up
            self.neighbors.append(grid[self.row - 1][self.col])
        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # Right
            self.neighbors.append(grid[self.row][self.col - 1])
        
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # Left
            self.neighbors.append(grid[self.row][self.col - 1])

        if (self.col > 0 and self.row > 0) and not grid[self.row - 1][self.col - 1].is_barrier():#up L
            self.neighbors.append(grid[self.row - 1][self.col - 1])

        if (self.row < self.total_rows - 1 and self.col > 0) and not grid[self.row + 1][self.col - 1].is_barrier(): # Upper Right 
            self.neighbors.append(grid[self.row + 1][self.col - 1])
        
        if (self.col < self.total_rows - 1 and self.row > 0) and not grid[self.row - 1][self.col + 1].is_barrier():# Lower Left
            self.neighbors.append(grid[self.row - 1][self.col + 1])

        if (self.col < self.total_rows - 1 and self.row < self.total_rows - 1) and not grid[self.row + 1][self.col + 1].is_barrier():# Lower Right
            self.neighbors.append(grid[self.row + 1][self.col + 1])


# lt stands for less than: it handles the case when we compare to nodes together and says the other node is greater than the current node 
    def __lt__(self, other):
        return False

# Heuristic Function (H Cost) = distance from end node
# Calculating manhattan distance 
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.turnto_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_position(), end.get_position())

# This set is here because the priority queue doesnt have any attribute to tell us if the node is in the queue or not and we need to be able to check if there's actually something in the queue or not 
# So Open set hash will help us keep track of all the items in the priority queue and all the items not in the priority queue 
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2] # current = node youre on

        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.turnto_end()
                
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current 
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_position(), end.get_position())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.turnto_open()

        draw()

        if current != start:
            current.turnto_closed()

    
    return False




def make_grid(rows, width):
    grid = []
    gap = width // rows #width of each cube 
    for r in range(rows):
        grid.append([])
        for c in range(rows):
            node = Node(r, c, gap, rows)
            grid[r].append(node)
    
    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    # width: The width of our entire grid (ex: 800px)
    # rows: How many rows we have (ex: 50)
    # gap: indicates what the width of each node (square) should be (ex: 800px/50 = 16px)

    for r in range(rows):
        pygame.draw.line(win, GREY, (0, r*gap), (width, r*gap))
        # Draws a horizontal line from x = 0 to x = width all the way down after every gap
    for c in range(rows):
        pygame.draw.line(win, GREY, (c*gap, 0), (c*gap, width))
        # Draws a vertical line from y = 0 to y = width all the way to the right after every gap


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()


# given a mouse position this function is going to translate that into a row, column position representing the cube clicked on 
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)

        # At beginning of while loop, loop through all the events to see what they are
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        

            if pygame.mouse.get_pressed()[0]: # click left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width) # returns which node we clicked on 
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                
                elif not end and node != start:
                    end = node
                    end.turnto_end()

                elif node != end and node != start:
                    node.turnto_barrier()


            elif pygame.mouse.get_pressed()[2]: # click right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width) # returns which node we clicked on 
                node = grid[row][col] 
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

# If a key is pressed down
# If that key is the space bar and algorithm has not yet started 
# For row in grid 
# For each node in row 
# Update the neighbors 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)


                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()
         
main(WIN, WIDTH)
