import time
import pygame
import json
import my_gui as gui
from Network import Network


class chat:
    def __init__(self, theme, n, Input, player):
        self.theme = theme
        self.n = n
        self.Input = Input
        self.chat_refresh = time.perf_counter()
        self.screen_x = theme.screen[0] / theme.scale
        self.screen_y = theme.screen[1] / theme.scale
        self.player = player
        self.scale = theme.scale
        self.messages = {}
        self.last_message = None
        self.pos = (-self.screen_x + 75, self.screen_y - 100)
        self.size = (150, 200)
        self.pointer = 0
        self.message_list = []
        self.ping = "--"
        self.received = True
        self.sent = False
        self.window = gui.window(self.theme, self.pos, self.size, "PyChat", self.Input, resizeable=True, min = (50,50),max = self.theme.screen)
        self.pychat_input = gui.Text_Box(theme, (-self.screen_x + 61, self.screen_y - 7.5), (122, 15), "", text_center="left")
        self.screen_pointer = "main_menu"
        self.channel = None
        self.PyChat_servers = []
        self.channel_name = ""
        self.server_ID = 0
        self.channel_name_gui = gui.Text_Box(theme, self.pos, (self.size[0], 20), "Channel Name")
        self.channel_pass_gui = gui.Text_Box(theme, self.pos, (self.size[0], 20), "password")


    def set_up(self,pos,size):
        self.pos = (x,y) = pos
        self.size = (sx,sy) = size
        self.pychat_input = gui.Text_Box(self.theme, (x-14, y+sy/2 - 7.5), (sx-28, 15), "", text_center="left")

    def reload(self):
        self.screen_x = self.theme.screen[0] / self.theme.scale
        self.screen_y = self.theme.screen[1] / self.theme.scale
        self.scale = self.theme.scale
        self.pos = (-self.screen_x + 75, self.screen_y - 100)
        self.window = gui.window(self.theme, self.pos, self.size, "PyChat", self.Input, resizeable=True, min = (50,50), max = self.theme.screen)
        self.pychat_input = gui.Text_Box(self.theme, (-self.screen_x + 61, self.screen_y - 7.5), (122, 15), "", text_center="left")
        self.channel_name_gui = gui.Text_Box(self.theme, self.pos, (self.size[0], 20), "Channel Name")
        self.channel_pass_gui = gui.Text_Box(self.theme, self.pos, (self.size[0], 20), "password")

    def update(self, Input):
        x, y, sx, sy, action= self.window.update()
        if action != None:
            if action == "back":
                self.screen_pointer = "main_menu"


        if self.screen_pointer == "main_menu":
            if gui.button(self.theme, (x, y-15), (sx, 20), "Join Existing Chat", Input):
                self.screen_pointer = "channel_selector"
                self.n.send({"packet": "get_PyChats"})
            if gui.button(self.theme, (x, y+15), (sx, 20), "Create New Chat", Input):
                self.screen_pointer = "channel_Creator"

        elif self.screen_pointer ==  "channel_selector":
            data = self.n.receive("PyChat_servers")
            if data != None:
                self.PyChat_servers = data["servers"]
            pos = -25
            if self.PyChat_servers == []:
                if gui.button(self.theme, (x, y - sy / 2 - pos), (sx, 20), "No Channels Available", Input):
                    self.screen_pointer = "main_menu"
            else:
                for server in self.PyChat_servers:
                    if gui.button(self.theme, (x, y - sy/2-pos ), (sx, 20), server, Input):
                        self.channel_name = server
                        self.screen_pointer = "join"
                    pos -= 20
            if gui.button(self.theme, (x, y + sy/2-10), (sx, 20), "Back", Input):
                self.screen_pointer = "main_menu"

        elif self.screen_pointer == "channel_Creator":
            self.channel_name_gui.pos = (x,y-15)
            self.channel_name_gui.size = (sx,20)
            self.channel_name_gui.update(self.Input)
            self.channel_pass_gui.pos = (x,y+15)
            self.channel_pass_gui.size = (sx,20)
            self.channel_pass_gui.update(self.Input)

            if gui.button(self.theme, (x, y + sy/2-30), (sx, 20), "Create", Input):
                self.screen_pointer = "creating_channel"
                self.n.send({"packet": "new_PyChat","name":self.channel_name_gui.text,"password":self.channel_pass_gui.text})
            if gui.button(self.theme, (x, y + sy/2-10), (sx, 20), "Back", Input):
                self.screen_pointer = "main_menu"

        elif self.screen_pointer == "join":
            self.channel_pass_gui.pos = (x,y)
            self.channel_pass_gui.size = (sx,20)
            self.channel_pass_gui.update(self.Input)
            if gui.button(self.theme, (x, y + sy/2-10), (sx, 20), "Join", Input):
                self.n.send({"packet": "join_PyChat","name":self.channel_name,"password":self.channel_pass_gui.text})
            data = self.n.receive("join_PyChat")
            if data != None:
                if data["server"] == "bad password":
                    self.channel_pass_gui.text = "wrong password"
                else:
                    self.server_ID = data["server"]["ID"]
                    self.screen_pointer = "In_channel"


        elif self.screen_pointer == "creating_channel":
            data = self.n.receive("new_chat")
            if data != None:
                self.server_ID = data["server"]["ID"]
                self.screen_pointer = "In_channel"

        elif self.screen_pointer == "In_channel":
            self.pos= (x, y)
            self.size = (sx, sy)
            self.pychat_input.pos = (x-15,y+sy/2-7.5)
            self.pychat_input.size = (sx-30, 15)
            self.pointer += Input.scroll()
            if self.pointer < 0:
                self.pointer = 0
            if self.pointer > len(self.message_list):
                self.pointer = len(self.message_list)

            if time.perf_counter() > self.chat_refresh:
                self.chat_refresh = time.perf_counter() + 0.2
                if self.received:
                    self.received = False
                    self.n.send({"packet": "get_messages", "last message": self.last_message,"ID":self.server_ID})
                    self.sent = True
                if self.sent:
                    data = self.n.receive("messages")
                    if data != None:
                        self.received = True
                        self.sent = False
                        for message in data["messages"]:
                            if data["messages"][message]['message'][0] == "/":
                                if data["messages"][message]['message'] == "/clear":
                                    print("clear")
                                    self.messages = {}
                                    self.last_message = None
                                    self.message_list = []
                            else:
                                self.last_message = message
                                self.messages[message] = data["messages"][message]
                                self.message_list.append(message)

            pos = 15
            for time_stamp in self.message_list[self.pointer:]:
                self.theme.fonts(font_size = 8)
                time_stamp_list = str(time_stamp).split(":")
                time_ = f"{time_stamp_list[0]}:{time_stamp_list[1]} {time_stamp_list[-1]}"
                pos += 4
                gui.lable(self.theme, (x-sx/2 + 2, y + pos-sy/2),str(self.messages[time_stamp]["player"]) + " at " + time_, center="top_left")
                pos += 8
                self.theme.fonts(font_size = 12)

                message = self.messages[time_stamp]["message"]
                if self.theme.font.size(message)[0] > sx*self.scale-10:
                    line = ""
                    for each in message.split(" "):
                        if self.theme.font.size(line + each + " ")[0] > sx*self.scale-10:
                            gui.lable(self.theme, (x-sx/2 + 2, y + pos-sy/2), line, center="top_left")
                            line = ""
                            line += each + " "
                            pos += 13
                        else:
                            line += each + " "
                    gui.lable(self.theme, (x - sx / 2 + 2, y + pos - sy / 2), line, center="top_left")
                    pos += 13
                else:
                    gui.lable(self.theme, (x-sx/2 + 2, y + pos-sy/2),self.messages[time_stamp]["message"], center="top_left")
                    pos += 13
                if pos > y+sy-self.theme.font.size("Qq")[1]:
                    break
            self.pychat_input.update(Input)
            if gui.button(self.theme, (x+sx/2-15, y+sy/2-7.5), (30, 15), "Send", Input):
                self.n.send({"packet": "send_message", "message": self.pychat_input.get_text(), "player": self.player.name,"ID":self.server_ID})
                self.pychat_input.change_text("")
        return self.ping

