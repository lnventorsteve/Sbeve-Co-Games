import os
import time
import pygame
import json
import my_gui as gui
import math
import random
import background
import local_games


def get_player_names(Players):
    names = []
    for player in Players:
        names.append(player.name)
    return names



class Snake:
    def __init__(self,theme,Input,Players,n):
        self.theme = theme
        self.Input = Input
        self.display, self.screen, self.scale = self.display_info = self.theme.screen_info()
        self.snake_scale = 32
        self.done = False
        self.debug = False
        self.dead = False
        self.setup_ = False
        self.Players = Players
        self.player = self.Players[0]
        self.n = n
        self.data = None
        if "snake" not in self.player.highScores:
            self.player.highScores["snake"] = {}
        if "snake" not in self.player.playTime:
            self.player.playTime["snake"] = 0

        self.scores = {}
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.blue = (6, 130, 196)
        self.color1 = (255, 0, 0)
        self.green = (0, 255, 0)
        self.snake_color = self.player.color1
        self.s = time.perf_counter() - 1
        self.last_frame = time.perf_counter() + 0.5
        self.next_frame = time.perf_counter()


        self.maxplayers = gui.lable_text(self.theme, (0, -100), (100, 20), "Max Players", 4)
        self.scaleSettings = gui.lable_text(self.theme, (0, -75), (100, 20), "Scale", self.snake_scale)
        self.difficulty_gui = gui.multiple_choice_input(self.theme,(0,-25),(100,20),"Difficulty","Normal",["Easy++","Easy+","Easy","Normal","Hard","Expert","God"],5,pointer=1)
        self.width = gui.Text_Box(self.theme,(-25,-50),(47.5,20),"Width",default_text="Width")
        self.height = gui.Text_Box(self.theme,(25,-50),(47.5,20),"Height",default_text="Height")
        self.grid = gui.multiple_choice_input(self.theme,(0,0),(100,20),"Grid","On",["On","Off"],2)


        self.bg = background.Snake_background(self.display,self.screen[0]*2,self.screen[1]*2,600)

    def setup(self):
        self.bg.update()
        gui.lable(self.theme, (0, -self.screen[1] / self.scale + 75), "Snake", in_box=True, size=(150, 20))
        self.difficulty_gui.update(self.Input)
        gui.text(self.theme, (-120, -50), "Grid Size", in_box=True, size=(100, 20))
        self.maxplayers.update(self.Input)
        self.scaleSettings.update(self.Input)
        self.width.update(self.Input)
        self.height.update(self.Input)
        self.grid.update(self.Input)
        if gui.button(self.theme, (0, 50), (100, 20), "Play", self.Input):
            if gui.get_text(self.width).isnumeric() and gui.get_text(self.height).isnumeric() and gui.get_text(self.scaleSettings).isnumeric():
                self.grid_size = (int(gui.get_text(self.width))-1, int(gui.get_text(self.height))-1)
                if self.grid.text == "On":
                    self.grid_state = True
                else:
                    self.grid_state = False
                self.snake_scale = int(gui.get_text(self.scaleSettings))
                self.apple_scale = self.snake_scale/32
                self.d_text = gui.get_text(self.difficulty_gui)
                if self.d_text == "Easy++":
                    d_value = 2
                elif self.d_text == "Easy+":
                    d_value = 1
                elif self.d_text == "Easy":
                    d_value = 0.5
                elif self.d_text == "Normal":
                    d_value = 0.25
                elif self.d_text == "Hard":
                    d_value = 0.1
                elif self.d_text == "Expert":
                    d_value = 0.05
                elif self.d_text == "God":
                    d_value = 0.01
                self.difficulty = d_value
                self.setup_ = True
                self.gx, self.gy = self.grid_size
                self.grid = self.grid_size

                if f"{self.grid_size[0]+1} by {self.grid_size[1]+1}" not in self.player.highScores["snake"]:
                    self.player.highScores["snake"][f"{self.grid_size[0]+1} by {self.grid_size[1]+1} on {self.d_text}"] = 0

                self.screenx = self.screen[0] - (self.gx+1)/2*self.snake_scale
                self.screeny = self.screen[1] - (self.gy+1)/2*self.snake_scale
                self.snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
                self.input_direction = "left"
                self.inputs = ["left"]
                self.last_direction = "left"
                self.make_apple()

        if gui.button(self.theme, (0, self.theme.screen[1] / self.theme.scale - 15), (100, 20), "back", self.Input):
            return True

    def draw_snake(self):
        for each in self.snake[1:-1]:
            sx, sy = each
            sx = sx * self.snake_scale
            sy = sy * self.snake_scale + self.snake_scale
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + sx+1, self.screeny + sy+1, self.snake_scale-1, self.snake_scale-1))


        for i in range(len(self.snake)):
            each = self.snake[i]
            sx, sy = each
            sx = sx * self.snake_scale
            sy = sy * self.snake_scale + self.snake_scale
            check = []
            if i > 0:
                check.append(self.snake[i - 1])
            if i < len(self.snake)-1:
                check.append(self.snake[i + 1])

            if (each[0] - 1, each[1]) in check:
                pygame.draw.line(self.display, self.snake_color, (self.screenx + sx,self.screeny + sy+1),(self.screenx + sx ,self.screeny + sy + self.snake_scale-1))
            if (each[0] , each[1]  -1) in check:
                pygame.draw.line(self.display, self.snake_color, (self.screenx + sx+1,self.screeny + sy),(self.screenx + sx+self.snake_scale-1,self.screeny + sy))

    def draw_tail(self):
        tx, ty = self.snake[0]
        bx, by = self.snake[1]
        if self.snake[0] == self.snake[1]:
            bx, by = self.snake[2]
        tail_dir = tx - bx, ty - by
        tx = tx * self.snake_scale
        ty = ty * self.snake_scale + self.snake_scale
        pygame.draw.rect(self.display, (0, 0, 0), (self.screenx + tx + 1, self.screeny + ty + 1, self.snake_scale-1, self.snake_scale-1))
        if tail_dir == (-1, 0):  # right
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + tx + (self.snake_scale/2), self.screeny + ty + 1, (self.snake_scale/2), self.snake_scale-1))
        if tail_dir == (0, -1):  # down
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + tx + 1, self.screeny + ty + (self.snake_scale/2), self.snake_scale-1, (self.snake_scale/2)))

        if tail_dir == (1, 0):  # left
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + tx + 1, self.screeny + ty + 1, (self.snake_scale/2), self.snake_scale-1))
        if tail_dir == (0, 1):  # up
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + tx + 1, self.screeny + ty + 1, self.snake_scale-1, (self.snake_scale/2)))

        pygame.draw.circle(self.display, self.snake_color, (self.screenx + (self.snake_scale/2) + tx, self.screeny + (self.snake_scale/2) + ty), (self.snake_scale/2)-1)

    def draw_head(self):
        sx, sy = self.snake[-1]
        sx = sx * self.snake_scale
        sy = sy * self.snake_scale + self.snake_scale
        if self.direction == "up":
            eyes = ((6*self.apple_scale, 10*self.apple_scale), (26*self.apple_scale, 10*self.apple_scale))
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + sx + 1, self.screeny + sy + (self.snake_scale/2), self.snake_scale-1, (self.snake_scale/2)))
        elif self.direction == "right":
            eyes = ((10*self.apple_scale, 26*self.apple_scale), (10*self.apple_scale, 6*self.apple_scale))
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + sx + (self.snake_scale/2), self.screeny + sy + 1, (self.snake_scale/2), self.snake_scale-1))
        elif self.direction == "down":
            eyes = ((26*self.apple_scale, 22*self.apple_scale), (6*self.apple_scale, 22*self.apple_scale))
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + sx + 1, self.screeny + sy + 1, self.snake_scale-1, (self.snake_scale/2)))
        elif self.direction == "left":
            eyes = ((22*self.apple_scale, 6*self.apple_scale), (22*self.apple_scale, 26*self.apple_scale))
            pygame.draw.rect(self.display, self.snake_color, (self.screenx + sx + 1, self.screeny + sy + 1, (self.snake_scale/2), self.snake_scale-1))
        left_eye, right_eye = eyes

        lex, ley = left_eye
        rex, rey = right_eye

        lex = lex + sx
        ley = ley + sy
        rex = rex + sx
        rey = rey + sy
        pygame.draw.circle(self.display, self.snake_color, (self.screenx + (self.snake_scale/2) + sx, self.screeny + (self.snake_scale/2) + sy), (self.snake_scale/2)-1)
        pygame.draw.circle(self.display, self.eyes, (self.screenx + lex, self.screeny + ley), 3*self.apple_scale)
        pygame.draw.circle(self.display, self.eyes, (self.screenx + rex, self.screeny + rey), 3*self.apple_scale)

    def draw_apple(self):
        ax, ay = self.apple
        ax = ax * self.snake_scale
        ay = ay * self.snake_scale + self.snake_scale
        pygame.draw.rect(self.display, (128, 70, 27), (self.screenx + ax + 14*self.apple_scale, self.screeny + ay + 2*self.apple_scale, 4*self.apple_scale, 8*self.apple_scale))
        pygame.draw.circle(self.display, (0, 200, 0), (self.screenx + ax + 20*self.apple_scale, self.screeny + ay + 10*self.apple_scale), 6*self.apple_scale)
        pygame.draw.circle(self.display, (255, 0, 0), (self.screenx + ax + 12*self.apple_scale, self.screeny + ay + 17*self.apple_scale), 10*self.apple_scale)
        pygame.draw.circle(self.display, (255, 0, 0), (self.screenx + ax + 20*self.apple_scale, self.screeny + ay + 17*self.apple_scale), 10*self.apple_scale)
        pygame.draw.circle(self.display, (255, 0, 0), (self.screenx + ax + 12*self.apple_scale, self.screeny + ay + 22*self.apple_scale), 8*self.apple_scale)
        pygame.draw.circle(self.display, (255, 0, 0), (self.screenx + ax + 20*self.apple_scale, self.screeny + ay + 22*self.apple_scale), 8*self.apple_scale)

    def score(self):
        gui.lable_value(self.theme, (0, -(self.gy / 2) * (self.snake_scale / self.scale)), "score = ",
                        (len(self.snake) - 3), in_box=True,
                        size=(((self.gx + 1) * self.snake_scale) / self.scale, self.snake_scale / self.scale))
        if len(self.snake) - 3 > self.player.highScores["snake"][
            f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1} on {self.d_text}"]:
            self.player.highScores["snake"][
                f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1} on {self.d_text}"] = len(self.snake) - 3

    def draw_grid(self):
        for x in range(self.gx + 2):
            x + 1
            pygame.draw.line(self.display, (128, 128, 128),
                             (self.screenx + x * self.snake_scale, self.screeny + self.snake_scale), (
                             self.screenx + x * self.snake_scale,
                             self.screeny + (self.gy + 1) * self.snake_scale + self.snake_scale))
        for y in range(self.gy + 2):
            pygame.draw.line(self.display, (128, 128, 128),
                             (self.screenx, self.screeny + y * self.snake_scale + self.snake_scale), (
                             self.screenx + (self.gx + 1) * self.snake_scale,
                             self.screeny + y * self.snake_scale + self.snake_scale))

    def update(self):
        self.n.send({"packet":"player_input","Server":self.server,"mosue":self.Input.mouse_info,"Keys":self.Input.Keys_pressed})
        data = self.n.receive("game_info")
        if data != None:
            self.data = data
            self.apple = data["apple"]
            self.snakes = data["snakes"]

        self.draw_apple()
        for snake in self.snakes:
            self.snake = snake["snake"]
            dir = snake["dir"]
            self.snake_color = snake["body"]
            self.eyes = snake["eyes"]
            self.draw_snake()
            self.draw_tail()
            self.draw_head()

        if self.grid:
            self.draw_grid()
        self.score()
