import threading
from tkinter import Tk, BOTH, Canvas
import random
import time

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
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("Mystical Maze Adventure")
        self.__canvas = Canvas(self.__root, bg="ivory", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = True
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def draw_dot(self, x, y, color="blue", size=4):
        self.__canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline=color)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        while self.__running:
            self.redraw()
        print("The adventure ends...")

    def draw_line(self, line, fill_color="black"):
        line.draw(self.__canvas, fill_color)

    def close(self):
        self.__running = False

class Maze:
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None):
        self._cells = []
        self._x1, self._y1 = x1, y1
        self._num_rows, self._num_cols = num_rows, num_cols
        self._cell_size_x, self._cell_size_y = cell_size_x, cell_size_y
        self._win = win
        self._create_cells()
        self._break_entrance_and_exit()
        self._carve_passages_from(0, 0)
        self._reset_cells_visited()

    def _create_cells(self):
        self._cells = [[Cell(self._win) for _ in range(self._num_rows)] for _ in range(self._num_cols)]
        for i in range(self._num_cols):
            for j in range(self._num_rows):
                self._draw_cell(i, j)

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

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        if not (0 <= i < self._num_cols and 0 <= j < self._num_rows) or self._cells[i][j].visited:
            return False

        self._cells[i][j].visited = True

        if (i, j) == (self._num_cols - 1, self._num_rows - 1):
            return True

        x1, y1 = self._x1 + i * self._cell_size_x, self._y1 + j * self._cell_size_y
        self._win.draw_dot(x1 + self._cell_size_x / 2, y1 + self._cell_size_y / 2, "blue")
        self._animate()

        if i > 0 and not self._cells[i][j].has_left_wall and self._solve_r(i - 1, j):
            return True
        if i < self._num_cols - 1 and not self._cells[i][j].has_right_wall and self._solve_r(i + 1, j):
            return True
        if j > 0 and not self._cells[i][j].has_top_wall and self._solve_r(i, j - 1):
            return True
        if j < self._num_rows - 1 and not self._cells[i][j].has_bottom_wall and self._solve_r(i, j + 1):
            return True

        self._cells[i][j].visited = False
        self._win.draw_dot(x1 + self._cell_size_x / 2, y1 + self._cell_size_y / 2, "red")
        self._animate()
    
        return False
def create_and_run_maze(maze_id):
    win = Window(800, 600)
    maze = Maze(50, 50, 12, 16, (700 / 16), (500 / 12), win)
    print(f"Maze {maze_id} created")
    if maze.solve():
        print(f"Maze {maze_id} solved, the treasure is yours!")
    else:
        print(f"Maze {maze_id} remains unsolved, the treasure lost to time...")
    win.wait_for_close()



def main():
    threads = []
    for i in range(4):
        # Create a new thread for each maze instance
        t = threading.Thread(target=create_and_run_maze, args=(i+1,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
