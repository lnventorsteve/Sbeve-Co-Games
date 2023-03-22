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
        self.join_ = False
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
        self.server_ID = None
        self.clients = {}
        self.snakes = []
        self.all_snakes = []
        self.input_direction = "left"
        self.inputs = ["left"]
        self.last_direction = "left"
        self.my_direction = "left"
        self.direction = "left"
        self.maxplayers_gui = gui.lable_text(self.theme, (0, -100), (100, 20), "Max Players", 4)
        self.scaleSettings_gui = gui.lable_text(self.theme, (0, -75), (100, 20), "Scale", self.snake_scale)
        self.difficulty_gui = gui.multiple_choice_input(self.theme,(0,-25),(100,20),"Difficulty","Normal",["Easy++","Easy+","Easy","Normal","Hard","Expert","God"],5,pointer=1)
        self.width_gui = gui.Text_Box(self.theme,(-25,-50),(47.5,20),"Width",default_text="Width")
        self.height_gui = gui.Text_Box(self.theme,(25,-50),(47.5,20),"Height",default_text="Height")
        self.grid_gui = gui.multiple_choice_input(self.theme,(0,0),(100,20),"Grid","On",["On","Off"],2)


        self.bg = background.Snake_background(self.display,self.screen[0]*2,self.screen[1]*2,600)

    def setup(self):
        self.bg.update()
        gui.lable(self.theme, (0, -self.screen[1] / self.scale + 75), "Snake", in_box=True, size=(150, 20))
        self.difficulty_gui.update(self.Input)
        gui.text(self.theme, (-120, -50), "Grid Size", in_box=True, size=(100, 20))
        self.maxplayers_gui.update(self.Input)
        self.scaleSettings_gui.update(self.Input)
        self.width_gui.update(self.Input)
        self.height_gui.update(self.Input)
        self.grid_gui.update(self.Input)
        if gui.button(self.theme, (0, 50), (100, 20), "Play", self.Input):
            if gui.get_text(self.width_gui).isnumeric() and gui.get_text(self.height_gui).isnumeric() and gui.get_text(self.scaleSettings_gui).isnumeric() and gui.get_text(self.maxplayers_gui).isnumeric():
                self.grid_size = (int(gui.get_text(self.width_gui))-1, int(gui.get_text(self.height_gui))-1)
                if self.grid_gui.text == "On":
                    self.grid_state = True
                else:
                    self.grid_state = False
                self.snake_scale = int(gui.get_text(self.scaleSettings_gui))
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
                self.gx, self.gy = self.grid_size
                self.grid = self.grid_size
                self.n.send({"packet": "new_server"})

        data = self.n.receive("new_server")
        if data != None:
            self.server_ID = data["server"]["ID"]
            self.n.send({"packet": "add_data", "server": self.server_ID, "key": "server_info", "data": {"Host":self.player.name,"Type":"game","Name":"Snake","Max players":gui.get_text(self.maxplayers_gui),"Grid":(self.gx+1, self.gy+1),"Difficulty":self.d_text}})
            self.n.send({"packet": "add_data", "server": self.server_ID, "key": "Snakes", "data": {}})
            self.n.send({"packet": "add_data", "server": self.server_ID, "key": "Apples", "data": []})
            self.n.send({"packet": "join_server", "server": self.server_ID,"name":self.player.name})
            self.setup_ = True

            if f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1}" not in self.player.highScores["snake"]:
                self.player.highScores["snake"][
                    f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1} on {self.d_text}"] = 0

            self.screenx = self.screen[0] - (self.gx + 1) / 2 * self.snake_scale
            self.screeny = self.screen[1] - (self.gy + 1) / 2 * self.snake_scale
            self.my_snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
            self.snake = self.my_snake
            self.make_apple()
            self.snakes = {self.player.name:{"snake":self.my_snake,"direction":self.my_direction,"body":self.player.color1,"eyes":self.player.color2}}

        if gui.button(self.theme, (0, self.theme.screen[1] / self.theme.scale - 15), (100, 20), "back", self.Input):
            return True

    def join(self):
        gui.lable(self.theme,(0,0),"Getting Server Info")
        data = self.n.receive("server_info")
        if data != None:
            data = data["data"]
            x,y = data["Grid"]
            self.grid_size = (x - 1, y - 1)
            self.grid = self.grid_size
            self.gx, self.gy = self.grid_size

            self.d_text = data["Difficulty"]
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

            if f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1}" not in self.player.highScores["snake"]:
                self.player.highScores["snake"][
                    f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1} on {self.d_text}"] = 0

            self.snake_scale = 32
            self.apple_scale = self.snake_scale / 32
            self.screenx = self.screen[0] - (self.gx + 1) / 2 * self.snake_scale
            self.screeny = self.screen[1] - (self.gy + 1) / 2 * self.snake_scale
            self.my_snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
            self.snake = self.my_snake
            self.make_apple()
            self.snakes = {self.player.name:{"snake":self.my_snake,"direction":self.my_direction,"body":self.player.color1,"eyes":self.player.color2}}
            self.join_ = False

    def draw_snake(self,snake,body_color):
        for each in snake[1:-1]:
            sx, sy = each
            sx = sx * self.snake_scale
            sy = sy * self.snake_scale + self.snake_scale
            pygame.draw.rect(self.display, body_color, (self.screenx + sx+1, self.screeny + sy+1, self.snake_scale-1, self.snake_scale-1))


        for i in range(len(snake)):
            each = snake[i]
            sx, sy = each
            sx = sx * self.snake_scale
            sy = sy * self.snake_scale + self.snake_scale
            check = []
            if i > 0:
                check.append(snake[i - 1])
            if i < len(snake)-1:
                check.append(snake[i + 1])

            if (each[0] - 1, each[1]) in check:
                pygame.draw.line(self.display, body_color, (self.screenx + sx,self.screeny + sy+1),(self.screenx + sx ,self.screeny + sy + self.snake_scale-1))
            if (each[0] , each[1]  -1) in check:
                pygame.draw.line(self.display, body_color, (self.screenx + sx+1,self.screeny + sy),(self.screenx + sx+self.snake_scale-1,self.screeny + sy))

    def draw_tail(self,snake,body_color):
        tx, ty = snake[0]
        bx, by = snake[1]
        if snake[0] == snake[1]:
            bx, by = snake[2]
        tail_dir = tx - bx, ty - by
        tx = tx * self.snake_scale
        ty = ty * self.snake_scale + self.snake_scale
        pygame.draw.rect(self.display, (0, 0, 0), (self.screenx + tx + 1, self.screeny + ty + 1, self.snake_scale-1, self.snake_scale-1))
        if tail_dir == (-1, 0):  # right
            pygame.draw.rect(self.display, body_color, (self.screenx + tx + (self.snake_scale/2), self.screeny + ty + 1, (self.snake_scale/2), self.snake_scale-1))
        if tail_dir == (0, -1):  # down
            pygame.draw.rect(self.display, body_color, (self.screenx + tx + 1, self.screeny + ty + (self.snake_scale/2), self.snake_scale-1, (self.snake_scale/2)))

        if tail_dir == (1, 0):  # left
            pygame.draw.rect(self.display, body_color, (self.screenx + tx + 1, self.screeny + ty + 1, (self.snake_scale/2), self.snake_scale-1))
        if tail_dir == (0, 1):  # up
            pygame.draw.rect(self.display, body_color, (self.screenx + tx + 1, self.screeny + ty + 1, self.snake_scale-1, (self.snake_scale/2)))

        pygame.draw.circle(self.display, body_color, (self.screenx + (self.snake_scale/2) + tx, self.screeny + (self.snake_scale/2) + ty), (self.snake_scale/2)-1)

    def draw_head(self,snake,direction,body_color,eye_color):
        sx, sy = snake[-1]
        sx = sx * self.snake_scale
        sy = sy * self.snake_scale + self.snake_scale
        if direction == "up":
            eyes = ((6*self.apple_scale, 10*self.apple_scale), (26*self.apple_scale, 10*self.apple_scale))
            pygame.draw.rect(self.display, body_color, (self.screenx + sx + 1, self.screeny + sy + (self.snake_scale/2), self.snake_scale-1, (self.snake_scale/2)))
        elif direction == "right":
            eyes = ((10*self.apple_scale, 26*self.apple_scale), (10*self.apple_scale, 6*self.apple_scale))
            pygame.draw.rect(self.display, body_color, (self.screenx + sx + (self.snake_scale/2), self.screeny + sy + 1, (self.snake_scale/2), self.snake_scale-1))
        elif direction == "down":
            eyes = ((26*self.apple_scale, 22*self.apple_scale), (6*self.apple_scale, 22*self.apple_scale))
            pygame.draw.rect(self.display, body_color, (self.screenx + sx + 1, self.screeny + sy + 1, self.snake_scale-1, (self.snake_scale/2)))
        elif direction == "left":
            eyes = ((22*self.apple_scale, 6*self.apple_scale), (22*self.apple_scale, 26*self.apple_scale))
            pygame.draw.rect(self.display, body_color, (self.screenx + sx + 1, self.screeny + sy + 1, (self.snake_scale/2), self.snake_scale-1))
        left_eye, right_eye = eyes

        lex, ley = left_eye
        rex, rey = right_eye

        lex = lex + sx
        ley = ley + sy
        rex = rex + sx
        rey = rey + sy
        pygame.draw.circle(self.display, body_color, (self.screenx + (self.snake_scale/2) + sx, self.screeny + (self.snake_scale/2) + sy), (self.snake_scale/2)-1)
        pygame.draw.circle(self.display, eye_color, (self.screenx + lex, self.screeny + ley), 3*self.apple_scale)
        pygame.draw.circle(self.display, eye_color, (self.screenx + rex, self.screeny + rey), 3*self.apple_scale)

    def make_apple(self):
        timeout = time.perf_counter() + 0.08
        ax = random.randrange(0, self.gx+1)
        ay = random.randrange(0, self.gy+1)
        while (ax, ay) in self.snake:
            ax = random.randrange(0, self.gx+1)
            ay = random.randrange(0, self.gy+1)
            if time.perf_counter() > timeout:
                self.apple = (-1,-1)
                break
        self.apple = (ax,ay)

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

    def death(self):
        hx, hy = self.my_snake[-1]
        print(self.all_snakes[0:-1])

        if 0 > hx:
            self.dead = True
        elif hx > self.gx:
            self.dead = True
        elif 0 > hy:
            self.dead = True
        elif hy > self.gy:
            self.dead = True
        elif self.my_snake[-1] in self.all_snakes[0:-1]:
            self.dead = True

        if self.dead:
            self.my_snake.pop()
            self.my_snake.insert(0,self.old_snake)

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

    def move_snake(self):
        self.old_snake = self.my_snake[0]
        hx, hy = self.my_snake[-1]
        if self.my_direction == "up":
            hy -= 1
        if self.my_direction == "down":
            hy += 1
        if self.my_direction == "left":
            hx += 1
        if self.my_direction == "right":
            hx -= 1

        self.my_snake.append((hx, hy))
        self.my_snake.pop(0)

    def settings(self):
        if gui.button(self.theme, (0, 50), (100, 20), "exit game", self.Input):
            return "exit"

    def exit(self):
        self.n.send({"packet": "leave_server", "server": self.server_ID})

    def update(self):
        for key in self.Input.keys:
            if key == 114:
                self.my_snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
                self.input_direction = "left"
                self.inputs = ["left"]
                self.last_direction = "left"
                self.dead = False

            if key == 119 and self.last_direction != "down" or key == 1073741906 and self.last_direction != "down":
                self.input_direction = "up"
            elif key == 97 and self.last_direction != "left" or key == 1073741904 and self.last_direction != "left":
                self.input_direction = "right"
            elif key == 115 and self.last_direction != "up" or key == 1073741905 and self.last_direction != "up":
                self.input_direction = "down"
            elif key == 100 and self.last_direction != "right" or key == 1073741903 and self.last_direction != "right":
                self.input_direction = "left"

            if self.input_direction != self.last_direction:
                self.last_direction = self.input_direction
                self.inputs.append(self.input_direction)


        if time.perf_counter() >= self.next_frame:
            self.next_frame = time.perf_counter() + self.difficulty
            if not self.dead:
                if len(self.inputs) > 1:
                    self.inputs.pop(0)
                self.my_direction = self.inputs[0]
                self.move_snake()
                self.death()
                if self.my_snake[-1] == self.apple:
                    self.my_snake.insert(0, self.my_snake[0])
                    self.make_apple()
            self.n.send(
                {"packet": "snake_data", "server": self.server_ID, "name": self.player.name, "snake": self.my_snake,
                 "direction": self.my_direction, "body": self.player.color1, "eyes": self.player.color2})
        data = self.n.receive("snake_data")
        if data != None:
            self.snakes = data["data"]
        #self.draw_grid()
        self.draw_apple()
        self.all_snakes = []
        for name in self.snakes:
            snake = self.snakes[name]
            self.all_snakes += snake["snake"]
            self.draw_snake(snake["snake"] ,snake["body"])
            self.draw_head(snake["snake"] ,snake["direction"],snake["body"],snake["eyes"])
            self.draw_tail(snake["snake"] ,snake["body"])

        self.draw_snake(self.my_snake,self.player.color1)
        self.draw_head(self.my_snake, self.my_direction,self.player.color1,self.player.color2)
        self.draw_tail(self.my_snake,self.player.color1)
        self.score()


class Dot_Game:
    def __init__(self,theme,Input,Players,n):
        self.display = theme.display
        self.screen = theme.screen
        self.theme = theme
        self.Input = Input
        self.Players = Players
        self.scale = 50
        self.tcolor = theme.tcolor
        self.scaleSettings = gui.lable_text(self.theme,(60,0),(100,15),"Scale",self.scale)
        self.half = self.scale/2
        self.playagain = False
        self.setup_ = False

        self.players = []
        self.dots = []
        self.lines= []
        self.moves = {}
        self.colors = {}
        self.scores = {}
        self.squares = {}
        self.turn = 0
        self.X = 10
        self.Y = 10

        self.X_ui = gui.Text_Box(theme,(35,-100),(40,15),"X", default_text = "X")
        self.Y_ui = gui.Text_Box(theme, (85, -100), (40, 15), "Y", default_text = "Y")

        for each in Players:
            self.players.append(each.name)
            self.moves[each.name] = []
            self.colors[each.name] = each.color1
            self.scores[each.name] = 0
            self.squares[each.name] = []

        self.turn_ui = gui.multiple_choice_input(theme,(60,-75),(100,15),"",self.players[0],self.players,5)
        self.num_of_players_ui = gui.multiple_choice_input(theme,(60,-50),(100,15),"Num of players?",len(self.players),range(len(self.players)+1)[1:],5)

        self.bg = background.dots_background(self.display, self.screen[0] * 2, self.screen[1] * 2, 600)

    def setup(self):
        self.bg.update()
        gui.lable(self.theme,(-60,-100),"Grid Size", in_box=True, size = (100,15))
        self.X_ui.update(self.Input)
        self.Y_ui.update(self.Input)

        self.turn_ui.update(self.Input)
        gui.lable(self.theme, (-60, -75), "Who goes first?", in_box=True, size=(100, 15))

        self.num_of_players_ui.update(self.Input)

        if gui.button(self.theme,(0,self.theme.screen[1]/self.theme.scale-40),(100,15),"Play!",self.Input):
            if self.X_ui.get_text().isnumeric() and self.Y_ui.get_text().isnumeric():
                self.X = int(self.X_ui.get_text())
                self.Y = int(self.Y_ui.get_text())
                self.offset = (self.screen[0] - self.X * self.half, self.screen[1] - self.Y * self.half)
                self.turn = self.players.index(self.turn_ui.text)
                self.num_of_players = int(self.num_of_players_ui.text)
                self.setup_ = True

        if gui.button(self.theme, (0, self.theme.screen[1]/self.theme.scale-15), (100, 15), "back", self.Input):
            return True


    def load(self):
        self.players = []
        self.dots = []
        self.lines= []
        self.moves = {}
        self.colors = {}
        self.scores = {}
        self.squares = {}
        self.setup_ = True
        with open("saves/dotgame.json", "r") as old_game:
            game = json.loads(old_game.read())

        self.num_of_players = len(game["players"])
        self.turn = game["turn"]
        self.X,self.Y = game["size"]
        self.offset = (self.screen[0]-self.X*self.half,self.screen[1]-self.Y*self.half)
        offx,offy = self.offset

        for player in game["players"]:
            self.players.append(player)
            self.scores[player] = game["players"][player]["score"]
            color_list = game["players"][player]["color"]
            r, g, b = color_list
            self.colors[player] = (r, g, b)
            self.moves[player] = []
            for line in game["players"][player]["moves"]:
                x,y = line
                self.moves[player].append((x,y))
                self.lines.append((x,y))
            self.squares[player] = []
            for squares in game["players"][player]["squares"]:
                x,y = squares
                self.squares[player].append((x,y))

    def settings(self):
        self.scaleSettings.update(self.Input)
        if gui.button(self.theme, (0, 50), (100, 20), "Exit Game", self.Input):
            return "exit"
        if gui.button(self.theme, (0, 75), (100, 20), "Save and Exit", self.Input):
            return "save exit"
        if gui.button(self.theme, (0, 100), (100, 20), "Apply", self.Input):
            if self.scaleSettings.text.isnumeric():
                self.scale = int(self.scaleSettings.text)
                self.half = self.scale/2
                self.offset = (self.screen[0] - self.X * self.half, self.screen[1] - self.Y * self.half)
                return "back"
        return False

    def Draw_Game(self):
        self.display.fill((0, 0, 0))
        gui.text(self.theme, (-self.screen[0]/self.theme.scale, self.screen[1]/self.theme.scale), f"{self.players[self.turn]}'s turn",center="bottom_left")
        offx, offy = self.offset
        _2 = self.scale/25
        _4 = self.scale/12.5
        _23 = self.half - self.scale/25
        _46 = self.scale - self.scale/12.5
        for player in self.players:
            current_color = self.colors[player]
            for line in self.moves[player]:
                X,Y = line
                x, y = X * self.half + offx, Y * self.half + offy
                if X % 2 == 0:
                    pygame.draw.rect(self.display, current_color, ((x - self.half, y - _2), (self.scale, _4))) # draw horizontally
                if Y % 2 == 0:
                    pygame.draw.rect(self.display, current_color, ((x - _2, y - self.half), (_4, self.scale))) # draw vertically
            for square in self.squares[player]:
                X, Y = square
                x, y = X * self.half + offx, Y * self.half + offy
                pygame.draw.rect(self.display, current_color, ((x - _23, y - _23), (_46, _46))) # draw Square down


        for x in range(self.X):
            x = x * self.scale + self.half
            for y in range(self.Y):
                y = y * self.scale + self.half
                pygame.draw.circle(self.display, (128, 128, 128), (offx + x, offy + y), self.scale/10)

    def update(self):
        x, y, mb = self.Input.mouse()
        if mb == 1:
            offx, offy = self.offset
            x, y = x - offx, y - offy
            if  self.half/2  < x < self.X*self.scale - self.half/2  and self.half/2  < y < self.Y*self.scale - self.half/2 :
                X = int(round(x /self.half))
                Y = int(round(y / self.half))
                x, y = X * self.half + offx, Y * self.half + offy
                print(X, Y)
                if X % 2 == 0 ^ Y % 2 == 0:
                    print("invalid move")
                else:
                    print("valid move")
                    playagain = False
                    current_color = self.colors[self.players[self.turn]]
                    if (X,Y) not in self.lines:
                        self.lines.append((X,Y))
                        self.moves[self.players[self.turn]].append((X,Y))

                        print(x, y )

                        if X % 2 == 0:
                            print("X")
                            if (X - 1, Y - 1) in self.lines and (X, Y - 2) in self.lines and (X + 1, Y - 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X,Y - 1))
                                playagain = True

                            if (X - 1, Y + 1) in self.lines and (X, Y + 2) in self.lines and (X + 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X, Y + 1))
                                playagain = True

                        if Y % 2 == 0:
                            print("Y")
                            if (X - 1, Y - 1) in self.lines and (X - 2, Y) in self.lines and (X - 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X - 1, Y))
                                playagain = True

                            if (X + 1, Y - 1) in self.lines and (X + 2, Y) in self.lines and (X + 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X + 1, Y))
                                playagain = True

                        if not playagain:
                            self.turn += 1
                            if self.turn == self.num_of_players:
                                self.turn = 0
        Dot_Game.Draw_Game(self)

    def exit(self):
        os.rename("saves/dotgame.json","saves/old saves/dotgame.json")

    def save_exit(self):
        game = {}
        game["turn"] = self.turn
        game["size"] = (self.X,self.Y)
        game["players"] = {}
        for player in self.players:
            game["players"][player] = {}
            game["players"][player]["score"] = self.scores[player]
            game["players"][player]["color"] = self.colors[player]
            game["players"][player]["moves"] = self.moves[player]
            game["players"][player]["squares"] = self.squares[player]
        with open("saves/dotgame.json", "w") as old_game:
            old_game.write(json.dumps(game))
