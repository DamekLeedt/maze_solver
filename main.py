from tkinter import Tk, BOTH, Canvas
from time import sleep

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, point1:Point, point2:Point):
        self.point1 = point1
        self.point2 = point2

    def draw(self, canvas:Canvas, fill_color):
        canvas.create_line(
            self.point1.x, self.point1.y, self.point2.x, self.point2.y, fill=fill_color, width=2
        )


class Window:
    def __init__(self, width, height):
        self.widget = Tk()
        self.canvas = Canvas(self.widget, width=width, height=height, name="maze_solver")
        self.canvas.pack()
        self.window_run = False
        self.widget.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.widget.update_idletasks()
        self.widget.update()

    def close(self):
        self.window_run = False

    def wait_for_close(self):
        self.window_run = True
        while self.window_run:
            self.redraw()

    def draw_line(self, line:Line, fill_color):
        line.draw(self.canvas, fill_color)

class Cell:
    def __init__(
            self,
            window:Window,
            x1,
            y1,
            size = 10,
            bottom = True,
            left = True,
            right = True, 
            top = True
            ):
        self.has_left_wall = left
        self.has_right_wall = right
        self.has_top_wall = top
        self.has_bottom_wall = bottom
        self._x1 = x1
        self._y1 = y1
        self._x2 = x1 + size
        self._y2 = y1 + size
        self._size = size
        self.center = Point((self._x1 + self._x2) // 2, (self._y1 + self._y2) // 2)
        self._win = window
    
    def __repr__(self):
        return " ".join(map(lambda s: str(s), [self._x1, self._y1, self._x2, self._y2]))
    
    def recalculate(self):
        self.x2 = self.x1 * self.size
        self.y2 = self.y1 * self.size
        
    def draw(self, color):
        if self.has_bottom_wall:
            self._win.draw_line(Line(Point(self._x1, self._y2), Point(self._x2, self._y2)), color)
        if self.has_left_wall:
            self._win.draw_line(Line(Point(self._x1, self._y1), Point(self._x1, self._y2)), color)
        if self.has_right_wall:
            self._win.draw_line(Line(Point(self._x2, self._y1), Point(self._x2, self._y2)), color)
        if self.has_top_wall:
            self._win.draw_line(Line(Point(self._x1, self._y1), Point(self._x2, self._y1)), color)
            
    def draw_move(self, to_cell, undo=False):
        color = "gray"
        if undo:
            color = "red"
        self._win.draw_line(Line(self.center, to_cell.center), color)
        
class Maze:
    def __init__(
            self,
            x1,
            y1,
            num_rows,
            num_cols,
            cell_size,
            win:Window
    ):
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size = cell_size
        self.win = win
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for i in range(self.num_rows):
            self._cells.append([Cell(self.win, 10, 10) for i in range(self.num_cols)])
            
        for row in range(len(self._cells)):
            for cell in range(len(self._cells[row])):
                self._draw_cell(row, cell)

    def _draw_cell(self, i, j):
        new_cell = Cell(self.win, i * self.cell_size + self.x1, j * self.cell_size + self.y1, self.cell_size)
        new_cell.draw("black")
        print(new_cell)
        self._animate(.01)

    def _animate(self, time_to_sleep):
        self.win.redraw()
        sleep(time_to_sleep)

def main():

    win = Window(800, 600)
    maze = Maze(5, 5, 10, 10, 50, win)
    win.wait_for_close()



main()