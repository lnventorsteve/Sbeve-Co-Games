import os
import time
import pygame
import json
import my_gui as gui
import math
import random
import background


def get_player_names(Players):
    names = []
    for player in Players:
        names.append(player.name)
    return names

class Game_of_Life:
    def __init__(self,theme,Input,Players):
        self.theme = theme
        self.screen = theme.screen_info()[0]
        self.scale = 32
        self.Input = Input
        self.Players = Players
        self.ac = {}
        self.setup_ = True
        self.grid = True
        self.X = int(theme.screen_info()[1][0] / (self.scale/2))
        self.Y = int(theme.screen_info()[1][1] / (self.scale/2))
        self.offx = 0
        self.offy = 0
        self.setup_ = True
        self.paused = True
        self.around = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

    def update(self):

        self.scale -= self.Input.scroll()
        if self.scale < 1:
            self.scale = 1
        self.X = int(self.theme.screen_info()[1][0] / (self.scale/2))
        self.Y = int(self.theme.screen_info()[1][1] / (self.scale/2))

        for key in self.Input.Keys_pressed:
            if key == 119 or key == 1073741906:
                self.offy += 1
            elif key == 97 or key == 1073741904:
                self.offx += 1
            elif key == 115 or key == 1073741905:
                self.offy -= 1
            elif key == 100 or key == 1073741903:
                self.offx -= 1
        for key in self.Input.keys:
            if key == 103:
                self.grid = not self.grid
            if key == 32:
                self.paused = True
                self.updatecells()
            if key == 112:
                self.paused = not self.paused
            if key == 114:
                self.paused = True
                self.ac = {}


        x, y, mb = self.Input.mouse()
        if mb == 1:
            self.paused = True
            self.Input.clicked()
            x = int(x/self.scale) - self.offx - int(self.X/2)
            y = int(y/self.scale) - self.offy - int(self.Y/2)
            if (x, y) in self.ac:
                if self.ac[(x, y)] & 1 == 1:
                    self.removeCell((x, y))
                else:
                    self.addCell((x, y))
            else:
                self.addCell((x, y))


        if not self.paused:
            self.updatecells()
        self.updatescreen()



    def settings(self):
        if gui.button(self.theme, (0, 50), (100, 20), "Exit Game", self.Input):
            return "exit"
        return False

    def exit(self):
        pass

    def removeCell(self,cell):
        x, y = cell
        self.ac[(x, y)] -= 1
        neighbors = self.ac[(x, y)]
        neighbors >>= 1
        if neighbors <= 0:
            self.ac.pop(x, y)
        for axay in self.around:
            ax, ay = axay
            if (x + ax, y + ay) in self.ac:
                neighbors = self.ac[(x + ax, y + ay)]
                neighbors >>= 1
                if neighbors > 0:
                    self.ac[(x + ax, y + ay)] -= 2
                else:
                    self.ac.pop(x + ax, y + ay)

    def addCell(self,cell):
        if cell in self.ac:
            self.ac[cell] += 1
        else:
            self.ac[cell] = 1
        x, y = cell
        for axay in self.around:
            ax, ay = axay
            if (x + ax, y + ay) in self.ac:
                self.ac[(x + ax, y + ay)] += 2
            else:
                self.ac[(x + ax, y + ay)] = 2

    def updatecells(self):
        acc = {}
        acc = self.ac.copy()
        for cell in acc:
            neighbors = acc[cell]
            neighbors >>= 1
            if acc[cell] & 1 == 1:
                if neighbors != 2 and neighbors != 3:
                    self.ac[cell] -= 1
                    neighbors = self.ac[cell]
                    neighbors >>= 1
                    if neighbors <= 0:
                        self.ac.pop(cell)
                    x, y = cell
                    for axay in self.around:
                        ax, ay = axay
                        if (x + ax, y + ay) in self.ac:
                            neighbors = self.ac[(x + ax, y + ay)]
                            neighbors >>= 1
                            if neighbors > 0:
                                self.ac[(x + ax, y + ay)] -= 2
                            else:
                                self.ac.pop(x + ax, y + ay)
            else:
                if neighbors == 3:
                    self.ac[cell] += 1
                    x, y = cell
                    for axay in self.around:
                        ax, ay = axay
                        if (x + ax, y + ay) in self.ac:
                            self.ac[(x + ax, y + ay)] += 2
                        else:
                            self.ac[(x + ax, y + ay)] = 2

    def updatescreen(self):
        sx = self.X
        sy = self.Y
        for cell in self.ac:
            x, y = cell
            if -sx <= x + self.offx < sx and -sy <= y + self.offy < sy:
                if self.ac[cell] & 1 == 1:
                    pygame.draw.rect(self.screen, (255, 255, 255), ((x + round(self.X / 2) + self.offx) * self.scale, (y + round(self.Y / 2) + self.offy) * self.scale, self.scale, self.scale))

        if self.grid:
            cellx = 1
            celly = 1

            while cellx <= self.X:
                pygame.draw.line(self.screen, (55, 55, 55), (cellx * self.scale, 0), (cellx * self.scale, self.Y * self.scale), 1)
                cellx += 1

            while celly <= self.Y:
                pygame.draw.line(self.screen, (55, 55, 55), (0, celly * self.scale - 1), (self.X * self.scale - 1, celly * self.scale - 1), 1)
                celly += 1

    def gon(self):
        cellx = 1
        celly = 1
        while cellx <= X:
            pygame.draw.line(self.screen, (55, 55, 55), (cellx * self.scale, 0), (cellx * self.scale, self.Y * self.scale), 1)
            cellx += 1

        while celly <= Y:
            pygame.draw.line(self.screen, (55, 55, 55), (0, celly * self.scale - 1), (self.X * self.scale - 1, celly * self.scale - 1), 1)
            celly += 1

    def random(self):
        self.ac = {}
        for x in range(self.X):
            for y in range(self.Y):
                if randrange(0, 3) == 1:
                    self.addCell((int(x - X / 2), int(y - Y / 2)))

class Dot_Game:
    def __init__(self,theme,Input,Players):
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

    def setup(self):
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

class Snake:
    def __init__(self,theme,Input,Players):
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

        self.scaleSettings = gui.lable_text(self.theme, (0, -75), (100, 20), "Scale", self.snake_scale)
        self.difficulty_gui = gui.multiple_choice_input(self.theme,(0,-25),(100,20),"Difficulty","Normal",["Easy++","Easy+","Easy","Normal","Hard","Expert","God"],5,pointer=1)
        self.width = gui.Text_Box(self.theme,(-25,-50),(47.5,20),"Width",default_text="Width")
        self.height = gui.Text_Box(self.theme,(25,-50),(47.5,20),"Height",default_text="Height")
        self.grid = gui.multiple_choice_input(self.theme,(0,0),(100,20),"Grid","On",["On","Off"],2)
        self.bg = background.Snake_background(self.display,self.screen[0]*2,self.screen[1]*2,600)

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
        pygame.draw.circle(self.display, self.player.color2, (self.screenx + lex, self.screeny + ley), 3*self.apple_scale)
        pygame.draw.circle(self.display, self.player.color2, (self.screenx + rex, self.screeny + rey), 3*self.apple_scale)

    def move_snake(self):
        self.old_snake = self.snake[0]
        hx, hy = self.snake[-1]
        if self.direction == "up":
            hy -= 1
        if self.direction == "down":
            hy += 1
        if self.direction == "left":
            hx += 1
        if self.direction == "right":
            hx -= 1

        self.snake.append((hx, hy))
        self.snake.pop(0)

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
        hx, hy = self.snake[-1]
        if 0 > hx:
            self.dead = True
        elif hx > self.gx:
            self.dead = True
        elif 0 > hy:
            self.dead = True
        elif hy > self.gy:
            self.dead = True
        elif self.snake[-1] in self.snake[0:-2]:
            self.dead = True

        if self.dead:
            self.snake.pop()
            self.snake.insert(0,self.old_snake)

    def score(self):
        gui.lable_value(self.theme, (0,-(self.gy/2)*(self.snake_scale/self.scale)), "score = ", (len(self.snake) - 3),in_box=True,size=(((self.gx+1)*self.snake_scale)/self.scale,self.snake_scale/self.scale))
        if len(self.snake) - 3 > self.player.highScores["snake"][f"{self.grid_size[0]+1} by {self.grid_size[1]+1} on {self.d_text}"]:
            self.player.highScores["snake"][f"{self.grid_size[0]+1} by {self.grid_size[1]+1} on {self.d_text}"] = len(self.snake) - 3

    def draw_grid(self):
        if self.grid_state:
            for x in range(self.gx+2):
                x + 1
                pygame.draw.line(self.display, (128, 128, 128),(self.screenx+x*self.snake_scale,self.screeny + self.snake_scale),(self.screenx+x*self.snake_scale,self.screeny+(self.gy+1)*self.snake_scale + self.snake_scale))
            for y in range(self.gy+2):
                pygame.draw.line(self.display, (128, 128, 128),(self.screenx,self.screeny+y*self.snake_scale + self.snake_scale),(self.screenx+(self.gx+1)*self.snake_scale,self.screeny+y*self.snake_scale + self.snake_scale))
        else:
            x=0
            pygame.draw.line(self.display, (128, 128, 128),(self.screenx+x*self.snake_scale,self.screeny + self.snake_scale),(self.screenx+x*self.snake_scale,self.screeny+(self.gy+1)*self.snake_scale + self.snake_scale))
            x= self.gx+1
            pygame.draw.line(self.display, (128, 128, 128),(self.screenx+x*self.snake_scale,self.screeny + self.snake_scale),(self.screenx+x*self.snake_scale,self.screeny+(self.gy+1)*self.snake_scale + self.snake_scale))
            y= 0
            pygame.draw.line(self.display, (128, 128, 128),(self.screenx,self.screeny+y*self.snake_scale + self.snake_scale),(self.screenx+(self.gx+1)*self.snake_scale,self.screeny+y*self.snake_scale + self.snake_scale))
            y=self.gy+1
            pygame.draw.line(self.display, (128, 128, 128),(self.screenx,self.screeny+y*self.snake_scale + self.snake_scale),(self.screenx+(self.gx+1)*self.snake_scale,self.screeny+y*self.snake_scale + self.snake_scale))


    def setup(self):
        self.bg.update()
        gui.lable(self.theme, (0, -self.screen[1] / self.scale + 75), "Snake", in_box=True, size=(150, 20))
        self.difficulty_gui.update(self.Input)
        gui.text(self.theme, (-120, -50), "Grid Size", in_box=True, size=(100, 20))
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

    def settings(self):
        self.scaleSettings.update(self.Input)
        if gui.button(self.theme, (0, 25), (100, 20), "Apply", self.Input):
            if self.scaleSettings.text.isnumeric():
                self.snake_scale = int(self.scaleSettings.text)
                self.apple_scale = self.snake_scale/32
                self.screenx = self.screen[0] - (self.gx+1)/2*self.snake_scale
                self.screeny = self.screen[1] - (self.gy+1)/2*self.snake_scale
                return "back"

        if gui.button(self.theme, (0, 50), (100, 20), "Return to Game", self.Input):
            return "back"

        if gui.button(self.theme, (0, 75), (100, 20), "Exit Game", self.Input):
            self.player.save_player()
            return "exit"

    def update(self):
        self.frame_time = (time.perf_counter() - self.last_frame)
        self.player.playTime["snake"] += self.frame_time
        self.last_frame = time.perf_counter()
        for key in self.Input.keys:
            if key == 114:
                self.snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
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

        if time.perf_counter() >= self.next_frame and not self.dead:
            self.next_frame = time.perf_counter() + self.difficulty
            if len(self.inputs) > 1:
                self.inputs.pop(0)
            self.direction = self.inputs[0]
            self.move_snake()
            self.death()
            if self.snake[-1] == self.apple:
                self.snake.insert(0, self.snake[0])
                self.make_apple()
        if self.apple == (-1,-1):
            self.make_apple()
        else:
            self.draw_apple()
        self.draw_grid()
        self.draw_snake()
        self.draw_head()
        self.draw_tail()
        self.score()

    def save_exit(self):
        game = {}
        game["snake"] = self.snake
        game["apple"] = self.apple
        game["size"] = (self.gx,self.gy)
        game["scale"] = self.snake_scale
        game["difficulty"] = self.difficulty
        with open("saves/snake.json", "w") as old_game:
            old_game.write(json.dumps(game))

    def load(self):
        self.setup_ = True
        with open("saves/dotgame.json", "r") as old_game:
            game = json.loads(old_game.read())
            self.snake = game["snake"]
            self.apple = game["apple"]
            self.grid_size = game["size"]
            self.snake_scale = game["scale"]
            self.difficulty = game["difficulty"]

        self.gx, self.gy = self.grid_size
        self.grid = self.grid_size

        if f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1}" not in self.player.highScores["snake"]:
            self.player.highScores["snake"][f"{self.grid_size[0] + 1} by {self.grid_size[1] + 1} on {self.d_text}"] = 0

        self.screenx = self.screen[0] - (self.gx + 1) / 2 * self.snake_scale
        self.screeny = self.screen[1] - (self.gy + 1) / 2 * self.snake_scale
        self.snake = [(0, int(self.gy / 2)), (0, int(self.gy / 2)), (1, int(self.gy / 2))]
        self.input_direction = "left"
        self.inputs = ["left"]
        self.last_direction = "left"
        self.make_apple()

class cookie_clicker:
    def __init__(self,theme,Input,player):
        self.setup_ = True
        self.theme = theme
        self.Input = Input
        self.player = player.name
        self.sw,self.sh = theme.screen
        self.sw = self.sw/theme.scale
        self.sh = self.sh / theme.scale
        self.menu = "cookie"
        self.shop_mode = "buy"
        self.shop_amount = 1
        if self.player in os.listdir("saves/Cookie/"):
            with open("saves/Cookie/" + self.player+".json", "w") as cookie_file:
                self.cookie_info = cookie_file.read(json.loads(self.cookie_info))
        else:
            self.cookie_info = {"cookies":0,"buildings":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
            with open("saves/Cookie/"+self.player+".json","w") as cookie_file:
                cookie_file.write(json.dumps(self.cookie_info))
        self.building_info = [(15,0.1),(100,1),(1100,8),(12000,47),(130000,260),(1400000,1400),(20000000,7800),(330000000,44000),(5100000000,260000),(75000000000,1600000),
                              (1000000000000,10000000),(14000000000000,65000000),(170000000000000,430000000),(2100000000000000,2900000000),(26000000000000000,21000000000),(310000000000000000,150000000000)]


    def update(self):
        self.theme.display.fill((0,0,0))
        gui.lable(self.theme,(0,-self.sh+30),"Cookies")
        gui.lable(self.theme, (0,-self.sh+45), self.cookie_info["cookies"])
        pygame.draw.circle(self.theme.display,(100,65,25),(self.sw*self.theme.scale,self.sh*self.theme.scale),400)
        mx,my,mb = self.Input.mouse()
        if gui.button(self.theme,(-50,-self.sh+15),(70,20),"Cookie",self.Input):
            self.menu = "cookie"
        if gui.button(self.theme,(50,-self.sh+15),(70,20),"Buildings",self.Input):
            self.menu = "buildings"



        if self.menu == "cookie":
            mx -= self.sw*self.theme.scale
            my -= self.sh*self.theme.scale
            print(int(math.sqrt(mx * mx + my * my)))
            if int(math.sqrt(mx*mx+my*my)) < 400 and mb > 0:
                self.Input.clicked()
                self.cookie_info["cookies"] = self.cookie_info["cookies"] + 1
        elif self.menu == "buildings":
            color1,color10,color0 = self.theme.bgcolor
            if self.shop_amount == 1:
                r,g,b = self.theme.bgcolor
                if r - 16 < 0: r = 0
                else: r -= 16
                if g - 16 < 0: g = 0
                else: g -= 16
                if b - 16 < 0: b = 0
                else: b -= 16
                color1 = r, g, b
            if self.shop_amount == 10:
                r,g,b = self.theme.bgcolor
                if r - 16 < 0: r = 0
                else: r -= 16
                if g - 16 < 0: g = 0
                else: g -= 16
                if b - 16 < 0: b = 0
                else: b -= 16
                color10 = r, g, b
            if self.shop_amount == 0:
                r,g,b = self.theme.bgcolor
                if r - 16 < 0: r = 0
                else: r -= 16
                if g - 16 < 0: g = 0
                else: g -= 16
                if b - 16 < 0: b = 0
                else: b -= 16
                color0 = r, g, b
            gui.lable(self.theme,(100,300),"1",in_box=True,size=(50,20),background_color=color1)
            gui.lable(self.theme, (100, 300), "10", in_box=True, size=(50, 20), background_color=color10)
            gui.lable(self.theme, (100, 300), "Max", in_box=True, size=(50, 20), background_color=color0)

class bird:
    def __init__(self, theme, Input, players):
        self.setup_ = True
        self.theme = theme
        self.display = theme.display
        self.Input = Input
        self.player = players[0]
        if "bird" not in self.player.highScores:
            self.player.highScores["bird"] = 0
        self.pcolor = players[0].color1
        self.eyecolor = players[0].color2
        self.wingcolor = players[0].color3
        self.sw,self.sh = theme.screen
        self.pos = self.sh
        self.pos_x = self.sw/2
        self.vector1 = 0
        self.pipes = [(self.sw*2,(self.sh*2)/(random.randrange(20,80)/10))]
        self.alive = True
        self.jump = 15
        self.last_frame = time.perf_counter()
        self.frame_time = 0
        self.score = 0
        self.paused = True
        self.bglength = int(self.sw*6)
        self.background = pygame.transform.scale(pygame.image.load("images/mario.jpg"), (self.bglength,int(self.sh*4)))
        self.bgpos = 0
        self.stars= []
        self.stars_per_sec = 1/10
        self.start_time =  time.perf_counter()
        self.death_timer = 0

    def settings(self):
        self.paused = True
        if self.bgpos >=  -self.bglength:
            self.display.blit(self.background,(self.bgpos,-self.sh*2))
        if self.bgpos <= -self.bglength + self.sw:
            for each in self.stars:
                x, y = each
                pygame.draw.circle(self.display, (255, 255, 255), (x, y), 2)
        for pipe in self.pipes:
            bird.pipe(self,pipe)
        pygame.draw.circle(self.display,self.pcolor,(self.pos_x,self.pos),40)
        pygame.draw.circle(self.display, self.eyecolor, (self.pos_x+30, self.pos-10), 5)
        pygame.draw.circle(self.display, self.wingcolor , (self.pos_x-5, self.pos+5), 20)
        pygame.draw.circle(self.display, self.pcolor, (self.pos_x-5, self.pos+5), 14)
        gui.box(self.theme, (0, -(self.sh / self.theme.scale)+15),(200,30))
        gui.text(self.theme, (0, -(self.sh / self.theme.scale) + 7), f"High Score = {self.player.highScores['bird']}")
        gui.text(self.theme, (0, -(self.sh / self.theme.scale) + 22), f"Score = {self.score}")

        if gui.button(self.theme, (0, 25), (100, 20), "Return to Game", self.Input):
            return "back"
        if gui.button(self.theme,(0,50),(100,20),"Reset Game",self.Input):
            self.pos = self.sh
            self.pos_x = self.sw / 2
            self.pipes = [(self.sw * 2, (self.sh * 2) / (random.randrange(20, 80) / 10))]
            self.jump = 15
            self.score = 0
            self.alive = True
            self.vector1 = 0
            self.last_frame = time.perf_counter()
            self.frame_time = 0
            self.paused = True
            self.atpipe = False
            self.bgpos = 0
            return "back"

        if gui.button(self.theme, (0, 75), (100, 20), "Exit Game", self.Input):
            self.player.save_player()
            return "exit"

    def exit(self):
        pass

    def pipe(self,pos):
        x,y = pos
        sy = self.sh*2
        pygame.draw.rect(self.display, (0, 255, 0), (x, 0, 20, y))
        pygame.draw.rect(self.display, (0, 230, 0), (x+20, 0,40,y))
        pygame.draw.rect(self.display, (0, 180, 0), (x+60, 0, 10 , y))
        pygame.draw.rect(self.display, (0, 140, 0), (x + 70, 0, 10, y))
        pygame.draw.rect(self.display, (0, 0, 0), (x+ 76, 0, 4, y))
        pygame.draw.rect(self.display, (0, 0, 0), (x, 0, 4, y))
        pygame.draw.rect(self.display, (0, 0, 0), (x-20, y-40, 120, 40))
        pygame.draw.rect(self.display, (0, 255, 0), (x - 16, y - 36, 112, 6))
        pygame.draw.rect(self.display, (0, 200, 0), (x - 16, y - 30, 112, 26))
        y+=300
        pygame.draw.rect(self.display, (0, 255, 0), (x, y, 20, sy-y))
        pygame.draw.rect(self.display, (0, 230, 0), (x+20, y,40,sy-y))
        pygame.draw.rect(self.display, (0, 180, 0), (x+60, y, 10 , sy-y))
        pygame.draw.rect(self.display, (0, 140, 0), (x + 70, y, 10, sy-y))
        pygame.draw.rect(self.display, (0, 0, 0), (x+ 76, y, 4, sy-y))
        pygame.draw.rect(self.display, (0, 0, 0), (x, y, 4, sy-y))
        pygame.draw.rect(self.display, (0, 0, 0), (x-20, y-40, 120, 40))
        pygame.draw.rect(self.display, (0, 255, 0), (x - 16, y - 36, 112, 6))
        pygame.draw.rect(self.display, (0, 200, 0), (x - 16, y - 30, 112, 26))

    def update(self):
        self.frame_time = (time.perf_counter() - self.last_frame)*100
        self.last_frame = time.perf_counter()
        if self.bgpos >=  -self.bglength:
            self.display.blit(self.background,(self.bgpos,-self.sh*2))
        if self.bgpos <= -self.bglength + self.sw:
            new_stars = []
            for each in self.stars:
                x,y = each
                pygame.draw.circle(self.display, (255,255,255), (x,y), 2)
                new_stars.append((x - self.frame_time * 2,y))
            self.stars = new_stars

        for pipe in self.pipes:
            bird.pipe(self,pipe)

        if not self.paused:
            if self.bgpos <= -self.bglength + self.sw:
                if time.perf_counter() > self.start_time:
                    self.start_time = time.perf_counter()+self.stars_per_sec
                    self.stars.append((self.sw * 2, random.randrange(0, self.sh * 2)))

            pipes = []
            for pipe in self.pipes:
                if pipe[0] < self.pos_x < pipe[0]+120 :
                    self.atpipe = True
                    if self.pos-40 < pipe[1]:
                        self.alive = False
                    elif self.pos+40 > pipe[1]+300:
                        self.alive = False
                if pipe[0] < self.pos_x + 42 < pipe[0]+120 :
                    if self.pos < pipe[1] or self.pos > pipe[1]+300:
                        self.alive = False
                if self.alive:
                    if pipe[0]>-100:
                        pipes.append((pipe[0] - self.frame_time*5 , pipe[1]))
                if pipe[0]+120 < self.pos_x < pipe[0]+140 and self.atpipe:
                    self.atpipe = False
                    self.score += 1

            if self.alive:
                self.pipes = pipes
                self.bgpos -= 2

            if self.pipes[-1][0] < self.sw*1.5:
                self.pipes.append((self.sw*2,(self.sh*2)/(random.randrange(20,80)/10)))

            self.pos += self.vector1*(self.frame_time/2)
            self.vector1+= self.frame_time/2
        if not self.alive:
            self.paused = False
            if self.pos < self.sh*3:
                if self.jump > 0:
                    self.pos_x -= self.jump*(self.frame_time)
                    self.jump-=1*(self.frame_time/2)
            else:
                if self.score > self.player.highScores["bird"]:
                    self.player.highScores["bird"] = self.score
                gui.box(self.theme,(0,-5),(140,75))
                gui.text(self.theme, (0, -32.5), "Welp that's unfortunate.")
                if gui.button(self.theme, (0, -12.5), (100, 20), "Play Again", self.Input):
                    self.pos = self.sh
                    self.pos_x = self.sw / 2
                    self.pipes = [(self.sw * 2, (self.sh * 2) / (random.randrange(20, 80) / 10))]
                    self.jump = 15
                    self.score = 0
                    self.alive = True
                    self.vector1 = 0
                    self.last_frame = time.perf_counter()
                    self.frame_time = 0
                    self.paused = True
                    self.atpipe = False
                    self.bgpos = 0

                if gui.button(self.theme, (0, 12.5), (100, 20), "Exit Game", self.Input):
                    self.player.save_player()
                    return "exit"

        if self.alive:
            for key in self.Input.keys:
                if key == 32:
                    if self.paused == True:
                        self.paused = False
                    else:
                        self.vector1 = -15
                    if self.vector1 > 25:
                        self.vector1 = 25
        pygame.draw.circle(self.display,self.pcolor,(self.pos_x,self.pos),40)
        pygame.draw.circle(self.display, self.eyecolor, (self.pos_x+30, self.pos-10), 5)
        pygame.draw.circle(self.display, self.wingcolor , (self.pos_x-5, self.pos+5), 20)
        pygame.draw.circle(self.display, self.pcolor, (self.pos_x-5, self.pos+5), 14)
        gui.box(self.theme, (0, -(self.sh / self.theme.scale)+15),(200,30))
        gui.text(self.theme, (0, -(self.sh / self.theme.scale) + 7), f"High Score = {self.player.highScores['bird']}")
        gui.text(self.theme, (0, -(self.sh / self.theme.scale) + 22), f"Score = {self.score}")

class Connect_4:
    def __init__(self, theme, Input, Players):
        self.theme = theme
        self.display = theme.display
        self.Input = Input
        self.Players = Players
        self.setup_ = False
        self.player1 = gui.multiple_choice_input(theme, (0,0),(100,20),"Player 1", Players[0].name,get_player_names(Players),5)
        self.player2 =  gui.multiple_choice_input(theme, (0,25),(100,20),"Player 2", Players[1].name,get_player_names(Players),5)
        self.board = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.winner = 0
        self.win = 0
        self.turn = "player 1"
        self.color1 = (255, 0, 0)
        self.color2 = (255, 255, 0)
        self.scale = 1
        self.scale_ui = gui.slider(self.theme,(0, 0), (100, 20),"right",self.Input, value = self.scale/2)
        self.xoff = (self.theme.width - 910* self.scale) /2
        self.yoff = (self.theme.height - 780* self.scale) /2


    def load(self):
        pass

    def setup(self):
        self.player1.update(self.Input)
        self.player2.update(self.Input)
        if gui.button(self.theme, (0, 50), (100, 20), "Play", self.Input):
            self.setup_ = True
            self.next_frame = time.perf_counter()
            for player in self.Players:
                if player.name == self.player1.text:
                    self.color1 = player.color1
                if player.name == self.player2.text:
                    self.color2 = player.color2


    def settings(self):
        gui.text(self.theme, (0, -25), "Scale",in_box = True, size = (100, 20), )
        self.scale_ui.update()
        if gui.button(self.theme, (0, 25), (100, 20), "Save Changes", self.Input):
            self.scale = self.scale_ui.value*2
            self.xoff = (self.theme.width - 910 * self.scale) / 2
            self.yoff = (self.theme.height - 780 * self.scale) / 2
        if gui.button(self.theme, (0, 50), (100, 20), "Return to Game", self.Input):
            return "back"
        if gui.button(self.theme, (0, 75), (100, 20), "Exit Game", self.Input):
            return "exit"

    def update_screen(self):
        pygame.draw.rect(self.display, (0, 0, 130), (self.xoff-10, self.yoff-10, 910 * self.scale+20, 780 * self.scale+20))
        pygame.draw.rect(self.display,(0,0,180),(self.xoff,self.yoff,910 * self.scale,780 * self.scale))
        if self.winner != 0:
            self.board = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
            for piece in self.winning_pieces:
                column, row = piece
                self.board[column][row] = self.winner

        board_x = -1
        for column in self.board:
            board_x += 1
            board_y = 0
            for row in column:
                board_y += 1
                x = board_x * 130 * self.scale + 65 * self.scale + self.xoff
                y = board_y * 130 * self.scale - 65 * self.scale + self.yoff
                if row == 0:
                    pygame.draw.circle(self.display, (0, 0, 130), (x, y), 60*self.scale)
                    pygame.draw.circle(self.display, (255, 255, 255), (x, y), 50*self.scale)
                if row == 1:
                    pygame.draw.circle(self.display, (0, 0, 130), (x, y), 60*self.scale)
                    pygame.draw.circle(self.display, self.color1, (x, y), 50*self.scale)
                if row == 2:
                    pygame.draw.circle(self.display, (0, 0, 130), (x, y), 60*self.scale)
                    pygame.draw.circle(self.display, self.color2, (x, y), 50*self.scale)



    def update(self):
        if time.perf_counter() >= self.next_frame and self.winner == 0:
            self.next_frame = time.perf_counter() + 0.1
            for column in self.board:
                for row in range(5):
                    if column[5 - row] == 0:
                        column[5 - row] = column[4 - row]
                        column[4 - row] = 0
            self.win += 1

        if 114 in self.Input.keys:
            self.board = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
            self.winner = 0
            self.win = 0
            self.turn = "player 1"

        if self.winner == 0 and self.win > 6:
            mouse_x, mouse_y, mb = self.Input.mouse()
            mouse_x-=self.xoff
            if mb == 1:
                self.win = 0
                self.Input.clicked()
                if mouse_x > 0 and  mouse_x < 910* self.scale:
                    print(mouse_x)
                    mouse_x = round((mouse_x / (130* self.scale)) - 0.5)
                    print(mouse_x)
                    if self.turn == "player 1" and self.board[mouse_x][0] == 0 :
                        self.board[mouse_x][0] = 1
                        self.turn = "player 2"
                    if self.turn == "player 2" and self.board[mouse_x][0] == 0 :
                        self.board[mouse_x][0] = 2
                        self.turn = "player 1"





        if self.win == 6:
            self.winner = 0
            self.winning_pieces = []
            for column in range(3):
                for check in range(6):
                    if self.board[column][check] == 1 and self.board[column + 1][check] == 1 and self.board[column + 2][check] == 1 and \
                            self.board[column + 3][check] == 1:
                        self.winning_pieces = [(column, check), (column + 1, check), (column + 2, check),
                                          (column + 3, check)]
                        self.winner = 1
                        print("player 1 won")
                    if self.board[column][check] == 2 and self.board[column + 1][check] == 2 and self.board[column + 2][check] == 2 and \
                            self.board[column + 3][check] == 2:
                        self.winning_pieces = [(column, check), (column + 1, check), (column + 2, check),
                                          (column + 3, check)]
                        self.winner = 2
                        print("player 2 won")
            for column in range(6):
                for row in range(3):
                    if self.board[column][row] == 1 and self.board[column][row + 1] == 1 and self.board[column][row + 2] == 1 and \
                            self.board[column][row + 3] == 1:
                        self.winning_pieces = [(column, row), (column, row + 1), (column, row + 2), (column, row + 3)]
                        self.winner = 1
                        print("player 1 won")
                    if self.board[column][row] == 2 and self.board[column][row + 1] == 2 and self.board[column][row + 2] == 2 and \
                            self.board[column][row + 3] == 2:
                        self.winning_pieces = [(column, row), (column, row + 1), (column, row + 2), (column, row + 3)]
                        self.winner = 2
                        print("player 2 won")
            for column in range(4):
                for check in range(3):
                    if self.board[column][check] == 1 and self.board[column + 1][check + 1] == 1 and self.board[column + 2][
                        check + 2] == 1 and self.board[column + 3][check + 3] == 1:
                        self.winning_pieces = [(column, check), (column + 1, check + 1), (column + 2, check + 2),
                                          (column + 3, check + 3)]
                        self.winner = 1
                        print("player 1 won")
                    if self.board[column][check] == 2 and self.board[column + 1][check + 1] == 2 and self.board[column + 2][
                        check + 2] == 2 and self.board[column + 3][check + 3] == 2:
                        self.winning_pieces = [(column, check), (column + 1, check + 1), (column + 2, check + 2),
                                          (column + 3, check + 3)]
                        self.winner = 2
                        print("player 2 won")
            for column in range(4):
                for check in range(3):
                    if self.board[column][check + 3] == 1 and self.board[column + 1][check + 2] == 1 and self.board[column + 2][
                        check + 1] == 1 and self.board[column + 3][check] == 1:
                        self.winning_pieces = [(column, check + 3), (column + 1, check + 2), (column + 2, check + 1),
                                          (column + 3, check)]
                        self.winner = 1
                        print("player 1 won")
                    if self.board[column][check + 3] == 2 and self.board[column + 1][check + 2] == 2 and self.board[column + 2][
                        check + 1] == 2 and self.board[column + 3][check] == 2:
                        self.winning_pieces = [(column, check + 3), (column + 1, check + 2), (column + 2, check + 1),
                                          (column + 3, check)]
                        self.winner = 2
                        print("player 2 won")


        self.update_screen()

    def save_exit(self):
        pass

    def exit(self):
        pass







class new_game:
    def init(self,theme,Players,Input):
        self.theme = theme
        self.display = theme.display
        self.Input = Input
        self.Players = Players
        self.setup_ = False

    def load(self):
        pass

    def setup(self):
        if gui.button(self.theme, (0, 50), (100, 20), "Play", self.Input):
            self.setup_ = True

    def settings(self):
        pass

    def update(self):
        pass

    def save_exit(self):
        pass

    def exit(self):
        if gui.button(self.theme, (0, 75), (100, 20), "Exit Game", self.Input):
            return "exit"


if __name__ == "__main__":
    pygame.init()
    with open("conf.json", "r") as conf:
        config = json.loads(conf.read())

    scale = config["scale"]
    zoom = config["zoom"]
    current_w, current_h = config["screen size"]
    fullscreen = config["mode"]
    main_display = config["main_display"]

    display_info = pygame.display.Info()
    print(current_w, current_h)
    display = pygame.display.set_mode((current_w, current_h),display=0)
    pygame.display.set_caption("Sbeve's Random Games")
    game = dot_game(display,current_w,current_h)

    mousedown = False
    cursor = False
    c_time  = time.perf_counter()
    done = False
    while not done:
        mouse = (0, 0, 0)
        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        if event.type == pygame.MOUSEBUTTONDOWN:

            if not mousedown:
                mx, my = pygame.mouse.get_pos()
                mouse = (mx, my, event.button)
                mousedown = True
                in_text = False
                print(mouse)


        if event.type == pygame.MOUSEBUTTONUP and mousedown:
            mousedown = False
        if event.type == pygame.KEYDOWN:
            key = event
            if event.key == 27:
                done = True

        if time.perf_counter() >= c_time:
            c_time = time.perf_counter()+0.5
            cursor = not cursor
            if cursor:
                c = "_"
            else:
                c = ""

        update(game, key, mouse, cursor)

        pygame.display.update()
