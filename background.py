import random
import time

import pygame

def new_background(background,current_w,current_h):
    background.fill((0, 0, 0))
    rbg = random.randrange(2)
    if rbg == 0:
        bg = dots_background(background,current_w,current_h,random.randrange(30, 300))
    else:
        bg = Snake_background(background, current_w, current_h, random.randrange(30, 300))
    return bg

class dots_background:
    def  __init__(self,display,current_w,current_h,length):
        self.lines = []
        self.current_w = current_w
        self.current_h = current_h
        self.display = display
        self.scale = 50
        self.half = 25
        self.turn = 0
        self.playagain  = False
        self.length = time.perf_counter() + length
        self.players = ["p1","p2","p3","p4","p5","p6"]
        self.colors = {"p1":(132, 204, 106),"p2":(86, 167, 191),"p3":(151, 104, 173),"p4":(247, 237, 141),"p5":(110, 97, 69),"p6":(77, 21, 37)}
        self.moves = {"p1":[],"p2":[],"p3":[],"p4":[],"p5":[],"p6":[]}
        self.squares = {"p1":[],"p2":[],"p3":[],"p4":[],"p5":[],"p6":[]}
        self.speed = time.perf_counter()

        width = int(self.current_w / 25)+2
        height = int(self.current_h / 25)+2
        for x in range(width+1):
            x = x * 50 + 25
            for y in range(height+1):
                y = y * 50 + 25
                pygame.draw.circle(self.display,(128,128,128),(x+5, y-5), 5)

    def update(self):
        if time.perf_counter() > self.length:
            return Snake_background(self.display,self.current_w,self.current_h, random.randrange(30, 300))
        if time.perf_counter() > self.speed:
            self.speed = time.perf_counter() + 0.05
            width = int(self.current_w / 25)+2
            height = int(self.current_h / 25)+2
            x = random.randrange(0, width)
            x = x * 25
            y = random.randrange(0, height)
            y = y * 25
            if x % 10 != 0 or y % 10 != 0:
                if (x,y) not in self.lines:
                    self.lines.append((x,y))
                    self.turn += 1
                    playagain = False
                    X = int(round(x / self.half))
                    Y = int(round(y / self.half))
                    x, y = X * self.half, Y * self.half
                    playagain = False
                    current_color = self.colors[self.players[self.turn]]
                    if (X, Y) not in self.lines:
                        self.lines.append((X, Y))
                        self.moves[self.players[self.turn]].append((X, Y))
                        if X % 2 == 0:
                            if (X - 1, Y - 1) in self.lines and (X, Y - 2) in self.lines and (X + 1, Y - 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X, Y - 1))
                                playagain = True

                            if (X - 1, Y + 1) in self.lines and (X, Y + 2) in self.lines and (X + 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X, Y + 1))
                                playagain = True

                        if Y % 2 == 0:
                            if (X - 1, Y - 1) in self.lines and (X - 2, Y) in self.lines and (X - 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X - 1, Y))
                                playagain = True

                            if (X + 1, Y - 1) in self.lines and (X + 2, Y) in self.lines and (X + 1, Y + 1) in self.lines:
                                self.squares[self.players[self.turn]].append((X + 1, Y))
                                playagain = True

                        if playagain:
                            self.turn -= 1
                        if self.turn == 5:
                            self.turn = 0
                        if self.turn < 0:
                            self.turn = 5
        dots_background.Draw_Game(self)
        return self

    def Draw_Game(self):
        width = int(self.current_w / 25)+2
        height = int(self.current_h / 25)+2
        _2 = self.scale/25
        _4 = self.scale/12.5
        _23 = self.half - self.scale/25
        _46 = self.scale - self.scale/12.5
        for player in self.players:
            current_color = self.colors[player]
            for line in self.moves[player]:
                X,Y = line
                x, y = X * self.half, Y * self.half
                if X % 2 == 0:
                    pygame.draw.rect(self.display, current_color, ((x - self.half+5, y - _2-5), (self.scale, _4))) # draw horizontally
                if Y % 2 == 0:
                    pygame.draw.rect(self.display, current_color, ((x - _2+5, y - self.half-5), (_4, self.scale))) # draw vertically
            for square in self.squares[player]:
                X, Y = square
                x, y = X * self.half, Y * self.half
                pygame.draw.rect(self.display, current_color, ((x - _23+5, y - _23-5), (_46, _46))) # draw Square down


        for x in range(width):
            x = x * self.scale + self.half
            for y in range(height):
                y = y * self.scale + self.half
                pygame.draw.circle(self.display, (128, 128, 128), (x+5, y-5), self.scale/10)



    def reset(self):
        self.display.fill((0,0,0))
        self.lines = []
        self.length = time.perf_counter()+60
        width = int(self.current_w / 25)+2
        height = int(self.current_h / 25)+2
        for x in range(width+1):
            x = x * 50 + 25
            for y in range(height+1):
                y = y * 50 + 25
                pygame.draw.circle(self.display,(128,128,128),(x+5, y-5), 5)


class Snake_background:
    def __init__(self,display,current_w,current_h,length):
        number_of_snakes = 10
        self.current_w = current_w
        self.current_h = current_h
        self.display = display
        self.length = time.perf_counter() + length
        self.difficulty = time.perf_counter()
        self.last_direction = 0
        x,y = int(current_w/64),int(current_h/64)
        snake = [(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y),(x,y)]
        self.snakes  = []
        width = int((current_w / 32)/(number_of_snakes+1))
        for i in range(number_of_snakes):
            i += 1
            self.snakes.append([(i*width,y),(i*width,y),(i*width,y)])


        self.grid = (int(self.current_w/32),int(self.current_h/32))
        gx, gy = self.grid
        ax = random.randrange(0, gx - 1)
        ay = random.randrange(0, gy - 1)
        self.apples = []
        all_snakes = []
        for snake in self.snakes:
            for each in snake:
                all_snakes.append(each)

        for i in range(number_of_snakes):
            apple = (random.randrange(0, gx - 1),random.randrange(0, gy - 1))
            tries = 0
            while apple in all_snakes and tries < 5:
                apple = (random.randrange(0, gx - 1), random.randrange(0, gy - 1))
                tries += 1
            self.apples.append(apple)


    def update(self):
        scale = 32
        if time.perf_counter() > self.length:
            return dots_background(self.display,self.current_w,self.current_h,random.randrange(30, 300))
        snake_num = 0
        all_snakes = []
        for snake in self.snakes:
            all_snakes += snake
        update = False
        if time.perf_counter() > self.difficulty:
            self.difficulty = time.perf_counter() + 0.1
            update = True

        for snake in self.snakes:
            coff = 16*len(snake)
            if coff > 255:
                coff = 255
            color = (coff,255-coff,0)
            Dead = False
            if update:
                head = Snake_background.move(self, snake, all_snakes)
                if head in all_snakes:
                    Dead = True
                else:
                    all_snakes.append(head)
                if not Dead:
                    snake.append(head)
                    snake.pop(0)

            if not Dead:
                for each in snake[1:-1]:
                    sx, sy = each
                    pygame.draw.rect(self.display, color, (sx*32,sy*32, scale, scale))

                tx, ty = snake[0]
                bx, by = snake[1]
                tail_dir = tx - bx, ty - by
                tx = tx * scale
                ty = ty * scale
                if tail_dir == (-1, 0):  # right
                    pygame.draw.rect(self.display, color, (tx + 16,ty, 16, 32))
                if tail_dir == (0, -1):  # down
                    pygame.draw.rect(self.display, color, (tx,ty + 16, 32, 16))
                if tail_dir == (1, 0):  # left
                    pygame.draw.rect(self.display, color, (tx, ty, 16, 32))
                if tail_dir == (0, 1):  # up
                    pygame.draw.rect(self.display, color, (tx,ty, 32, 16))
                pygame.draw.circle(self.display, color, (16 + tx,16 + ty), 16)

                sx, sy = snake[-1]
                sx2, sy2 = snake[-2]
                head_dir = sx - sx2, sy - sy2
                sx = sx * scale
                sy = sy * scale
                if head_dir == (0, -1): #left
                    eyes = ((6, 10), (26, 10))
                    pygame.draw.rect(self.display, color, (sx, sy + 16, 32, 16))
                elif head_dir == (-1, 0): #right
                    eyes = ((10, 26), (10, 6))
                    pygame.draw.rect(self.display, color, (sx + 16, sy, 16, 32))
                elif head_dir == (0, 1): #down
                    eyes = ((26, 22), (6, 22))
                    pygame.draw.rect(self.display, color, (sx, sy, 32, 16))
                elif head_dir == (1, 0): #up
                    eyes = ((22, 6), (22, 26))
                    pygame.draw.rect(self.display, color, (sx, sy, 16, 32))
                else:
                    eyes = ((0,0), (0,0))
                    pygame.draw.rect(self.display, color, (sx, sy, 16, 32))
                left_eye, right_eye = eyes

                lex, ley = left_eye
                rex, rey = right_eye

                lex = lex + sx
                ley = ley + sy
                rex = rex + sx
                rey = rey + sy
                pygame.draw.circle(self.display, color, (16 + sx,16 + sy), 16)
                pygame.draw.circle(self.display, (0, 0, 0), (lex,ley), 3)
                pygame.draw.circle(self.display, (0, 0, 0), (rex,rey), 3)

                if snake[-1] in snake[0:-2]:
                    x, y = self.current_w / 64, self.current_h / 64
                    snake = [(x, y), (x, y), (x, y), (x, y), (x, y), (x, y)]

                if snake[-1] in self.apples:
                    i = self.apples.index(snake[-1])
                    gx, gy = self.grid
                    apple = (random.randrange(0, gx - 1), random.randrange(0, gy - 1))
                    tries = 0
                    while apple in all_snakes and tries < 5:
                        apple = (random.randrange(0, gx - 1), random.randrange(0, gy - 1))
                        tries += 1
                    self.apples[i] = (apple)
                    snake.append(snake[-1])
                self.snakes[snake_num] = snake
            else:
                gx, gy = self.grid
                self.snakes[snake_num] = [(int(gx/2),int(gy/2)),(int(gx/2),int(gy/2)),(int(gx/2),int(gy/2))]
            snake_num += 1

        for apple in self.apples:
            ax, ay = apple
            ax = ax * scale
            ay = ay * scale
            pygame.draw.rect(self.display, (128, 70, 27,0), (ax + 14, ay + 2, 4, 8))
            pygame.draw.circle(self.display, (0, 200, 0,0), (ax + 20, ay + 10), 6)
            pygame.draw.circle(self.display, (255, 0, 0,0), (ax + 12, ay + 17), 10)
            pygame.draw.circle(self.display, (255, 0, 0,0), (ax + 20, ay + 17), 10)
            pygame.draw.circle(self.display, (255, 0, 0,0), (ax + 12, ay + 22), 8)
            pygame.draw.circle(self.display, (255, 0, 0,0), (ax + 20, ay + 22), 8)
        return self


    def move(self,snake,all_snakes):
        x, y = self.grid
        near_apple = False
        cx = 10+len(snake)
        cy = 10+len(snake)
        hx, hy = snake[-1]
        next_move = ["left","right","down","up"]
        if (hx + 1,hy) in all_snakes:
            next_move.remove("right")
        if (hx - 1,hy) in all_snakes:
            next_move.remove("left")
        if (hx,hy + 1) in all_snakes:
            next_move.remove("down")
        if (hx,hy - 1) in all_snakes:
            next_move.remove("up")

        if len(next_move) == 0:
            return snake[-1]
        direction = random.choice(next_move)
        for apple in self.apples:
            ax,ay = apple
            if abs(hx-ax) <= abs(cx) and abs(hy - ay) <= abs(cy):
                cx = hx-ax
                cy = hy-ay
                nearest_apple = apple
                near_apple = True
        if near_apple:
            ax, ay = nearest_apple
            if abs(ax - hx) - abs(ay - hy) > 0:
                if hx - ax > 0:
                    if "left" in next_move:
                        direction = "left"
                else:
                    if "right" in next_move:
                        direction = "right"
            else:
                if hy - ay > 0:
                    if "up" in next_move:
                        direction = "up"
                else:
                    if "down" in next_move:
                        direction = "down"
        if direction == self.last_direction:
            direction = random.choice(next_move)
            if direction == self.last_direction:
                direction = self.last_direction
            else:
                self.last_direction = direction
        else:
            self.last_direction = direction

        if direction == "up":
            hy -= 1
        if direction == "down":
            hy += 1
        if direction == "right":
            hx += 1
        if direction == "left":
            hx -= 1

        if 0 > hx:
            hx = x
        if hx > x:
            hx = 0
        if 0 > hy:
            hy = y
        if hy > y:
            hy = 0

        return (int(hx),int(hy))

    def reset(self):
        self.display.fill((0,0,0))
        self.length = time.perf_counter()+60