from tkinter import *
import math

# colors
WHITE = "white"
BLACK = "black"
RED = "red"
BLUE = "lightblue"


def get_flipped_color(color):
    if color == BLACK:
        return WHITE
    if color == WHITE or color == BLUE:
        return BLACK
    raise Exception("Unknown color : " + color)


# directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


def right_dir(direction):
    return (direction + 1) % 4  # since directions are numbered from 0 to 3


def left_dir(direction):
    return (direction - 1) % 4  # since directions are numbered from 0 to 3


# TK config
X_CELLS = 71
Y_CELLS = 51
CELL_SIZE = 13
SLEEP_TIME = 1     # time in ms between 2 moves
DEFAULT_SPEED = 1  # number of moves before a sleep


class Cell:
    def __init__(self, widget, x, y, color=WHITE):
        self.widget = widget
        self.x = x
        self.y = y
        self.color = color


class Ant:
    def __init__(self, widget, x, y, direction=UP):
        self.widget = widget
        self.x = x
        self.y = y
        self.dir = direction


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.cells = dict()
        self.finished = False   # cant go any further due to grid size
        self.stopped = False    # user interrupted the run
        self.running = False    # currently running (avoid multiple callbacks)
        self.steps = 0
        self.speed = DEFAULT_SPEED

        if X_CELLS % 2 == 0 or Y_CELLS % 2 == 0:
            raise Exception("The number of cells in both directions must be odd.")

        # Title
        self.title_label = Label(self, text="Langton's ant", justify=CENTER)
        self.title_label.pack()

        # Frame
        self.frame = Frame(self, padx=1, pady=1, borderwidth=2, relief=GROOVE)
        self.frame.pack()

        # Canvas Grid and squares
        self.canvas = Canvas(self.frame,
                             width=10 + X_CELLS * CELL_SIZE,
                             height=10 + Y_CELLS * CELL_SIZE,
                             bd=0, background=WHITE)
        for i in range(0, 1 + X_CELLS):
            self.canvas.create_line(5 + CELL_SIZE * i, 5,
                                    5 + CELL_SIZE * i, 5 + Y_CELLS * CELL_SIZE,
                                    fill=BLACK)
        for j in range(0, 1 + Y_CELLS):
            self.canvas.create_line(5, 5 + CELL_SIZE * j,
                                    5 + X_CELLS * CELL_SIZE, 5 + CELL_SIZE * j,
                                    fill=BLACK)
        self.canvas.pack()

        for i in range(0, X_CELLS):
            for j in range(0, Y_CELLS):
                cell = self.canvas.create_rectangle(
                    5 + i * CELL_SIZE + 1, 5 + j * CELL_SIZE + 1,
                    (i + 1) * CELL_SIZE + 5, 5 + (j + 1) * CELL_SIZE,
                    fill=BLUE, outline="")
                self.cells[(i, j)] = Cell(cell, i, j)

        # Ant
        self.x0 = math.trunc(X_CELLS / 2)
        self.y0 = math.trunc(Y_CELLS / 2)
        ant_widget = self.canvas.create_oval(
            5 + self.x0 * CELL_SIZE + 1 + 1, 5 + self.y0 * CELL_SIZE + 1 + 1,
            5 + (self.x0 + 1) * CELL_SIZE - 1, 5 + (self.y0 + 1) * CELL_SIZE - 1,
            fill=RED, outline="")
        self.ant = Ant(ant_widget, self.x0, self.y0)

        # Start / Stop / Reset buttons

        self.bottom_frame = Frame(self)
        self.bottom_frame.pack()

        self.next_button = Button(self, text="Next", command=self.next_button_click)
        self.next_button.pack(side="left")
        self.run_button = Button(self, text="Run", command=self.run_button_click)
        self.run_button.pack(side="left")
        self.stop_button = Button(self, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side="left")
        self.reset_button = Button(self, text="Reset", command=self.reset_button_click)
        self.reset_button.pack(side="left")

        # speed adjustment
        var = IntVar()
        var.set(DEFAULT_SPEED)

        def update_speed():
            self.speed = var.get()

        Label(self, text=' ', padx=20).pack(side='left')  # spacer
        Label(self, text="Speed : ").pack(side="left")
        Radiobutton(self, text="x1", variable=var, value=1, command=update_speed).pack(side="left")
        Radiobutton(self, text="x5", variable=var, value=5, command=update_speed).pack(side="left")
        Radiobutton(self, text="x10", variable=var, value=10, command=update_speed).pack(side="left")

        # steps count
        self.steps_label1 = Label(self, text="Step : ")
        self.steps_label2 = Label(self, text="0")
        self.steps_label2.pack(side="right")
        self.steps_label1.pack(side="right")

    def get_next_cell(self, direction):
        x = self.ant.x
        y = self.ant.y
        if direction == UP:
            return x, y - 1
        if direction == RIGHT:
            return x + 1, y
        if direction == DOWN:
            return x, y + 1
        if direction == LEFT:
            return x - 1, y

    def ant_cell_color(self):
        return self.cells[(self.ant.x, self.ant.y)].color

    def get_next_dir(self):
        curr_color = self.ant_cell_color()
        if curr_color == BLACK:
            return left_dir(self.ant.dir)
        elif curr_color == WHITE or curr_color == BLUE:
            return right_dir(self.ant.dir)

    def move_ant(self):
        direction = self.get_next_dir()
        (next_x, next_y) = self.get_next_cell(direction)
        if not 0 <= next_x < X_CELLS or not 0 <= next_y < Y_CELLS:
            return False  # out of grid
        else:
            dx = (next_x - self.ant.x) * CELL_SIZE
            dy = (next_y - self.ant.y) * CELL_SIZE
            self.canvas.move(self.ant.widget, dx, dy)
            self.steps += 1
            self.steps_label2.config(text=str(self.steps))
            self.ant.x = next_x
            self.ant.y = next_y
            self.ant.dir = direction
            return True

    def set_cell_color(self, x, y, color):
        cell = self.cells[(x, y)]
        cell.color = color  # logical flip
        self.canvas.itemconfigure(cell.widget, fill=color)  # visual flip

    def flip_cell_color(self, x, y):
        cell = self.cells[(x, y)]
        next_color = get_flipped_color(cell.color)
        self.set_cell_color(x, y, next_color)

    def next_turn(self):
        cell_before_move = self.cells[(self.ant.x, self.ant.y)]
        moved = self.move_ant()
        if moved:
            self.flip_cell_color(cell_before_move.x, cell_before_move.y)
        return moved

    def start_play_loop(self):
        if self.finished or self.stopped:
            return
        moved = False
        for _ in range(self.speed):
            moved = self.next_turn()
        if moved:
            self.after(SLEEP_TIME, self.start_play_loop)
        else:
            self.finished = True

    def next_button_click(self):
        if self.finished or self.running:
            return
        moved = self.next_turn()
        if not moved:
            self.finished = True

    def run_button_click(self):
        if self.finished or self.running:
            return
        self.stopped = False
        self.running = True
        self.start_play_loop()
        self.running = False

    def stop_button_click(self):
        self.stopped = True

    def reset_button_click(self):
        # reset grid
        for i in range(0, X_CELLS):
            for j in range(0, Y_CELLS):
                self.set_cell_color(i, j, BLUE)
        # reset ant
        dx = (self.x0 - self.ant.x) * CELL_SIZE
        dy = (self.y0 - self.ant.y) * CELL_SIZE
        self.canvas.move(self.ant.widget, dx, dy)
        self.steps = 0
        self.ant.x = self.x0
        self.ant.y = self.y0
        self.ant.dir = UP
        # reset flags
        self.stopped = False
        self.finished = False
        self.running = False


app = App()
app.mainloop()
