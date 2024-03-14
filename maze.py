from tkinter import Tk, BOTH, Canvas
import random
from time import sleep
"""
TODO?:
Add other solving algorithms, like breadth-first search or A*
Make the visuals prettier, change the colors, etc
Mess with the animation settings to make it faster/slower. Maybe make backtracking slow and blazing new paths faster?
Add configurations in the app itself using Tkinter buttons and inputs to allow users to change maze size, speed, etc
Make much larger mazes to solve
Make it a game where the user chooses directions
If you made it a game, allow the user to race an algorithm
Make it 3 dimensional
Time the various algorithms and see which ones are the fastest"""

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
        self.width = width
        self.height = height
        self.canvas = Canvas(self.widget, width=width, height=height)
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

    def refresh(self):
        self.canvas.delete("all")


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
        self.visited = False
    
    def __repr__(self):
        return " ".join(map(lambda s: str(s), [self._x1, self._y1, self._x2, self._y2]))
    
    def recalculate(self):
        self._x2 = self._x1 + self._size
        self._y2 = self._y1 + self._size
        self.center = Point((self._x1 + self._x2) // 2, (self._y1 + self._y2) // 2)
        return self
        
    def draw(self, color):
        self._win.draw_line(Line(Point(self._x1, self._y2), Point(self._x2, self._y2)), color if self.has_bottom_wall else "#d9d9d9")
        self._win.draw_line(Line(Point(self._x1, self._y1), Point(self._x1, self._y2)), color if self.has_left_wall else "#d9d9d9")
        self._win.draw_line(Line(Point(self._x2, self._y1), Point(self._x2, self._y2)), color if self.has_right_wall else "#d9d9d9")
        self._win.draw_line(Line(Point(self._x1, self._y1), Point(self._x2, self._y1)), color if self.has_top_wall else "#d9d9d9")
            
    def draw_move(self, to_cell, undo=False):
        color = "gray"
        if undo:
            color = "red"
        self._win.draw_line(Line(self.center, to_cell.center), color)

    def _check_wall(self, to_cell):
        if self._x1 < to_cell._x1:
            if self.has_right_wall or to_cell.has_left_wall:
                return False
        if self._x1 > to_cell._x1:
            if self.has_left_wall or to_cell.has_right_wall:
                return False
        if self._y1 < to_cell._y1:
            if self.has_bottom_wall or to_cell.has_top_wall:
                return False
        if self._y1 > to_cell._y1:
            if self.has_top_wall or to_cell.has_bottom_wall:
                return False
        return True
        
class Maze:
    def __init__(
            self,
            num_rows,
            num_cols,
            win:Window = None
    ):
        self.x1 = 5
        self.y1 = 5
        self.num_rows = num_rows
        self.num_cols = num_cols
        row = col = 1
        while row * num_rows < win.height:
            row += 1
        while col * num_cols < win.width:
            col += 1
        self.cell_size = min(row-1, col-1)
        self.win = win
        random.seed()
        self.time_to_sleep = num_cols / (num_rows ** 3)
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for i in range(self.num_rows):
            self._cells.append([Cell(self.win, 10, 10, self.cell_size) for i in range(self.num_cols)])
            
        for row in range(len(self._cells)):
            for cell in range(len(self._cells[row])):
                self._draw_cell(row, cell)
        self._break_entrance_and_exit()

    def _draw_cell(self, i, j):
        current_cell = self._cells[i][j]
        current_cell._x1, current_cell._y1 = i * self.cell_size + self.x1, j * self.cell_size + self.y1
        current_cell.recalculate()
        current_cell.draw("black")
        self._cells[i][j] = current_cell
        print(current_cell)
        self._animate()

    def _adjacent(self, row, column):
        # 0 = up, 1 = left, 2 = down, 3 = right
        return {
            (row-1, column): row > 0,
            (row, column-1): column > 0,
            (min(self.num_rows - 1, row+1), column): row < self.num_rows,
            (row, min(self.num_cols - 1, column+1)): column < self.num_cols
        }

    def _break_walls_r(self, i, j):
        current_cell:Cell = self._cells[i][j]
        while True:
            to_visit = []
            adjacents = self._adjacent(i, j)
            for path in adjacents:
                if adjacents[path] and not self._cells[path[0]][path[1]].visited:
                    to_visit.append(path)
            if not to_visit:
                current_cell.draw("black")
                return
            chosen_dir = to_visit[random.randrange(0, len(to_visit))]
            try:
                chosen_cell:Cell = self._cells[chosen_dir[0]][chosen_dir[1]]
            except:
                raise Exception(f"Tried to get to index {chosen_dir}. Out of range")
            chosen_cell.visited = True
            if current_cell._x1 < chosen_cell._x1:
                current_cell.has_right_wall = False
                chosen_cell.has_left_wall = False
            elif current_cell._x1 > chosen_cell._x1:
                current_cell.has_left_wall = False
                chosen_cell.has_right_wall = False
            elif current_cell._y1 < chosen_cell._y1:
                current_cell.has_bottom_wall = False
                chosen_cell.has_top_wall = False
            else:
                current_cell.has_top_wall = False
                chosen_cell.has_bottom_wall = False
            self._break_walls_r(chosen_dir[0], chosen_dir[1])

    def _break_entrance_and_exit(self):
        if not self._cells:
            return
        self._cells[0][0].has_top_wall = False
        self._cells[-1][-1].has_bottom_wall = False
        self._draw_cell(0, 0)
        self._draw_cell(self.num_rows-1, self.num_cols-1)

    def _reset_visited(self):
        for row in self._cells:
            for cell in row:
                cell.visited = False

    def solve(self):
        return self._solve_r(0, 0)
    
    def _solve_r(self, i, j):
        self._animate()
        current_cell:Cell = self._cells[i][j]
        current_cell.visited = True
        if current_cell == self._cells[-1][-1]:
            return True
        adjacents = self._adjacent(i, j)
        print(adjacents)
        for path in adjacents:
            if adjacents[path]:
                chosen_cell = self._cells[path[0]][path[1]]
                if not chosen_cell.visited:
                    print("Moving on to", str(path))
                    if current_cell._check_wall(chosen_cell):
                        current_cell.draw_move(chosen_cell)
                        if self._solve_r(path[0], path[1]):
                            return True
                        else:
                            current_cell.draw_move(chosen_cell, True)
        return False



    def _animate(self):
        self.win.redraw()
        sleep(self.time_to_sleep)

def main():

    win = Window(800, 600)
    for _i in range(10):
        size = random.randrange(2, 40)
        maze = Maze(size, size, win)
        maze._break_walls_r(0, 0)
        maze._reset_visited()
        maze.solve()
        sleep(2)
        maze.win.refresh()

    win.wait_for_close()



main()