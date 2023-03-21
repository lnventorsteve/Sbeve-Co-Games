import json
import math
import os
import time
import pygame
import win32clipboard

pygame.init()
default_font = pygame.font.SysFont(pygame.font.get_default_font(), 24)


#lookup tables
shift_table = {
32:32,
33:33,
34:34,
35:35,
36:36,
37:37,
38:38,
39:34,
40:40,
41:41,
42:42,
43:43,
44:44,
45:95,
46:46,
47:63,
48:41,
49:33,
50:64,
51:35,
52:36,
53:37,
54:94,
55:38,
56:42,
57:40,
58:58,
59:58,
60:60,
61:43,
62:62,
63:63,
64:64,
65:65,
66:66,
67:67,
68:68,
69:69,
70:70,
71:71,
72:72,
73:73,
74:74,
75:75,
76:76,
77:77,
78:78,
79:79,
80:80,
81:81,
82:82,
83:83,
84:84,
85:85,
86:86,
87:87,
88:88,
89:89,
90:90,
91:123,
92:124,
93:125,
94:126,
95:95,
96:126,
97:65,
98:66,
99:67,
100:68,
101:69,
102:70,
103:71,
104:72,
105:73,
106:74,
107:75,
108:76,
109:77,
110:78,
111:79,
112:80,
113:81,
114:82,
115:83,
116:84,
117:85,
118:86,
119:87,
120:88,
121:89,
122:90,
123:91,
124:92,
125:93,
126:126}

class Input:
    def __init__(self):
        self.Keys_pressed = {} # raw key info
        self.keys = [] # key info with filter for button input
        self.unicode = [] # key info with filter for text input
        self.cursor_state = False
        self.mouse_info = (0, 0, 0)
        self.mouse_button = 0
        self.mouse_position = (0,0)
        self.c_time = 0
        self.scroll_amount = 0
        self.mods = []
        self.CAPS = False

    def get_input(self,event,frame):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_button = event.button

        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_button = 0
            mb = event.button
            scroll = mb
            if mb > 7:
                if mb % 2 == 0:
                    scroll -= 3
                    self.scroll_amount = -scroll
                else:
                    scroll -= 7
                    self.scroll_amount = scroll
            else:
                if mb == 4:
                    self.scroll_amount = -1
                if mb == 5:
                    self.scroll_amount = 1
            self.mouse_info = (mx, my, 0)

        if event.type == pygame.KEYDOWN:
            key = event.key
            self.Keys_pressed[key] = [frame,time.perf_counter() + 0.5]
            if key > 1000000000:
                if key == 1073742049:
                    self.mods.append("SHIFT")
                elif key == 1073742048:
                    self.mods.append("CTRL")
                elif key == 1073742050:
                    self.mods.append("ALT")
                elif key == 1073742051:
                    self.mods.append("WIN")
                elif key == 1073742053:
                    self.mods.append("SHIFT")
                elif key == 1073742054:
                    self.mods.append("ALT")
                elif key == 1073742052:
                    self.mods.append("CTRL")
                elif key == 1073742881:
                    if "Caps" in self.mods:
                        self.mods.remove("Caps")
                    else:
                        self.mods.append("Caps")

        if event.type == pygame.KEYUP:
            key = event.key
            self.Keys_pressed.pop(key)

            if key > 1000000000:
                if key == 1073742049:
                    self.mods.remove("SHIFT")
                elif key == 1073742048:
                    self.mods.remove("CTRL")
                elif key == 1073742050:
                    self.mods.remove("ALT")
                elif key == 1073742051:
                    self.mods.remove("WIN")
                elif key == 1073742053:
                    self.mods.remove("SHIFT")
                elif key == 1073742054:
                    self.mods.remove("ALT")
                elif key == 1073742052:
                    self.mods.remove("CTRL")

    def update(self,frame):
        mx,my = self.mouse_position = pygame.mouse.get_pos()
        self.mouse_info = (mx,my,self.mouse_button)
        ct = time.perf_counter()
        self.keys = []
        for key in self.Keys_pressed:
            kf , kt = self.Keys_pressed[key]
            if kf == frame:
                self.keys.append(key)
            if ct > kt:
                self.keys.append(key)
                self.Keys_pressed[key] = [kf , kt+0.05]
        self.unicode = []
        for key in self.keys:
            if key in shift_table:
                if "SHIFT" in self.mods or "CAPS" in self.mods:
                    self.unicode.append(chr(shift_table[key]))
                else:
                    self.unicode.append(chr(key))


    def cursor(self):
        if time.perf_counter() >= self.c_time:
            self.c_time = time.perf_counter() + 0.5
            self.cursor_state = not self.cursor_state
        return self.cursor_state

    def Keys_pressedraw(self):
        return self.Keys_pressed

    def mouse(self):
        return self.mouse_info

    def clicked(self):
        self.mouse_button = -abs(self.mouse_button)
        mx, my = self.mouse_position
        self.mouse_info = (mx, my, self.mouse_button)
    def scroll(self):
        scroll_amount = self.scroll_amount
        self.scroll_amount = 0
        return scroll_amount

class Theme:
    def __init__(self,screen_info=(None,(0,0),0),font=default_font,font_size = 12,
            font_name = pygame.font.get_default_font(), text_color = (255,255,255),
            border_color = (128,128,128), background_color = (64,64,64)):
        self.display = screen_info[0]
        self.screen = screen_info[1]
        self.width = self.screen[0]*2
        self.height = self.screen[1]*2
        self.scale = screen_info[2]
        self.font_name = font_name
        self.font = font
        self.font_size = font_size
        self.Colors = {text_color,border_color,background_color}
        self.tcolor = text_color
        self.bcolor = border_color
        self.bgcolor = background_color
        self.Sounds = {}
        self.sound_info = {}
        self.border = 3
        self.path = str(os.path.dirname(__file__))

    def save_Theme(self):
        dict = {}
        dict["Colors"] = self.Colors
        dict["Sounds"] = self.sound_info
        dict["Fonts"] = {}
        dict["Fonts"][self.font_name] = self.font_size
        dict["Properties"]={}
        dict["Properties"]["Border Thickness"] = self.border

        return dict


    def load_Theme(self,config,Theme = False):
        if Theme == False:
            file = config["theme"]
        else:
            file = Theme

        with open(f"{self.path}/Themes/{file}.json", "r") as Theme:
            Theme = json.loads(Theme.read())
            Fonts = []
            for font in Theme["Fonts"]:
                Fonts.append(font)
            self.font = pygame.font.SysFont(Fonts[0], Theme["Fonts"][Fonts[0]] * config["scale"])
            self.font_size = Theme["Fonts"][Fonts[0]]
            self.font_name = Fonts[0]
            for sound in Theme["Sounds"]:
                self.Sounds[sound] = pygame.mixer.Sound(f"{self.path}/sounds/{Theme['Sounds'][sound]['name']}")
                self.Sounds[sound].set_volume(Theme["Sounds"][sound]["volume"])
            self.sound_info = Theme["Sounds"]
            self.Colors = Theme["Colors"]
            self.tcolor = Theme["Colors"]['Text color']
            self.bcolor = Theme["Colors"]['Border color']
            self.bgcolor = Theme["Colors"]['Background color']
            self.border = Theme["Properties"]["Border Thickness"]

    def change_Theme(self, new_theme):
        with open(f"{self.path}/Themes/{new_theme}.json", "r") as Theme:
            Theme = json.loads(Theme.read())
            Fonts = []
            for font in Theme["Fonts"]:
                Fonts.append(font)
            self.font = pygame.font.SysFont(Fonts[0], Theme["Fonts"][Fonts[0]] * self.scale)
            self.font_size = Theme["Fonts"][Fonts[0]]
            for sound in Theme["Sounds"]:
                self.Sounds[sound] = pygame.mixer.Sound(f"{self.path}/sounds/{Theme['Sounds'][sound]['name']}")
                self.Sounds[sound].set_volume(Theme["Sounds"][sound]["volume"])
            self.sound_info = Theme["Sounds"]
            self.Colors = Theme["Colors"]
            self.tcolor = Theme["Colors"]['Text color']
            self.bcolor = Theme["Colors"]['Border color']
            self.bgcolor = Theme["Colors"]['Background color']
            self.border = Theme["Properties"]["Border Thickness"]

    def fonts(self,font_name=False,font_size=False):
        if font_name != False:
            self.font_name = font_name
        if font_size != False:
            self.font_size = font_size

        if font_name != False or font_size != False:
            self.font = pygame.font.SysFont(self.font_name, self.font_size * self.scale)

        return self.font

    def screen_info(self,screen_info = False, display = False, screen = False, scale = False):
        if screen_info != False:
            self.display = screen_info[0]
            self.screen = screen_info[1]
            self.width = self.screen[0] * 2
            self.height = self.screen[1] * 2
            self.scale = screen_info[2]
            self.font = pygame.font.SysFont(self.font_name, self.font_size* self.scale)
        if display != False:
            self.display = display
        if screen != False:
            self.screen = screen
        if scale != False:
            self.scale = scale
            self.font = pygame.font.SysFont(self.font_name, self.font_size * self.scale)
        return (self.display,self.screen,self.scale)

    def colors(self, colors = False,text_color = False,border_color = False, background_color = False):
        if colors != False:
            self.tcolor = colors[0]
            self.bcolor = colors[1]
            self.bgcolor = colors[2]
            self.Colors = {}
            self.Colors["Text color"] = self.tcolor
            self.Colors["Border color"] = self.bcolor
            self.Colors["Background color"] = self.bgcolor
        if text_color != False:
            self.tcolor = text_color
            self.Colors["Text color"] = self.tcolor
        if border_color != False:
            self.bcolor = border_color
            self.Colors["Border color"] = self.bcolor
        if background_color != False:
            self.bgcolor = background_color
            self.Colors["Background color"] = self.bgcolor

        return (self.tcolor,self.bcolor,self.bgcolor)

    def sounds(self, type = False, sound = False, volume = False):
        if type != False:
            if type in self.Sounds:
                if sound != False:
                    self.Sounds[type] = pygame.mixer.Sound("sounds/" + sound)
                    self.sound_info[type]["name"] = sound
                if volume != False:
                    self.Sounds[type].set_volume(volume/100)
                    self.sound_info[type]["volume"] = volume
                return self.Sounds[type]
        else:
            if volume != False:
                for sound in self.Sounds:
                    self.Sounds[sound].set_volume((volume/100) * (self.sound_info[sound]["volume"]/100))
            return self.Sounds


def box(theme, pos, size,border_color = False,background_color = False):
    display, screen, scale = theme.screen_info()
    tcolor,bcolor,bgcolor = theme.colors()
    if border_color != False:
        bcolor = border_color
    if background_color != False:
        bgcolor = background_color
    sx, sy = screen
    px, py = pos
    x, y = sx + px * scale, sy + py * scale
    x2, y2 = size
    x2, y2 = x2 * scale, y2 * scale
    pygame.draw.rect(display, bcolor, (x - x2 / 2, y - y2 / 2, x2, y2))
    pygame.draw.rect(display, bgcolor, ((x - x2 / 2) + theme.border, (y - y2 / 2) + theme.border,
                                        x2 - theme.border*2, y2 - theme.border*2))

    return (x - x2 / 2, y - y2 / 2, x + x2 / 2, y + y2 / 2)


def text(theme, pos, text, in_box=False, size=False, text_color = False
         ,border_color = False,background_color = False,  center = "center"
         ,cut_dir = False):
    display, screen, scale = theme.screen_info()
    tcolor,bcolor,bgcolor = theme.colors()
    font = theme.fonts()
    if text_color != False:
        tcolor = text_color
    if border_color != False:
        bcolor = border_color
    if background_color != False:
        bgcolor = background_color
    if size == False:
        size = (0,0)
    sx, sy = screen
    x, y = pos
    x, y = sx + x * scale, sy + y * scale
    tx, ty = font.size(str(text))
    if in_box:
        box(theme, pos, size,border_color,background_color)
        while tx > size[0]*scale:
            if cut_dir:
                text = text[1:]
            else:
                text = text[:-1]
            tx = font.size(str(text))[0]

    text_text = font.render(str(text), True, tcolor)
    display.blit(text_text, get_center(center,scale,(x-tx/2, y-ty/2),tx,ty,size))
    return tx, ty

def get_center(center,scale,pos,tx = 0,ty = 0,size = (0,0)):
    x,y = pos
    sx,sy = size
    sx = sx / 2 * scale
    sy = sy / 2 * scale
    if center == "left":
        pos = ( x + tx / 2 - sx, y)
    elif center == "right":
        pos = (x - tx / 2 + sx, y)
    elif center == "top":
        pos = (x,y - ty / 2 - sy)
    elif center == "bottom":
        pos = (x, y + ty / 2 + sy)
    elif center == "top_left":
        pos = (x + tx / 2- sx,y + ty / 2 - sy)
    elif center == "top_right":
        pos = (x - tx / 2 + sx, y + ty / 2 - sy)
    elif center == "bottom_left":
        pos = (x + tx / 2, y - ty / 2 + sy)
    elif center == "bottom_right":
        pos = (x - tx / 2 + sx, y - ty / 2 + sy)
    return pos

def switch(theme, pos, state, input):
    display, screen, scale = theme.screen_info()
    tcolor,bcolor,bgcolor = theme.colors()
    sound = theme.sounds("button")
    sx, sy = screen
    x, y = pos
    x, y = sx + x * scale, sy + y * scale
    mx, my, mb = input.mouse()
    if mx != 0 and my != 0 and mb == 1:
        if x - 10 * scale < mx < x + 10 * scale:
            if y - 4 * scale < my < y + 4 * scale:
                if sound != False:
                    pygame.mixer.Sound.play(sound)
                state = not state
                input.clicked()
    if state:
        pygame.draw.circle(display, (0, 200, 0), (x - 6 * scale, y), 4 * scale)
        pygame.draw.rect(display, (0, 200, 0), (x - 6 * scale, y - 4 * scale, 13 * scale, 8 * scale))
        pygame.draw.circle(display, tcolor, (x + 6 * scale, y), 4 * scale)
    else:
        pygame.draw.circle(display, (255, 0, 0), (x + 6 * scale, y), 4 * scale)
        pygame.draw.rect(display, (255, 0, 0), (x - 6 * scale, y - 4 * scale, 13 * scale, 8 * scale))
        pygame.draw.circle(display, tcolor, (x - 6 * scale, y), 4 * scale)
    return (state)

def hit_box(theme, pos, size, input):
    display, screen, scale = theme.screen_info()
    sound = theme.sounds("button")
    sx, sy = screen
    x, y = pos
    x, y = sx + x * scale, sy + y * scale
    x2, y2 = size
    mx, my, mb = input.mouse()
    if mx != 0 and my != 0 and mb == 1:
        if x - (x2 / 2) * scale < mx < x + (x2 / 2) * scale:
            if y - (y2 / 2) * scale < my < y + (y2 / 2) * scale:
                if sound != False:
                    pygame.mixer.Sound.play(sound)
                input.clicked()
                return True
    return False

def hover(theme, pos, size, input):
    display, screen, scale = theme.screen_info()
    sx, sy = screen
    x, y = pos
    x, y = sx + x * scale, sy + y * scale
    x2, y2 = size
    mx, my, mb = input.mouse()
    if x - (x2 / 2) * scale < mx < x + (x2 / 2) * scale:
        if y - (y2 / 2) * scale < my < y + (y2 / 2) * scale:
            return True
    return False


def button(theme, pos, size, _text, input):
    display, screen, scale = theme.screen_info()
    tcolor,bcolor,bgcolor = theme.colors()
    sound = theme.sounds("button")

    sx, sy = screen
    x, y = pos
    x, y = sx + x * scale, sy + y * scale
    x2, y2 = size
    x2, y2 = x2* scale, y2* scale
    mx, my, mb = input.mouse()
    if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2:
        r,g,b = bgcolor
        if r - 16 < 0: r = 0
        else: r -= 16
        if g - 16 < 0: g = 0
        else: g -= 16
        if b - 16 < 0: b = 0
        else: b -= 16
        bgcolor = r, g, b
        if mb == 1:
            if sound != False:
                pygame.mixer.Sound.play(sound)
            input.clicked()
            return True
    text(theme, pos, _text, True, size, background_color = bgcolor)
    return False


class Text_Box:
    def __init__(self, theme, pos, size, text, text_center = "center" , center="center", in_box=True, default_text = "", resizeable = False):
        self.theme = theme
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.sound = theme.sounds("button")
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.in_text = False
        self.name = ""
        self.default_text = default_text
        self.text = str(text)
        self.pos = pos
        self.size = size
        self.font = theme.fonts()
        self.pointer = 0
        self.in_box = in_box
        self.center = center
        self.text_center = text_center
        self.resizeable = resizeable

    def update(self, input, maxTextLength = False):
        update(self, input, maxTextLength)

    def get_text(self):
        return str(self.text)

    def change_text(self, text):
        p_text = self.text
        self.text = str(text)
        return str(p_text)




def update(self, input, maxTextLength = False):
    sound = self.sound
    sx, sy = self.screen
    x, y = self.pos
    x, y = sx + x * self.scale, sy + y * self.scale
    size_x, size_y = self.size
    x2, y2 = size_x * self.scale, size_y * self.scale
    mx, my, mb = input.mouse()
    centerX, centerY =  get_center(self.center, self.scale, self.pos, size = self.size)
    mods = input.mods
    bgcolor = self.bgcolor
    if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2:
        r,g,b = bgcolor
        if r - 16 < 0: r = 0
        else: r -= 16
        if g - 16 < 0: g = 0
        else: g -= 16
        if b - 16 < 0: b = 0
        else: b -= 16
        bgcolor = r, g, b
        if mb == 1:
            input.clicked()
            if self.text == self.default_text:
                self.text = ""
            if sound != False:
                pygame.mixer.Sound.play(sound)
            self.in_text = True
    else:
        if mb != 0:
            self.in_text = False
            if self.text == "":
                self.text = self.default_text

    if self.in_text:
        # split text at cursor
        if self.pointer == 0:
            text1 = self.text
            text2 = ""
        else:
            text1 = self.text[:-self.pointer]
            text2 = self.text[-self.pointer:]
        for key in input.keys:
            # backsapce
            if key == 8:
                text1 = text1[:-1]
                self.text = text1 + text2
                max = len(self.text)
                if self.pointer > max:
                    self.pointer = max
                print(self.pointer)
            # delete
            elif key == 127:
                text2 = text2[1:]
                self.text = text1 + text2
                if self.pointer > 0:
                    self.pointer -= 1
                print(self.pointer)
            # enter
            elif key == 13 or key == 27:
                self.in_text = False
                if self.text == "":
                    self.text = self.default_text

            # left arrow
            elif key == 1073741904:
                max = len(self.text)
                self.pointer += 1
                if self.pointer > max:
                    self.pointer = max
                print(self.pointer)
            # right arrow
            elif key == 1073741903:
                if self.pointer > 0:
                    self.pointer -= 1
                print(self.pointer)
            # ctrl-v
            elif key == 118 and "CTRL" in mods:
                try:
                    win32clipboard.OpenClipboard()
                    data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    self.text = text1 + data + text2
                except:
                    print("What is this bullshit")

            # ctrl-c
            elif key == 99 and "CTRL" in mods:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(self.text)
                win32clipboard.CloseClipboard()
            # ctrl-x
            elif key == 120 and "CTRL" in mods:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(self.text)
                win32clipboard.CloseClipboard()
                self.text = ""
            # ctrl-delete
            elif key == 127 and "CTRL" in mods:
                self.text = ""

        # add key to text
            for key  in input.unicode:
                textX, textY = self.font.size(self.text)
                if maxTextLength != False:
                    if textX + 20 < maxTextLength:
                        text1 = text1 + key
                        textX, textY = self.font.size(text1+ text2)
                        if textX + 10 > maxTextLength:
                            text1 = text1[:-1]
                        self.text = text1 + text2
                else:
                    self.text = text1 + key + text2



        _text = self.text
        textX, textY = self.font.size(_text)
        textOffset = self.font.size(self.text[:-len(_text)])
        text(self.theme, self.pos, _text, self.in_box,self.size, background_color=bgcolor,cut_dir = True, center = self.center)

        if input.cursor():
            t1x, t1y = self.font.size(text1)
            t1x -= (textX + textOffset[0]) /2 + textOffset[0]/2
            if t1x > (self.size[0]*self.scale)/2- self.theme.border*self.scale:
                t1x = (self.size[0]*self.scale)/2- self.theme.border*self.scale

            pygame.draw.line(self.display, self.tcolor, (x+t1x,y+t1y/2.5), (x+t1x,y-t1y/2.5), self.scale)

        #set pointer on mouse click
        if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2 and mb == 1:
            clicked = True
            mx = mx-self.screen[0] - centerX*self.scale
            print(mx)



    else:
        _text = self.text
        tx, ty = self.font.size(_text)
        if maxTextLength != False:
            while tx + 10 > x2:
                _text = _text[1:]
                tx, ty = self.font.size(_text)
        text(self.theme, (centerX,centerY), _text, self.in_box,self.size, background_color=bgcolor)


def get_text(self):
    return str(self.text)


def change_text(self, text):
    p_text = self.text
    self.text = str(text)
    return str(p_text)


def graph(theme, pos, size, values, name):
    display, screen, scale = theme.screen_info()
    tcolor,bcolor,bgcolor = theme.colors()
    sx, sy = screen
    px, py = pos
    x, y = sx + px * scale, sy + py * scale
    sx, sy = size
    x2, y2 = sx * scale, sy * scale
    gx, gy = x + x2 / 2, y + y2 / 2
    box(theme, pos, size)

    text(theme, (px, py + sy / 1.7), name, font, tcolor)
    p_point = None
    total_x = len(values) - 1
    p_time = total_x
    for point in values:
        if point > 100:
            point = 100
        py = point * (y2 / 100)
        if p_point != None:
            ppx, ppy = p_point
            pygame.draw.line(display, tcolor, ((gx - p_time * (x2 / total_x)), gy - py),
                             (gx - ppx * (x2 / total_x), gy - ppy), 2)
        p_point = (p_time, py)
        p_time -= 1


def vertical_bar_graph(theme, pos, size, value,max_value = 100,min_value = 0, name = ""):
    display, screen, scale = theme.screen_info()
    color,bcolor,bgcolor = theme.colors()
    sx, sy = screen
    px, py = pos
    x, y = sx + px * scale, sy + py * scale
    sx, sy = size
    x2, y2 = sx * scale, sy * scale
    box(theme, pos, size)
    if value > max_value:
        pygame.draw.rect(display, bcolor, (x - x2 / 2, (y + y2 / 2) - y2, x2, y2))
    else:
        fill = (y2 / max_value) * value
        pygame.draw.rect(display, color, (x - x2 / 2, (y + y2 / 2) - fill, x2, fill))
    text(theme,(px, py - sy / 1.7), name)


def horizontal_bar_graph(theme, pos, size, value, name):
    display, screen, scale = theme.screen_info()
    color,bcolor,bgcolor = theme.colors()
    sx, sy = screen
    px, py = pos
    x, y = sx + px * scale, sy + py * scale
    sx, sy = size
    x2, y2 = sx * scale, sy * scale
    box(theme, pos, size)
    if value > 100:
        pygame.draw.rect(display, bcolor, (x - x2 / 2, (y + y2 / 2) - y2, x2, y2))
    else:
        fill = (x2 / 100) * value
        pygame.draw.rect(display, color, ((x - x2 / 2), (y - y2 / 2), fill, y2))
    text(theme, (px, py + y2 / 3), name)


def multi_graph(theme, pos, size, time, values, name):
    display, screen, scale = theme.screen_info()
    sx, sy = screen
    px, py = pos
    x, y = sx + px * scale, sy + py * scale
    sx, sy = size
    x2, y2 = sx * scale, sy * scale
    gx, gy = x + x2 / 2, y + y2 / 2
    box(theme, pos, size)
    text(theme, (px, py + sy / 1.85), name)
    for value in values:
        color = value[:3]
        print(color)
        value = value[3:]
        p_point = None
        p_time = len(time) - 1
        max_time = time[-1]
        print(max_time)
        for _ in value:
            point = value[p_time]
            if point > 100:
                point = 100
            py = point * ((y2 - 2) / 100)
            if p_point != None:
                ppx, ppy = p_point
                pygame.draw.line(display, color, ((gx - (time[-p_time - 1] * (x2 / max_time))), (gy - py - 2)),
                                 ((gx - (ppx * (x2 / max_time))), (gy - ppy - 2)), 2)
            p_point = (time[-p_time - 1], py)
            p_time -= 1



def value_lable(theme, pos, value, name, center="center", in_box=False, size=False, text_color = False
         ,border_color = False, background_color = False):
    display, screen, scale = theme.screen_info()
    font = theme.fonts()
    name = str(value) + str(name)
    tx,ty = font.size(name)
    text(theme, pos, name, in_box, size, center=center, text_color = text_color
         ,border_color = border_color, background_color = background_color)


def lable_value(theme, pos, name, value, center="center", in_box=False, size=False, fixed = True, text_color = False
         ,border_color = False,background_color = False):
    display, screen, scale = theme.screen_info()
    font = theme.fonts()
    name = str(name) + str(value)
    tx, ty = font.size(name)
    text(theme, pos, name, in_box, size, center=center, text_color = text_color
         ,border_color = border_color, background_color = background_color)

def lable(theme, pos, name, center="center", in_box=False, size=False, fixed = True, text_color = False
         ,border_color = False,background_color = False):
    display, screen, scale = theme.screen_info()
    font = theme.fonts()
    name = str(name)
    tx, ty = font.size(name)
    text(theme, pos, name, in_box, size, center=center, text_color = text_color
         ,border_color = border_color, background_color = background_color)



class lable_text:
    def __init__(self, theme, pos, size, name, value, text_center="center",center="center",in_box=True, resizeable = False):
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.sound = theme.sounds("button")
        self.in_text = False
        self.name = name
        self.text = str(value)
        self.default_text = str(value)
        self.pos = pos
        self.mousePos = (0,0)
        self.size = size
        self.pointer = 0
        self.in_box = in_box
        self.center = center
        self.text_center = text_center
        self.resizeable = resizeable

    def update(self, input):
        posX,posY = self.pos
        sizeX, sizeY = self.size
        text(self.theme,(posX-sizeX-20,posY),self.name, self.in_box,self.size)
        return update(self, input)

class color_picker:
    def __init__(self, theme, pos, size, name = "", color = (0,0,0), center="center"):
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.sound = theme.sounds("button")
        self.pos = pos
        self.color = (color[0],color[1],color[2])
        self.size = size
        self.name = str(name)
        self.center = center
        self.text_center = "center"
        sx, sy = self.screen
        scale = self.scale
        px, py = pos
        px, py = px * scale, py * scale
        x, y = sx + px, sy + py
        sx, sy = size
        sx, sy = sx * scale, sy * scale
        self.Spectrum = pygame.transform.scale(pygame.image.load("images/spectrum_chart.jpg"), (sx-4, sy-4))

        if center == "center":
            x, y = x - sx / 2, y - sy / 2
        elif center == "left":
            x, y = x - sx / 2, y
        self.rect = (x+2, y+2)

    def get_color(self, input):
        box(self.theme, self.pos, self.size)
        self.display.blit(self.Spectrum, self.rect)
        px, py = self.pos
        x, y = self.rect
        sx, sy = self.size
        x2, y2 = sx * self.scale, sy * self.scale
        mx, my, mb = input.mouse()
        mb = abs(mb)
        if x < mx < x + x2 and y < my < y + y2 and mb == 1:
            input.clicked()
            self.color = (self.display.get_at((int(mx), int(my)))[:3])

        R,G,B = self.color
        luminance = R * 0.2126 + G * 0.7152 + B * 0.0722
        if luminance > 120:
            C=0
        else:
            C = 255
        text_color = (C,C,C)

        text(self.theme, (px - (sx + 20), py), self.name,True, self.size, text_color = text_color,background_color = self.color)

        return self.color


class multiple_choice_input:
    def __init__(self, theme, pos, size, name, current_value, values, max_values, center="center", pointer=0):
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.sound = theme.sounds("button")
        self.selected = False
        self.name = name
        self.text = str(current_value)
        self.values = values
        self.max_values = max_values
        self.pos = pos
        self.size = size
        self.pointer = pointer
        self.in_box = True
        scale = self.scale
        x, y = self.screen
        px, py = pos
        sx, sy = size
        x2, y2 = self.scaled = sx * scale, sy * scale
        self.rect = ((x + px * scale) - (x2 / 2), (y + py * scale) - (y2 / 2), (x + px * scale) + (x2 / 2),
                     (y + py * scale) + (y2 / 2))

    def update(self, input):
        px, py = self.pos
        x, y, x2, y2 = self.rect
        text_x, text_y = self.font.size("pd")
        text_y = text_y * (2 / self.scale)
        mx, my, mb = input.mouse()
        screen_x,screen_y = self.screen
        bgcolor = self.theme.bgcolor
        if self.selected:
            if len(self.values) > self.max_values:
                values = self.values[self.pointer:self.max_values + self.pointer]
                start_pos = len(values) * text_y
                box_rect = box(self.theme, (px + 120, py), (100, (start_pos / 2) + 10))
                pos = - math.floor(len(values) / 2)
                if len(values) %2 == 0:
                    pos += 0.5
                for each in values:
                    text(self.theme, (px + 120, py + pos * (text_y / 2)), each)
                    pos += 1
            else:
                start_pos = len(self.values) * text_y
                box_rect = box(self.theme, (px + 120, py), (100, (start_pos / 2) + 10))
                values = self.values
                pos = - math.floor(len(self.values) / 2)
                if len(self.values)%2 == 0:
                    pos += 0.5
                for each in values:
                    text(self.theme, (px + 120, py + pos * (text_y / 2)), each)
                    pos += 1

            bx, by, bx2, by2 = box_rect

            if bx < mx < bx2 and by < my < by2 and mb == 1:
                input.clicked()
                if self.sound != False:
                    pygame.mixer.Sound.play(self.sound)
                click = my - by
                self.text = values[math.floor(click / ((by2 - by) / len(values)))]

            self.pointer += input.scroll()

            if self.pointer < 0:
                self.pointer = 0
            if self.pointer > len(self.values) - self.max_values:
                self.pointer = len(self.values) - self.max_values


        if x < mx < x2 and y < my < y2:
            r,g,b = bgcolor
            if r - 16 < 0: r = 0
            else: r -= 16
            if g - 16 < 0: g = 0
            else: g -= 16
            if b - 16 < 0: b = 0
            else: b -= 16
            bgcolor = r, g, b
            if  mb == 1:
                input.clicked()
                self.selected = True
                if self.sound != False:
                    pygame.mixer.Sound.play(self.sound)
        elif mb != 0:
                self.selected = False

        size_x,size_y = self.size
        text(self.theme, (px - (size_x+20), py), self.name,self.in_box,self.size)
        text(self.theme, self.pos, self.text,self.in_box,self.size,background_color=bgcolor)


class pop_up:
    def __init__(self, theme, pos1, pos2, speed, delay, size, text, center="center"):
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.text = str(text)
        self.pos1 = pos1
        self.pos2 = pos2
        self.pos = pos1
        self.speed = speed
        self.delay = delay
        self.size = size
        if size[0] == -1:
            self.size = (self.font.size(self.text)[0]/self.scale+10,self.size[1])
        self.start = False
        self.delay_time = 0
        self._return = False
        self.pop_up = True
        self.last_frame = time.perf_counter()

    def update(self):
        self.frame_time = (time.perf_counter() - self.last_frame) * 100
        self.last_frame = time.perf_counter()
        if self.pop_up:
            posx, posy = self.pos
            posx1, posy1 = self.pos1
            posx2, posy2 = self.pos2

            if self.pos == self.pos2:
                if not self.start:
                    self.delay_time = time.perf_counter() + self.delay
                    self.start = True
                if time.perf_counter() > self.delay_time:
                    self.start = False
                    self._return = True
                    if posx > posx1: posx -= self.speed*(self.frame_time/4)
                    if posx < posx1: posx += self.speed*(self.frame_time/4)
                    if posy > posy1: posy -= self.speed*(self.frame_time/4)
                    if posy < posy1: posy += self.speed*(self.frame_time/4)

            else:
                if self._return:
                    if self.pos == self.pos1:
                        self._return = False
                        self.pop_up = False
                    else:
                        if posx > posx1:
                            posx -= self.speed*(self.frame_time/4)
                            if posx < posx1:
                                posx = posx1
                        if posx < posx1:
                            posx += self.speed*(self.frame_time/4)
                            if posx > posx1:
                                posx = posx1
                        if posy > posy1:
                            posy -= self.speed*(self.frame_time/4)
                            if posy < posy1:
                                posy = posy1
                        if posy < posy1:
                            posy += self.speed*(self.frame_time/4)
                            if posy > posy1:
                                posy = posy1

                else:
                    if posx > posx2:
                        posx -= self.speed*(self.frame_time/4)
                        if posx < posx2:
                            posx = posx2
                    if posx < posx2:
                        posx += self.speed*(self.frame_time/4)
                        if posx > posx2:
                            posx = posx2
                    if posy > posy2:
                        posy -= self.speed*(self.frame_time/4)
                        if posy < posy2:
                            posy = posy2
                    if posy < posy2:
                        posy += self.speed*(self.frame_time/4)
                        if posy > posy2:
                            posy = posy2


            self.pos = (posx, posy)
            text(self.theme, self.pos, self.text,True,self.size)



class file:
    def __init__(self,theme,pos,size,file_name,input,mode = "Open"):
        self.Input = input
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.sound = theme.sounds("button")
        size_x,size_y = size
        self.file_name = Text_Box(theme, (15, -size_y/2+12),(size_x-108, 15), file_name,in_box = True)
        self.file_history = [file_name]
        self.selected = "No file selected"
        self.size = size
        self.pos = pos
        self.browsing = False
        self.pointer = 0
        self.filters = False
        self.mode = mode


    def browse(self):
        sound = self.sound
        color = (64, 64, 64)
        file_name = self.file_name.text
        mx,my,mb = self.Input.mouse()
        px, py  =  self.pos
        size_x, size_y = self.size
        sx, sy = self.screen_info[1]
        scale = self.screen_info[2]
        row = 17
        stuff = []

        if self.filters:
            box(self.theme, self.pos, self.size)
            text(self.theme, (px, -size_y / 2 + 12), "Filters")
            text(self.theme, (px, py), "Sorry no filters are available.")

            if button(self.theme,(px+size_x/2-25, -size_y/2+12),(30,15),"Exit",self.Input):
                self.Input.clicked()
                print("Exit")
                self.filters = False
                self.browsing = False
                if sound != False:
                    pygame.mixer.Sound.play(sound)

            if button(self.theme,(px+size_x/2-60,py+size_y/2-15),(80,15),"Apply",self.Input):
                self.Input.clicked()
                print("Apply")
                self.filters = False
                if sound != False:
                    pygame.mixer.Sound.play(sound)

            if button(self.theme,(px-size_x/2+60,py+size_y/2-15),(80,15),"Cancel",self.Input):
                self.Input.clicked()
                print("Cancel")
                self.filters = False
                if sound != False:
                    pygame.mixer.Sound.play(sound)

        else:
            box(self.theme,self.pos,self.size)
            self.file_name.update(self.Input)
            text(self.theme, (-size_x/2+40, -size_y/2+12), "Search",in_box=True,size =(60,15))
            if button(self.theme,(px+size_x/2-25, -size_y/2+12),(30,15),"Exit",self.Input):
                self.Input.clicked()
                print("Exit")
                self.browsing = False
                if sound != False:
                    pygame.mixer.Sound.play(sound)

            if button(self.theme,(px-size_x/2+60,py+size_y/2-15),(80,15),"Back",self.Input) or mb == 6:
                self.Input.clicked()
                print("back")
                self.pointer = 0
                path = file_name.split("/")
                if "" in path:
                    path = path[:-1]
                path = path[:-1]
                file_name = ''
                for folder in path:
                    print(file_name)
                    file_name += folder+"/"
                self.file_name.change_text(file_name)
                self.selected = ""
                if sound != False:
                    pygame.mixer.Sound.play(sound)

            if button(self.theme,(px,py+size_y/2-15),(80,15),"Filters",self.Input):
                self.Input.clicked()
                print("Filters")
                self.filters = True
                if sound != False:
                    pygame.mixer.Sound.play(sound)

            self.pointer -= self.Input.scroll()
            if self.pointer > len(stuff)/2:
                self.pointer = len(stuff)/2


            _file_name = file_name

            try:
                if len(file_name) > 1:
                    while not os.path.isdir(_file_name):
                        _file_name = _file_name[:-1]
                        if _file_name == "":
                            break

                    name = file_name.strip(_file_name)
                    for each in os.listdir(_file_name):
                        if each.lower().startswith(name.lower()):
                            stuff.append(each)

                else:
                    for drive in range(26):
                        drive += 65
                        drive = chr(drive)
                        if os.path.isdir(drive+":"):
                            stuff.append(drive+":")
            except:
                pass

            top = -size_y/2 + 13 + self.pointer*row
            line = -75
            if 10 < len(stuff) < 20:
                column1 = stuff[:9]
                column2 = stuff[9:]
            elif len(stuff) > 10:
                split = math.ceil(len(stuff)/2)
                column1 = stuff[:split]
                column2 = stuff[split:]
            else:
                column1 = stuff
                column2 = []

            columns = [column1,column2]
            for  column in  columns:
                for each in column:
                    try:
                        if file_name.find("Blueprints/"):
                            with open(file_name+each+'/description.json',"r") as description:
                                description = json.loads(description.read())
                                name = description["name"]
                        else:
                            name = each
                    except:
                        name = each

                    tx,ty = self.font.size(name)
                    if tx > 130*scale:
                        name += "..."
                        while tx > 130*scale:
                            name = name[:-4]
                            name += "..."
                            tx, ty = self.font.size(name)


                    top += row
                    if top > -size_y / 2 + row:
                        if on_hover(self.theme,(line, top),(130,15),self.Input) or each == self.selected:
                            r,g,b = self.bgcolor
                            if r - 16 < 0: r = 0
                            else: r -= 16
                            if g - 16 < 0: g = 0
                            else: g -= 16
                            if b - 16 < 0: b = 0
                            else: b -= 16
                            bgcolor = r, g, b
                        else:
                            bgcolor = self.bgcolor
                        lable(self.theme,(line, top),name, in_box = True,size = (130,15),background_color=bgcolor)
                        if hit_box(self.theme,(line, top),(130,15),self.Input):
                            self.selected = each
                            path = file_name.split("/")
                            path = path[:-1]
                            file_name = ''
                            for folder in path:
                                file_name += folder + "/"
                            file_name += each+"/"
                            if not os.path.isdir(file_name):
                                file_name = file_name +  '/' + each + '/'
                            if os.path.isdir(file_name):
                                self.file_name.change_text(file_name)
                                self.pointer = 0
                            if sound != False:
                                pygame.mixer.Sound.play(sound)

                    if top > py + size_y / 2 - row*3:
                        break
                top = -size_y / 2 + 13 + self.pointer * row
                line += 150

            if button(self.theme,(px+size_x/2-60,py+size_y/2-15),(80,15),self.mode,self.Input):
                self.Input.clicked()
                print(self.mode)
                if sound != False:
                    pygame.mixer.Sound.play(sound)
                if self.mode == "Open":
                    self.browsing = False
                elif self.mode == "Save as":
                    x,y = pos = (0,0)
                    sx,sy = size = (200,100)
                    save_name = Text_Box(self.theme, (x, y), (sx / 1.2, 15), "", default_text = "File name" )
                    lable(self.theme,(px+size_x/2-60,py+size_y/2-15),self.mode, in_box = True, size = (80,15))
                    while True:
                        for event in pygame.event.get():
                            self.Input.get_input(event)
                        self.Input.update()
                        box(self.theme, pos, size)
                        lable(self.theme,(x, y - sy / 2 + 20),"Save file as",in_box = True, size =  (sx / 2, 15))
                        save_name.update(self.Input)
                        if button(self.theme, (x - sx / 2 + sx / 4, y + sy / 2 - 20), (sx / 3, 15), "Cancel", self.Input):
                            break
                        if button(self.theme, (x + sx / 2 - sx / 4, y + sy / 2 - 20), (sx / 3, 15), "Save", self.Input):
                            try:
                                shutil.copy("temp", self.file_name.text + save_name.text + ".xml")
                            except Exception as e:
                                print(e)
                            break
                            self.browsing = False
                        pygame.display.update()
                        time.sleep(0.05)

                elif self.mode == "Set Path":
                    self.browsing = False


def alert(theme, pos, size, name, button1, button2, Input, frame,  timer = False, center="center"):
    name = str(name)
    button1 = str(button1)
    button2 = str(button2)
    x, y = pos
    sx, sy = size
    scale = theme.scale
    text_x, text_y = theme.font.size(name)
    name_list = name.split(" ")
    if timer != False:
        timer = time.perf_counter()+timer
    while True:
        for event in pygame.event.get():
            Input.get_input(event,frame)
        Input.update(frame)
        if timer != False:
            if timer < time.perf_counter():
                return False
        box(theme, pos, size)
        line = ""
        Pos = 0
        for each in name_list:
            line += each + " "
            text_x, text_y = theme.font.size(line)
            if text_x > (sx * scale) / 2+20:
                lable(theme, (x, y - sy / 2 + 15 + Pos), line)
                line = ""
                Pos += 15
        lable(theme, (x, y - sy / 2 + 15 + Pos), line)
        if button(theme,(x-sx/2+sx/4,y+sy/2-20),(sx/3,15),button1,Input):
            return True
        if button(theme, (x+sx/2-sx/4, y+sy/2-20), (sx/3, 15),button2,Input):
            return False
        if timer != False:
            lable(theme, (x, y+sy/2-20), round(timer - time.perf_counter()))
        frame+=1
        pygame.display.update()
        time.sleep(0.05)


class slider:
    def __init__(self,theme,pos,size,direction,Input, value = 0):
        self.Input = Input
        self.theme = theme
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()
        self.font = theme.fonts()
        self.sound = theme.sounds("button")
        self.pos = pos
        self.size = size
        self.direction = direction
        self.value = value
        self.center = "center"
        self.selected = False
        self.p_mouse = self.Input.mouse()
        self.p_value = self.value

    def update(self):
        sx,sy = self.size
        sx,sy = sx*self.scale,sy*self.scale
        x,y = self.pos
        screenx, screeny = self.screen
        box(self.theme,self.pos,self.size)
        if hover(self.theme,self.pos,self.size,self.Input):
            self.value -= self.Input.scroll()/100
            if self.value > 1:
                self.value = 1
            if self.value < 0:
                self.value = 0

        if hit_box(self.theme,self.pos,self.size,self.Input):
            self.selected = True
            mx,my,mb = self.p_mouse = self.Input.mouse()

            if self.direction == "up":
                self.value = 1-(my - y-sy/2)/sy
                print(self.value)
            elif self.direction == "right":
                self.value = (mx - (screenx - x - sx/2))/sx
            elif self.direction == "down":
                self.value = (my - y-sy/2)/sy
            elif self.direction == "left":
                self.value = 1-(mx - (screenx - x - sx/2))/sx

        if self.selected:
            mx,my,mb = self.Input.mouse()
            pmx, pmy, pmb = self.p_mouse
            if mb == -1:
                if self.direction == "up":
                    self.value += (pmy-my)/sy
                elif self.direction == "right":
                    self.value += (mx - pmx)/sx
                elif self.direction == "down":
                    self.value += (my - pmy)/sy
                elif self.direction == "left":
                    self.value += (pmx - mx)/sx
                self.p_mouse = self.Input.mouse()
                if self.value > 1:
                    self.value = 1
                if self.value < 0:
                    self.value = 0

            else:
                self.selected = False

        if self.direction  == "up":
            spy = sy / 2 - sy * self.value
            if spy > sy/2-sx/4:
                spy = sy/2-sx/4
            elif spy < -sy / 2 + sx/4:
                spy = -sy / 2 + sx/4
            slider_pos = (x,spy)
            size = (sx,sx/2)

        elif self.direction  == "right":
            spx = -sx / 2 + sx * self.value
            if spx > sx/2-sy/4:
                spx = sx/2-sy/4
            elif spx < -sx / 2 + sy/4:
                spx = -sx / 2 + sy/4
            slider_pos = (spx,y)
            size = (sy/2,sy)

        elif self.direction == "down":
            spy = sy / 2 + sy * self.value
            if spy > sy/2-sx/4:
                spy = sy/2-sx/4
            elif spy < -sy / 2 + sx/4:
                spy = -sy / 2 + sx/4
            slider_pos = (x,spy)
            size = (sx,sx/2)

        elif self.direction == "left":
            spx = sx / 2 - sx * self.value
            if spx > sx/2-sy/4:
                spx = sx/2-sy/4
            elif spx < -sx / 2 + sy/4:
                spx = -sx / 2 + sy/4
            slider_pos = (spx,y)
            size = (sy/2,sy)
        spx,spy = slider_pos
        sizex,sizey = size
        sizex, sizey = sizex - self.theme.border*2, sizey  - self.theme.border*2
        cx,cy = get_center(self.center,self.scale,self.pos,size=self.size)
        pygame.draw.rect(self.display, self.tcolor, (cx+screenx+x+spx-sizex/2,cy+screeny+y+spy-sizey/2,sizex,sizey))
        if int(self.value*100) == int(self.value*10)*10 and self.value != self.p_value:
            pygame.mixer.Sound.play(self.sound)

        self.p_value = self.value


def button_list(theme,pos,size,options,max,Input):
    for each in options:
        if button(theme,pos,size,each,Input):
            return each
        pos += size[1]+5


class window:
    def __init__(self, theme, pos, size, name, Input, resizeable=False, min=False, max=False):
        self.theme = theme
        self.display = theme.display
        self.screen = theme.screen
        self.scale = theme.scale
        self.Input = Input
        self.pos = pos
        self.size = size
        self.name = name
        self.resizeable =resizeable
        if min == False:
            self.min = (0,0)
        else:
            self.min = min
        if max == False:
            self.max = self.screen
        else:
            self.max = max
        self.resizing = False
        self.smx = 0
        self.smy = 0
        self.dir = 0

    def update(self):
        action = None
        sx, sy = self.screen
        x, y = self.pos
        x, y = sx + x * self.scale, sy + y * self.scale
        size_x, size_y = self.size
        x2, y2 = size_x * self.scale, size_y * self.scale
        mx, my, mb = self.Input.mouse()
        old_x,old_y = self.pos

        if self.resizeable:
            if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2:
#resize window <^v>
                if y - y2 / 2 + self.theme.border * 3 > my:
                    if x - x2 / 2 + self.theme.border * 3 > mx:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smx = mx
                            self.smy = my
                            self.dir = 6
                        pygame.mouse.set_system_cursor(5)
                    elif x + x2 / 2 - self.theme.border * 3 < mx:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smx = mx
                            self.smy = my
                            self.dir = 7
                        pygame.mouse.set_system_cursor(6)
                    else:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smy = my
                            self.dir = 3
                        pygame.mouse.set_system_cursor(8)
                elif y + y2 / 2 - self.theme.border * 3 < my:
                    if x - x2 / 2 + self.theme.border * 3 > mx:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smx = mx
                            self.smy = my
                            self.dir = 8
                        pygame.mouse.set_system_cursor(6)
                    elif x + x2 / 2 - self.theme.border * 3 < mx:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smx = mx
                            self.smy = my
                            self.dir = 9
                        pygame.mouse.set_system_cursor(5)
                    else:
                        if mb == 1:
                            self.Input.clicked()
                            self.resizing = True
                            self.smy = my
                            self.dir = 4
                        pygame.mouse.set_system_cursor(8)
                elif x - x2 / 2 + self.theme.border * 3 > mx:
                    if mb == 1:
                        self.Input.clicked()
                        self.resizing = True
                        self.smx = mx
                        self.dir = 1
                    pygame.mouse.set_system_cursor(7)
                elif x + x2 / 2 - self.theme.border * 3 < mx:
                    if mb == 1:
                        self.Input.clicked()
                        self.resizing = True
                        self.smx = mx
                        self.dir = 2
                    pygame.mouse.set_system_cursor(7)
#move whole window
                elif my < (y - y2 / 2)+15*self.scale and mx < x+x2/2 - 30*self.scale:
                    if mb == 1:
                        self.Input.clicked()
                        self.resizing = True
                        self.smx = mx
                        self.smy = my
                        self.dir = 5
                    pygame.mouse.set_system_cursor(9)

                elif not self.resizing:
                    pygame.mouse.set_system_cursor(0)
            elif not self.resizing:
                pygame.mouse.set_system_cursor(0)
            if mb == -1 and self.resizing:
                if self.dir == 1:
                    dmx = (self.smx - mx)/ self.scale
                    self.pos = (self.pos[0] - dmx / 2, self.pos[1])
                    self.size = (self.size[0] + dmx, self.size[1])
                elif self.dir == 2:
                    dmx = (mx - self.smx)/ self.scale
                    self.pos = (self.pos[0] + dmx / 2, self.pos[1])
                    self.size = (self.size[0] + dmx, self.size[1])
                elif self.dir == 3:
                    dmy = (self.smy - my )/ self.scale
                    self.pos = (self.pos[0], self.pos[1] - dmy / 2)
                    self.size = (self.size[0], self.size[1] + dmy)
                elif self.dir == 4:
                    dmy = (self.smy - my)/ self.scale
                    self.pos = (self.pos[0], self.pos[1] - dmy / 2)
                    self.size = (self.size[0], self.size[1] - dmy)
                elif self.dir == 5:
                    dmx, dmy = (self.smx - mx) / self.scale, (self.smy - my) / self.scale
                    self.pos = (self.pos[0] - dmx, self.pos[1] - dmy)
                elif self.dir == 6:
                    print("6")
                    dmx, dmy = (self.smx - mx)/ self.scale, (self.smy - my)/ self.scale
                    self.pos = (self.pos[0] - dmx / 2, self.pos[1] - dmy / 2)
                    self.size = (self.size[0] + dmx, self.size[1] + dmy)
                elif self.dir == 7:
                    print("7")
                    dmx, dmy = (self.smx - mx)/ self.scale, (self.smy - my)/ self.scale
                    self.pos = (self.pos[0] - dmx / 2, self.pos[1] - dmy / 2)
                    self.size = (self.size[0] - dmx, self.size[1] + dmy)
                elif self.dir == 8:
                    print("8")
                    dmx, dmy = (self.smx - mx)/ self.scale, (self.smy - my)/ self.scale
                    self.pos = (self.pos[0] - dmx / 2, self.pos[1] - dmy / 2)
                    self.size = (self.size[0] + dmx, self.size[1] - dmy)
                elif self.dir == 9:
                    print("9")
                    dmx, dmy = (self.smx - mx)/ self.scale, (self.smy - my)/ self.scale
                    self.pos = (self.pos[0] - dmx / 2, self.pos[1] - dmy / 2)
                    self.size = (self.size[0] - dmx, self.size[1] - dmy)



            if mb == 0 and self.resizing:
                self.resizing = False
            self.smx, self.smy = mx, my
            if self.min[0] > self.size[0]:
                self.size = (self.min[0],self.size[1])
                self.pos = (old_x,self.pos[1])
            if self.max[0] < self.size[0]:
                self.size = (self.max[0], self.size[1])
                self.pos = (old_x, self.pos[1])
            if self.min[1] > self.size[1]:
                self.size = (self.size[0],self.min[1])
                self.pos = (self.pos[0],old_y )
            if self.max[1] < self.size[1]:
                self.size = (self.size[0], self.max[1])
                self.pos = (self.pos[0], old_y)



        x,y = self.pos
        sx,sy = self.size
        box(self.theme,self.pos,self.size)
        lable(self.theme, (x, y - sy / 2 + 7.5), self.name, in_box=True, size=(sx, 15))
        if button(self.theme, (x+sx/2 - 22.5, y - sy / 2 + 7.5),(15,15),"←",self.Input):
            action = "back"
        if button(self.theme, (x+sx/2 - 7.5, y - sy / 2 + 7.5),(15,15),"X",self.Input):
            action = "close"
        return x, y, sx, sy, action