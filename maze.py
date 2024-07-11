import threading
from tkinter import Tk, BOTH, Canvas
import random
import time
import heapq

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def draw(self, canvas, fill_color="black"):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2)
        canvas.pack(fill=BOTH, expand=1)

class Cell:
    def __init__(self, win=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False
        self._x1 = None
        self._x2 = None
        self._y1 = None
        self._y2 = None
        self._win = win
        self.f = float('inf')
        self.g = float('inf')
        self.h = float('inf')
        self.parent = None

    def draw(self, x1, y1, x2, y2):
        if self._win is None: return
        self._x1, self._x2, self._y1, self._y2 = x1, x2, y1, y2
        walls = {'left': (x1, y1, x1, y2), 'top': (x1, y1, x2, y1),
                 'right': (x2, y1, x2, y2), 'bottom': (x1, y2, x2, y2)}
        for wall, coords in walls.items():
            color = "white" if getattr(self, f'has_{wall}_wall') is False else "black"
            self._win.draw_line(Line(Point(*coords[:2]), Point(*coords[2:])), color)

    def draw_move(self, to_cell, undo=False):
        if self._win is None: return
        mid_points = lambda s1, s2: ((s1 + s2) / 2, (s1 + s2) / 2)
        x_mid, y_mid = mid_points(self._x1, self._x2), mid_points(self._y1, self._y2)
        to_x_mid, to_y_mid = mid_points(to_cell._x1, to_cell._x2), mid_points(to_cell._y1, to_cell._y2)
        fill_color = "gray" if undo else "red"
        directions = [
            (self._x1 > to_cell._x1, Line(Point(self._x1, y_mid), Point(x_mid, y_mid))),
            (self._x1 < to_cell._x1, Line(Point(x_mid, y_mid), Point(self._x2, y_mid))),
            (self._y1 > to_cell._y1, Line(Point(x_mid, y_mid), Point(x_mid, self._y1))),
            (self._y1 < to_cell._y1, Line(Point(x_mid, y_mid), Point(x_mid, self._y2)))
        ]
        for condition, line in directions:
            if condition:
                self._win.draw_line(line, fill_color)
                self._win.draw_line(Line(Point(to_x_mid, to_y_mid), Point(*line.p2.coords())), fill_color)

class Window:
    def __init__(self, width, height, close_event):
        self.__root = Tk()
        self.__root.title("Mystical Maze Adventure")
        self.__canvas = Canvas(self.__root, bg="ivory", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = True
        self.__close_event = close_event
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def draw_dot(self, x, y, color="blue", size=4):
        self.__canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline=color)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        while self.__running and not self.__close_event.is_set():
            self.redraw()
        self.__root.destroy()
        print("The adventure ends...")

    def draw_line(self, line, fill_color="black"):
        line.draw(self.__canvas, fill_color)

    def close(self):
        self.__running = False

class Scoreboard:
    def __init__(self):
        self.scores = {}

    def update(self, maze_id, status):
        self.scores[maze_id] = status
        self.display()

    def display(self):
        for maze_id, status in self.scores.items():
            print(f"Maze {maze_id}: {status}")

class Maze:
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, scoreboard=None, maze_id=None):
        self._cells = []
        self._x1, self._y1 = x1, y1
        self._num_rows, self._num_cols = num_rows, num_cols
        self._cell_size_x, self._cell_size_y = cell_size_x, cell_size_y
        self._win = win
        self._scoreboard = scoreboard
        self._maze_id = maze_id
        self._create_cells()
        self._break_entrance_and_exit()
        self._carve_passages_from(0, 0)
        self._reset_cells_visited()
        self.moves = 0
        self.start_time = time.time()

    def _create_cells(self):
        self._cells = [[Cell(self._win) for _ in range(self._num_rows)] for _ in range(self._num_cols)]
        for i in range(self._num_cols):
            for j in range(self._num_rows):
                self._draw_cell(i, j)
        if self._scoreboard:
            self._scoreboard.update(self._maze_id, "Drawing")

    def _draw_cell(self, i, j):
        if self._win is None: return
        x1, y1 = self._x1 + i * self._cell_size_x, self._y1 + j * self._cell_size_y
        self._cells[i][j].draw(x1, y1, x1 + self._cell_size_x, y1 + self._cell_size_y)
        self._animate()

    def _animate(self):
        if self._win:
            self._win.redraw()
            time.sleep(0.05)

    def _break_entrance_and_exit(self):
        self._cells[0][0].has_top_wall = False
        self._draw_cell(0, 0)
        self._cells[-1][-1].has_bottom_wall = False
        self._draw_cell(self._num_cols - 1, self._num_rows - 1)

    def _carve_passages_from(self, cx, cy):
        directions = [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]
        random.shuffle(directions)
        for nx, ny in directions:
            if 0 <= nx < self._num_cols and 0 <= ny < self._num_rows and not self._cells[nx][ny].visited:
                self._break_wall(cx, cy, nx, ny)
                self._carve_passages_from(nx, ny)

    def _break_wall(self, cx, cy, nx, ny):
        if cx == nx:
            if cy > ny:
                self._cells[cx][cy].has_top_wall, self._cells[nx][ny].has_bottom_wall = False, False
            else:
                self._cells[cx][cy].has_bottom_wall, self._cells[nx][ny].has_top_wall = False, False
        else:
            if cx > nx:
                self._cells[cx][cy].has_left_wall, self._cells[nx][ny].has_right_wall = False, False
            else:
                self._cells[cx][cy].has_right_wall, self._cells[nx][ny].has_left_wall = False, False
        self._cells[nx][ny].visited = True
        self._draw_cell(nx, ny)

    def _reset_cells_visited(self):
        for row in self._cells:
            for cell in row:
                cell.visited = False

    def heuristic(self, cell, goal):
        return abs(cell._x1 - goal._x1) + abs(cell._y1 - goal._y1)

    def get_neighbors(self, cell_x, cell_y):
        neighbors = []
        if cell_x > 0 and not self._cells[cell_x][cell_y].has_left_wall:
            neighbors.append((cell_x - 1, cell_y))
        if cell_x < self._num_cols - 1 and not self._cells[cell_x][cell_y].has_right_wall:
            neighbors.append((cell_x + 1, cell_y))
        if cell_y > 0 and not self._cells[cell_x][cell_y].has_top_wall:
            neighbors.append((cell_x, cell_y - 1))
        if cell_y < self._num_rows - 1 and not self._cells[cell_x][cell_y].has_bottom_wall:
            neighbors.append((cell_x, cell_y + 1))
        return neighbors

    def solve(self):
        start = self._cells[0][0]
        goal = self._cells[self._num_cols - 1][self._num_rows - 1]

        open_set = []
        heapq.heappush(open_set, (0, (0, 0)))
        came_from = {}

        self._cells[0][0].g = 0
        self._cells[0][0].f = self.heuristic(start, goal)

        if self._scoreboard:
            self._scoreboard.update(self._maze_id, "Solving")

        while open_set:
            current_f, (current_x, current_y) = heapq.heappop(open_set)
            current = self._cells[current_x][current_y]

            if (current_x, current_y) == (self._num_cols - 1, self._num_rows - 1):
                self.reconstruct_path(came_from, current_x, current_y)
                end_time = time.time()
                elapsed_time = end_time - self.start_time
                if self._scoreboard:
                    self._scoreboard.update(self._maze_id, f"Solved in {elapsed_time:.2f} seconds in {self.moves} moves")
                return True

            current.visited = True

            for neighbor_x, neighbor_y in self.get_neighbors(current_x, current_y):
                neighbor = self._cells[neighbor_x][neighbor_y]
                if neighbor.visited:
                    continue

                tentative_g = current.g + 1

                if tentative_g < neighbor.g:
                    came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + self.heuristic(neighbor, goal)

                    if not any(neighbor.f == f and (neighbor_x, neighbor_y) == pos for f, pos in open_set):
                        heapq.heappush(open_set, (neighbor.f, (neighbor_x, neighbor_y)))

            self.moves += 1

        return False

    def reconstruct_path(self, came_from, current_x, current_y):
        path = []
        while (current_x, current_y) in came_from:
            path.append((current_x, current_y))
            current_x, current_y = came_from[(current_x, current_y)]
        path.append((0, 0))
        path.reverse()

        for x, y in path:
            self._win.draw_dot(self._x1 + x * self._cell_size_x + self._cell_size_x / 2,
                               self._y1 + y * self._cell_size_y + self._cell_size_y / 2, "blue")
            self._animate()

def create_and_run_maze(maze_id, scoreboard, close_event):
    win = Window(800, 600, close_event)
    maze = Maze(50, 50, 12, 16, (700 / 16), (500 / 12), win, scoreboard, maze_id)
    print(f"Maze {maze_id} created")
    if maze.solve():
        print(f"Maze {maze_id} solved, the treasure is yours!")
    else:
        print(f"Maze {maze_id} remains unsolved, the treasure lost to time...")
    close_event.set()
    win.wait_for_close()

def main():
    close_event = threading.Event()
    scoreboard = Scoreboard()
    mazes = 1
    threads = []
    # creates x maze GUI's
    for i in range(mazes):
        t = threading.Thread(target=create_and_run_maze, args=(i+1, scoreboard, close_event))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
