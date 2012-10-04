import sys
import time
import random
import Queue 

from Tkinter import Tk, Frame, Canvas, W
from threading import Thread
from collections import deque

snake_default_points = [(245, 155), (255, 155), (265, 155), (275, 155)]

class Food(object):
    """Food."""
    
    def __init__(self, queue):
        """Init Food."""
        self.queue = queue
        self.score = 1
        self.reposition(snake_default_points)

    def reposition(self, forbidden_points=[]):
        """Move food to random position."""
        while True:
            x = random.randrange(5, 495, 10)
            y = random.randrange(5, 295, 10)
            self.position = x, y
            if not self.position in forbidden_points:
                break
        self.queue.put(dict(food=self.position))

class Snake(Thread):
    """Snake."""

    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

    def __init__(self, queue):
        """Init Snake."""
        Thread.__init__(self)
        self.daemon = True
        self.queue = queue

        self.score = 0
        self.points = deque(snake_default_points)
        self.foods = []
        self.move_direction = self.RIGHT
        self.pause = False

    def keypress_handler(self, event):
        """Handels events."""
        keysym = event.keysym
        if keysym == 'Left':
            self.move_direction = self.LEFT
        elif keysym == 'Right':
            self.move_direction = self.RIGHT
        elif keysym == 'Up':
            self.move_direction = self.UP
        elif keysym == 'Down':
            self.move_direction = self.DOWN
        elif keysym in ['p', 'P']:
            if self.pause == False:
                self.pause = True
            else:
                self.pause = False

    def move(self):
        """Move snake."""
        if self.pause:
            return

        # calculate new position
        last_x, last_y = self.points[-1]
        move_direction = self.move_direction
        if move_direction == self.LEFT:
            newpoint = (last_x - 10), last_y
        elif move_direction == self.RIGHT:
            newpoint = (last_x + 10), last_y
        elif move_direction == self.UP:
            newpoint = last_x, (last_y - 10)
        elif move_direction == self.DOWN:
            newpoint = last_x, (last_y + 10)
        
        # check for selfcollision or wallcollision
        if newpoint in self.points or newpoint[0] in [-5, 505] or newpoint[1] in [-5, 305]:
            self.queue.put(dict(quit=None))

        # move snake
        self.points.append(newpoint)

        # only remove first snake point if snake did not eat
        for food in self.foods:
            if food.position == newpoint:
                self.score += food.score
                self.queue.put(dict(score=self.score))
                food.reposition()
            else:
                self.points.popleft()

    def run(self):
        """Run thread."""
        while True:
            self.queue.put(dict(snake=self.points))
            time.sleep(0.1)
            self.move()

class App(Frame):
    """Tkinter App."""

    def __init__(self, parent, queue):
        """Init Tkinter app."""
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.wm_attributes('-type', 'dialog')

        self.queue = queue
        self.initUI()
        self.worker()

    def initUI(self):
        """Init UI."""
        self.parent.title('PySnake')
        self.canvas = Canvas(self.parent, width=500, height=300, bg='black')
        self.canvas.pack()

        self.score = self.canvas.create_text(30, 270, anchor=W, fill='blue', text='Score: 0')
        self.food = self.canvas.create_rectangle(0, 0, 0, 0, fill='white')
        self.snake = self.canvas.create_line((0, 0), (0, 0), fill='green', width=10)

    def worker(self):
        try:
            while True:
                job = self.queue.get_nowait()
                if job.has_key('snake'):
                    #self.snake = self.canvas.create_line(*job['snake'], fill='green', width=10)
                    points = [x for point in job['snake'] for x in point]
                    self.canvas.coords(self.snake, *points)
                elif job.has_key('food'):
                    x, y = job['food']
                    self.canvas.coords(self.food, (x - 5), (y - 5), (x + 5), (y + 5))
                elif job.has_key('score'):
                    self.canvas.itemconfigure(self.score, text='Score: {}'.format(job['score']))
                elif job.has_key('quit'):
                    self.parent.quit()
                self.queue.task_done()
        except Queue.Empty:
            pass
        self.after(50, self.worker)

root = Tk()
queue = Queue.Queue()

app = App(root, queue)
snake = Snake(queue)
food = Food(queue)
snake.foods.append(food)

root.bind('<KeyPress-Left>', snake.keypress_handler)
root.bind('<KeyPress-p>', snake.keypress_handler)
root.bind('<KeyPress-P>', snake.keypress_handler)
root.bind('<KeyPress-Right>', snake.keypress_handler)
root.bind('<KeyPress-Up>', snake.keypress_handler)
root.bind('<KeyPress-Down>', snake.keypress_handler)

snake.start()
root.mainloop()

print 'You have reached {score} points!'.format(score=snake.score)
