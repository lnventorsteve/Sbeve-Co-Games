import time
import pygame
from Network import Network
import json
import my_gui as gui
import math
import local_games
import multiplayer_games
import background as bgs
import os
import copy
import PyChat as pc
import traceback


def load_config():
    try:
        with open("conf.json", "r") as conf:
            config_ = json.loads(conf.read())
        config = {}
        config["scale"] = config_["scale"]
        config["current_w"], config["current_h"] = config_["screen size"]
        config["screen mode"] = config_["screen mode"]
        config['main_display'] = config_["main_display"]
        config['theme'] = config_["theme"]
        config["volume"] = config_["volume"]
        config["target_fps"] = config_["target_fps"]
        return config
    except:
        config = {}
        config["current_w"], config["current_h"] = 1920,1080
        config["scale"] = 2
        config["screen mode"] = "Windowed"
        config['main_display'] = 0
        config['theme'] = "Default theme"
        config["volume"] = 100
        config["target_fps"] = 20
        return config

class Player_class:
    def __init__(self):
        self.name = "No Name"
        self.position = 0
        self.color1 = (255, 0, 0)
        self.color2 = (0, 255, 0)
        self.color3 = (0, 0, 255)
        self.highScores = {}
        self.playTime = {}
        self.currentGames = {}

    def load_player(self,player):
        with open(f"playerdata/{player}","r") as player_info:
            player_info = json.loads(player_info.read())
        self.name = player_info["name"]
        self.position = player_info["position"]
        self.color1 = player_info["color1"]
        self.color2 = player_info["color2"]
        self.color3 = player_info["color3"]
        self.highScores = player_info["scores"]
        self.playTime = player_info["playtime"]

    def save_player(self):
        with open(f"playerdata/{self.name}.json","w") as player_info:
            dict_player = {}
            dict_player["name"] = self.name
            dict_player["position"] = self.position
            dict_player["color1"] = self.color1
            dict_player["color2"] = self.color2
            dict_player["color3"] = self.color3
            dict_player["scores"] = self.highScores
            playtime = {}
            for each in self.playTime:
                playtime[each] = round(self.playTime[each],2)
            dict_player["playtime"] = playtime
            player_info.write(json.dumps(dict_player))

def get_position(player):
    if player.position == 0:
        return  100
    return player.position

#init pygame
pygame.init()
pygame.mixer.init()
pygame.font.init()

pygame.display.set_caption("Sbeve Co Games")

#init some vars
p_frame = time.perf_counter()
fps = 0
menu_fps = 20
game_fps = 60
ping = "--"
done = False
keep_awake = p_frame
chat_refresh = p_frame
messages = []
connected = False
reconnecting = False
debug = False
setting = False
in_game = False
mpgame = False
pychat = False
reset_screen = False
reload_players = False
check_settings = False
resolutions = ("2560x1440","1920x1440","1920x1200","1920x1080","1680x1050","1600x1200","1600x1024","1600x900","1440x900","1366x768","1360x768","1280x1024","1280x960","1280x800","1280x768","1280x720","1152x864","1024x768","800x600")
data = None
frame = 0
n = Network()
chat = None

alpha = 255

#{"name": "player 1", "position": 1, "color1": [255, 0, 0], "color2": [0, 255, 0], "color3": [0, 0, 255], "scores": {}, "playtime": {}}

if __name__ == "__main__":
    config = load_config()
    theme = gui.Theme()
    theme.load_Theme(config)
    current_w = config["current_w"]
    current_h = config["current_h"]
    screen_mode = config["screen mode"]
    main_display = config["main_display"]
    volume = config["volume"]
    theme.sounds(volume=volume)
    scale = config["scale"]
    tcolor, bcolor, bgcolor = theme.colors()

    main_screen = ["main_menu"]
    sub_screen = ["main"]
    background = pygame.surface.Surface((current_w, current_h))
    bg = bgs.new_background(background,current_w,current_h)
    Input = gui.Input()


    if screen_mode == "Fullscreen":
        flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Fullscreen")
    elif screen_mode == "Borderless":
        flags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Borderless")
    else:
        flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Windowed")
    display = pygame.display.set_mode((current_w, current_h), flags, vsync=1, display=main_display)
    print(current_w, current_h)
    screen = (current_w / 2, current_h / 2)
    screen_info = (display, screen, scale)
    bg = bgs.new_background(display, current_w, current_h)
    theme.screen_info(screen_info)
    bg.reset()
    popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),"™ © Patent Pending Sbeve Co. Inc LLC")
    volume_gui = gui.slider(theme, (0, 0), (100, 15), "right", Input, volume)

    Players = []
    numofplayers = 0
    if os.listdir("playerdata") == []:
        new_player = Player_class()
        pos = -screen[1] / scale/2+35
        name = gui.lable_text(theme, (60, pos), (100, 20), "Name", "Enter name here")
        pos+=25
        color1 = gui.color_picker(theme, (60, pos), (100, 20), "color 1")
        pos += 25
        color2 = gui.color_picker(theme, (60, pos), (100, 20), "color 2")
        pos += 25
        color3 = gui.color_picker(theme, (60, pos), (100, 20), "color 3")
        pos += 25
        sub_screen.append("Force New player")


    for each in os.listdir("playerdata"):
        Players.append(Player_class())
        Players[numofplayers].load_player(each)
        numofplayers += 1
    Players.sort(key=get_position)

    for each in Players:
        if each.position == 1:
            player = each



    while not done:
#check if the scale has changed
        if reset_screen:
            reset_screen = False
            if screen_mode == "Fullscreen":
                flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Fullscreen")
            elif screen_mode == "Borderless":
                flags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Borderless")
            else:
                flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Windowed")
            display = pygame.display.set_mode((current_w, current_h), flags, vsync=1, display=main_display)
            print(current_w, current_h)
            screen = (current_w / 2, current_h / 2)
            screen_info = (display, screen, scale)
            try:
                bg = bgs.new_background(display, current_w, current_h)
            except:
                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,(300, 15), "Error creating Background")
            theme.screen_info(screen_info)
            theme.sounds(volume=volume)
            if pychat:
                chat.reload()
            bg.reset()
#reload all players
        if reload_players:
            reload_players = False
            for each in Players:
                each.save_player()
            Players = []
            numofplayers = 0
            for each in os.listdir("playerdata"):
                Players.append(Player_class())
                Players[numofplayers].load_player(each)
                numofplayers += 1
            Players.sort(key=get_position)

            for each in Players:
                if each.position == 1:
                    player = each
            if chat != None:
                chat.player = player

    #user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.VIDEORESIZE:
                reset_screen = True
                current_w = event.w
                current_h = event.h

            Input.get_input(event,frame)
        Input.update(frame)

        if main_screen == []:
            main_screen = ["main_menu"]
        if sub_screen == []:
            sub_screen = ["main"]

        for key in Input.keys:
            if key == 27:
                pygame.mixer.Sound.play(theme.sounds("button"))
                if main_screen[-1] == "main_menu" or in_game and main_screen[-1] != "settings":
                    main_screen.append("settings")
                    sub_screen = ["main"]
                else:
                    if sub_screen[-1] != "main":
                        sub_screen.pop()
                    else:
                        main_screen.pop()

            if key == 1073741884:
                debug = not debug

            if key == 1073741892:
                if screen_mode == "Fullscreen":
                    screen_mode = "Windowed"
                else:
                    screen_mode = "Fullscreen"
                reset_screen = True

            if key == 9:
                pychat = not pychat
                if chat == None:
                    chat = pc.chat(theme, n, Input, player)

#main screen

        display.fill((0, 0, 0))
        if not in_game:
            try:
                bg = bg.update()
            except:
                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),"Error updating Background")
        try:
#main menu

            if not in_game:
                if pychat:
                    if not n.is_connected():
                        n.connect()
                        if not n.is_connected():
                            pychat = False
                            popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25* scale), (0, -current_h / (2 * scale) + 15), 2, 3, (300, 15), "Failed to connect to server")
                    else:
                        if chat.update(Input) == "close":
                            pychat = False

                if main_screen[-1] == "main_menu":
                    temp = theme.font
                    theme.font = pygame.font.SysFont("impact", 30 * scale)
                    gui.lable(theme, (0, -current_h / (2 * scale) + 50), "Sbeve Co Games", in_box=True, size=(350, 40))
                    theme.font = temp
                    if sub_screen[-1] == "main":
                        if gui.button(theme, (0, -75), (100, 20), "Edit Player", Input):
                            main_screen.append("Edit")

                        if gui.button(theme, (0, -50), (100, 20), "Resume", Input):
                            main_screen.append("resume")
                            currentgames = []
                            for each in os.listdir("saves/Current Games/"):
                                with open(f"saves/Current Games/{each}","r") as file:

                                    currentgames.append(json.dumps(file.read()))
                            print(currentgames)

                        if gui.button(theme, (0, -25), (100, 20), "Random Game", Input):
                            main_screen.append("random")

                        if gui.button(theme, (0, 0), (100, 20), "Multiplayer", Input):
                            if not n.is_connected():
                                n.connect()
                            if n.is_connected():
                                main_screen.append("multiplayer")
                                servers = []
                            else:
                                popUp = gui.pop_up(theme,(0,-current_h/(2*scale)-25),(0,-current_h/(2*scale)+15),2,3,(300,15),"Failed to connect to server!")

                        if gui.button(theme, (0, 25), (100, 20), "Local Games",Input):
                            localGames = ["Game of Life","Dot Game","Snake","Connect 4","Flappy Bird"]#,"Tic Tac Toe","Hangman","Cookie Clicker",
                            main_screen.append("local_games")


                        if gui.button(theme, (0, 50), (100, 20), "Settings", Input):
                            main_screen.append("settings")

                        if gui.button(theme, (0, 75), (100, 20), "Quit", Input):
                            done = True

                    if sub_screen[-1] == "Force New player":
                        gui.box(theme, (0, 0), (230, screen[1] / scale))
                        gui.lable(theme, (0, -screen[1] / scale/2 + 10), "Create a New Player", in_box=True, size=(230, 20))
                        gui.lable_text.update(name, Input)
                        new_player.name = name.text
                        new_player.color1 = color1.get_color(Input)
                        new_player.color2 = color2.get_color(Input)
                        new_player.color3 = color3.get_color(Input)

                        if gui.button(theme, (0, screen[1] / scale/2 - 10), (230, 20), "Save", Input):
                            new_player.position = 1
                            new_player.save_player()
                            Players = []
                            numofplayers = 0
                            for each in os.listdir("playerdata"):
                                Players.append(Player_class())
                                Players[numofplayers].load_player(each)
                                numofplayers += 1
                            Players.sort(key=get_position)

                            for each in Players:
                                if each.position == 1:
                                    player = each
                            sub_screen.pop()

                elif main_screen[-1] == "local_games":
                    gui.lable(theme, (0, -current_h / (2 * scale) + 50), "Local Games", in_box=True, size=(150, 20))
                    if sub_screen[-1] == "main":
                        pos = 15-(screen[1] / scale)/2
                        gui.box(theme, (0, 0), (200, screen[1] / scale))
                        for game in localGames:
                            if gui.button(theme, (0, pos), (100, 20), game, Input):
                                sub_screen.append(game)
                            pos += 25

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            main_screen.pop()

                    elif sub_screen[-1] == "Game of Life":
                        game = local_games.Game_of_Life(theme,Input,Players)
                        in_game = True
                        sub_screen.pop()

                    elif sub_screen[-1] == "Dot Game":
                        game = local_games.Dot_Game(theme,Input,Players)
                        in_game = True
                        sub_screen.pop()

                    elif sub_screen[-1] == "Snake":
                        game = local_games.Snake(theme,Input,Players)
                        in_game = True
                        sub_screen.pop()

                    elif sub_screen[-1] == "Connect 4":
                        game = local_games.Connect_4(theme, Input, Players)
                        in_game = True
                        sub_screen.pop()

                    elif sub_screen[-1] == "Tic Tac Toe":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Hangman":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Cookie Clicker":
                        game = local_games.cookie_clicker(theme,Input,player)
                        in_game = True
                        sub_screen.pop()
                    elif sub_screen[-1] == "Flappy Bird":
                        game = local_games.bird(theme,Input,Players)
                        in_game = True
                        config["target_fps"] = game_fps
                        sub_screen.pop()
                    else:
                        if main_screen[-2] =="resume":
                            main_screen.pop()
                        sub_screen = ["main"]

                elif main_screen[-1] == "multiplayer":

                    if sub_screen[-1] == "main":
                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            main_screen.pop()

                        gui.lable(theme, (0, -current_h / (2 * scale) + 50), "Multiplayer", in_box=True, size=(150, 20))
                        gui.box(theme,(0,0),(200,screen[1]/scale))
                        if gui.button(theme,(-25,(screen[1]/scale)/2-10),(150,20),"New Server",Input):
                            sub_screen.append("create_server")
                            multiplayerGames = ["Snake"] # ["Dot Game","Snake","Connect 4","Flappy Bird"]

                        if gui.button(theme,(75,(screen[1]/scale)/2-10),(50,20),"Refresh",Input):
                            n.send({"packet": "get_servers"})

                        data = n.receive("servers")

                        if data != None:
                            servers = data["servers"]

                        pos = 15 - (screen[1] / scale) / 2
                        for each in servers:
                            if gui.button(theme, (0,pos), (100,20), str(each["name"]), Input):
                                sub_screen.append("join_server")
                                properties_window = gui.window(theme,(0,0),(240, screen[1] / scale),"Properties",Input,resizeable=True,min = (240,40))
                                n.send({"packet": "get_server_info","server":each["ID"]})
                                server_ID = each["ID"]
                                server = {}
                            pos += 25

                    elif sub_screen[-1] == "join_server":
                        x,y,sx,sy,button = properties_window.update()
                        data = n.receive("server_info")
                        if data != None:
                            server = data["server_info"]
                        pos = y - sy/2 + 30
                        for each in server:
                            gui.lable(theme, (x-60, pos), str(each),in_box=True, size = (100, 20))
                            gui.lable(theme, (x+60, pos), str(server[each]), in_box=True, size=(100, 20))
                            pos += 25
                            if pos > y+sy/2-20:
                                break
                        if gui.button(theme, (x,y+sy/2-10 ), (sx, 20), "join", Input):
                            n.send({"packet": "join_server", "server": server_ID ,"name":player.name})
                        data = n.receive("join_server")
                        if data != None:
                            clients = data["clients"]
                            sub_screen[-1] = f"join_{server['Name']}"



                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input) or button != None:
                            sub_screen.pop()

                    elif sub_screen[-1] == "create_server":
                        gui.lable(theme, (0, -current_h / (2 * scale) + 50), "New Server", in_box=True, size=(150, 20))
                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            sub_screen.pop()
                        gui.box(theme, (0, 0), (200, screen[1] / scale))
                        pos = 15 - (screen[1] / scale) / 2
                        for game in multiplayerGames:
                            if gui.button(theme, (0, pos), (100, 20), game, Input):
                                sub_screen.append(game)
                            pos += 25

                    elif sub_screen[-1] == "join_Snake":
                        game = multiplayer_games.Snake(theme, Input, Players,n)
                        game.setup_ = True
                        game.join_ = True
                        mpgame = True
                        game.clients = clients
                        game.server_ID = server_ID
                        n.send({"packet": "get_data", "server": server_ID, "key": "server_info"})
                        in_game = True
                        sub_screen.pop()
                        sub_screen.pop()

                    elif sub_screen[-1] == "Snake":
                        game = multiplayer_games.Snake(theme, Input, Players,n)
                        in_game = True
                        mpgame = True
                        sub_screen.pop()

                    elif sub_screen[-1] == "Dot Game":
                        game = multiplayer_games.Dot_Game(theme, Input, Players,n)
                        in_game = True
                        mpgame = True
                        sub_screen.pop()

                elif main_screen[-1] == "random":
                    gui.lable(theme, (0, -current_h / (2 * scale) + 50), "Random Game", in_box=True, size=(150, 20))
                    gui.box(theme,(0,0),(200,screen[1]/scale))
                    if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                        main_screen.pop()

                elif main_screen[-1] == "resume":
                    if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                        if sub_screen[-1] == "main":
                            main_screen.pop()
                        else:
                            sub_screen.pop()

                    if sub_screen[-1]  == "main":
                        gui.lable(theme, (0, -current_h / (2 * scale) + 50), "Resume Game", in_box=True, size=(150, 20))
                        gui.box(theme,(0,0),(200,screen[1]/scale))
                        if currentgames == []:
                            gui.lable(theme, (0, -screen[1] / (2 * scale)+25), "No Games Found", in_box=True, size=(150, 20))

                        pos=25
                        for each in currentgames:
                            game = each.strip('"{\\"Game\\":\\"')
                            game = game.strip('\\"}"')
                            if gui.button(theme, (0, -screen[1]/(2 * scale) + pos), (150, 20), game,Input):
                                sub_screen.append(game)
                            pos+= 25

                    elif sub_screen[-1] == "Game of Life":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Dot Game":
                        game = local_games.Dot_Game(theme, Input, Players)
                        game.load()
                        in_game = True
                        mpgame = False
                        sub_screen.pop()

                    elif sub_screen[-1] == "Snake":
                        game = local_games.Snake(theme, Input, Players)
                        in_game = True
                        mpgame = False
                        sub_screen.pop()

                    elif sub_screen[-1] == "Connect 4":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Tic Tac Toe":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Hangman":
                        sub_screen.pop()

                    elif sub_screen[-1] == "Cookie Clicker":
                        game = local_games.cookie_clicker(theme, Input, player)
                        in_game = True
                        mpgame = False
                        sub_screen.pop()

                    elif sub_screen[-1] == "Flappy Bird":
                        game = local_games.bird(theme, Input, Players)
                        in_game = True
                        mpgame = False
                        config["target_fps"] = game_fps
                        sub_screen.pop()

                elif main_screen[-1]  == "Edit":
                    gui.lable(theme, (0, -current_h / (2 * scale) + 75), "Player Editor", in_box=True, size=(150, 20))
                    if sub_screen[-1] == "main":
                        if gui.button(theme, (0, -75), (100, 20), "New Player", Input):
                            new_player = Player_class()
                            pos = -screen[1] / scale / 2 + 35
                            name = gui.lable_text(theme, (60, pos), (100, 20), "Name", "Enter name here")
                            pos += 25
                            color1 = gui.color_picker(theme, (60, pos), (100, 20), "color 1")
                            pos += 25
                            color2 = gui.color_picker(theme, (60, pos), (100, 20), "color 2")
                            pos += 25
                            color3 = gui.color_picker(theme, (60, pos), (100, 20), "color 3")
                            pos += 25
                            sub_screen.append("New player")

                        if gui.button(theme, (0, -50), (100, 20), "Change Player", Input):
                            sub_screen.append("player picker")

                        if gui.button(theme, (0, -25), (100, 20), "Edit Players", Input):
                            sub_screen.append("edit player")

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            main_screen.pop()

                    elif sub_screen[-1] == "player picker":
                        pos = -numofplayers*12.5
                        i = 1
                        for player in Players:
                            if gui.button(theme, (0, pos), (200, 20),"Player "+str(i)+" = "+player.name, Input):
                                current_player = player
                                sub_screen.append("pick")
                            pos += 25
                            i += 1

                        if gui.button(theme, (0, current_h / (2 * scale) - 40), (100, 20), "Apply", Input):
                            for each in Players:
                                each.save_player()
                            reload_players = True
                            sub_screen.pop()

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            reload_players = True
                            sub_screen.pop()

                    elif sub_screen[-1] == "pick":
                        pos = -numofplayers * 12.5
                        i = 1
                        for player in Players:
                            if gui.button(theme, (0, pos), (100, 20), player.name, Input):
                                old_spot = player.position
                                new_spot = current_player.position
                                current_player.position = old_spot
                                player.position = new_spot
                                Players.sort(key=get_position)
                                reload_players = True
                                sub_screen.pop()
                            pos += 25
                            i += 1

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            sub_screen.pop()

                    elif sub_screen[-1] == "edit player":
                        pos = -numofplayers*12.5
                        i = 1
                        for player in Players:
                            if gui.button(theme, (0, pos), (100, 20),player.name, Input):
                                current_player = player
                                name = gui.lable_text(theme, (60, -25), (100, 20), "Name", current_player.name )
                                color1 = gui.color_picker(theme, (60, 0), (100, 20), "color 1",current_player.color1)
                                color2 = gui.color_picker(theme, (60, 25), (100, 20), "color 2",current_player.color2)
                                color3 = gui.color_picker(theme, (60, 50), (100, 20), "color 3",current_player.color3)
                                sub_screen.append("edit")
                            pos += 25
                            i += 1

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            sub_screen.pop()

                    elif sub_screen[-1] == "edit":
                        gui.lable_text.update(name,Input)
                        current_player.color1 = color1.get_color(Input)
                        current_player.color2 = color2.get_color(Input)
                        current_player.color3 = color3.get_color(Input)

                        if gui.button(theme, (-60, 75), (100, 20), "Delete Player", Input):
                            if gui.alert(theme, (0, 0), (300, 200), f"Are you sure you want to PERMANENTLY delete {current_player.name} forever! This will delete all player data!", "Yes", "No",Input, frame):
                                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),f"{current_player.name} has been deleted!")
                                os.remove(f"playerdata/{current_player.name}.json")
                                Players.remove(current_player)
                                reload_players = True
                                sub_screen.pop()


                        if gui.button(theme, (60, 75), (100, 20), "Clear Saved Data", Input):
                            if gui.alert(theme, (0, 0), (300, 200), f"Are you sure you want to PERMANENTLY delete {current_player.name}'s Save data forever! This will delete high scores and playtime!", "Yes", "No",Input, frame):
                                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),f"Clear {current_player.name}'s saved data!")
                                current_player.highScores = {}
                                current_player.currentGames = {}
                                current_player.playTime = {}
                                reload_players = True



                        if gui.button(theme, (0, current_h / (2 * scale) - 40), (100, 20), "Apply", Input):
                            current_player.name = name.text
                            current_player.save_player()
                            reload_players = True
                            sub_screen.pop()

                        if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                            sub_screen.pop()

                    elif sub_screen[-1] == "New player":
                        gui.box(theme, (0, 0), (230, screen[1] / scale))
                        gui.lable(theme, (0, -screen[1] / scale / 2 + 10), "Create a New Player", in_box=True,
                                  size=(230, 20))
                        gui.lable_text.update(name, Input)
                        new_player.name = name.text
                        new_player.color1 = color1.get_color(Input)
                        new_player.color2 = color2.get_color(Input)
                        new_player.color3 = color3.get_color(Input)

                        if gui.button(theme, (57, screen[1] / scale / 2 - 10), (115, 20), "Save", Input):
                            new_player.save_player()
                            reload_players = True
                            sub_screen.pop()

                        if gui.button(theme, (-57, screen[1] / scale / 2 - 10), (115, 20), "Cancel", Input):
                            sub_screen.pop()

                    else:
                        popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2,3, (300, 20), "error 404; " + sub_screen[-1] + " not found")
                        sub_screen.pop()
                        continue

                elif main_screen[-1] == "Test":
                    gui.lable(theme, (0, -current_h / (2 * scale) + 75), "Test Area", in_box=True, size=(150, 20))
                    if gui.button(theme, (0, -50), (100, 15), "connect to server", Input):
                        n.connect()

                    if gui.button(theme, (0, 50), (100, 20), "get servers", Input):
                        n.send({"packet":"get_servers"})

                    if gui.button(theme, (0, 75), (100, 20), "print servers", Input):
                        print(n.receive("servers"))


                    if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                        main_screen.pop()

                # Fonts menu
                elif main_screen[-1] == "fonts":
                    fonts.update(Input)
                    font_size.update(Input)

                    if gui.button(theme, (0, current_h / (2 * scale) - 40), (100, 20), "Apply", Input):
                        theme.fonts(gui.get_text(fonts),int(gui.get_text(font_size)))

                    if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                        main_screen.pop()

                else:
                    if main_screen[-1] != "settings":
                        popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),"error 404; " + main_screen[-1] + " not found")
                        main_screen.pop()
                        continue

            else:
                if main_screen[-1] != "settings":
                    if not game.setup_:
                        if game.setup():
                            sub_screen.pop()
                            in_game = False
                    elif mpgame:
                        if game.join_:
                            game.join()
                    else:
                        button = game.update()
                        if button == "settings":
                            main_screen.append("settings")
                        elif button == "exit":
                            sub_screen.pop()
                            game.exit()
                            in_game = False
    #setting screen
            if main_screen[-1] == "settings":
                if sub_screen[-1] == "main":
                    if in_game:
                        button = game.settings()
                        if button == "exit":
                            main_screen.pop()
                            game.exit()
                            in_game = False
                        elif button == "save exit":
                            game.save_exit()
                            main_screen.pop()
                            in_game = False
                        elif button == "back":
                            main_screen.pop()
                    else:

                        if gui.button(theme, (0, 25), (100, 20), "Video Setting", Input):
                            sub_screen.append("Video Setting")
                            scale_box = gui.lable_text(theme, (60, 0), (100, 20), "GUI Scale", scale)
                            screen_size = gui.multiple_choice_input(theme, (60, -25), (100, 20), 'Resolution', str(current_w) + "x" + str(current_h), resolutions, 5)
                            window_modes = ["Fullscreen", "Windowed", "Borderless"]
                            window_mode = gui.multiple_choice_input(theme, (60, 25), (100, 20), 'Window Mode', screen_mode, window_modes, 5)

                        if gui.button(theme, (0, 50), (100, 20), "New Theme", Input):
                            sub_screen.append("Edit Theme")
                            name = gui.lable_text(theme,(60,-50),(100,20),"Theme Name","Enter Name")
                            t_color = gui.color_picker(theme, (60, -25), (100, 20), "Text color", color=tcolor)
                            b_color = gui.color_picker(theme, (60, 0), (100, 20), "Text border", color=bcolor)
                            bg_color = gui.color_picker(theme, (60, 25), (100, 20), "Text background", color=bgcolor)

                        if gui.button(theme, (0, 0), (100, 20), "Manage Themes", Input):
                            sub_screen.append("Themes")

                        if gui.button(theme, (0, -25), (100, 20), "Audio", Input):
                            sub_screen.append("audio")

                if sub_screen[-1] == "audio":
                    gui.lable_value(theme,(0,25),"Volume = ", volume,in_box = True,size = (100,20))
                    volume_gui.update()
                    v = int(volume_gui.value*100)
                    theme.sounds(volume=v)
                    volume = v

                elif sub_screen[-1] == "Video Setting":
                    gui.lable_text.update(scale_box,Input)
                    screen_size.update(Input)
                    window_mode.update(Input)

                    if gui.button(theme, (0, current_h/(2*scale)-65), (100, 20), "Apply", Input):
                        if gui.get_text(scale_box).isnumeric():
                            if int(gui.get_text(scale_box)) < 10:
                                scale = int(gui.get_text(scale_box))
                        w,h = gui.get_text(screen_size).split("x")
                        current_w, current_h = int(w),int(h)
                        screen_mode = gui.get_text(window_mode)
                        print(screen_mode)
                        reset_screen = True
                        check_settings = True
                        continue

                elif sub_screen[-1] == "Themes":
                    path = theme.path
                    Themes = os.listdir(f"{path}/Themes")
                    new_Theme = config["theme"]
                    pos = -math.floor(len(Themes) / 2) * 25
                    for Theme in Themes:
                        Theme = Theme[:-5]
                        theme.change_Theme(Theme)
                        theme.sounds(volume=volume)
                        if gui.button(theme, (0, pos), (100, 20), Theme, Input):
                            config["theme"] = Theme
                        if gui.button(theme, (-100, pos), (60, 20), "Edit", Input):
                            edit_theme = gui.Theme()
                            edit_theme.load_Theme(config,Theme)
                            name = gui.lable_text(theme,(60,-50),(100,20),"Theme Name",Theme)
                            t_color = gui.color_picker(theme, (60, -25), (100, 20), "Text color", edit_theme.tcolor)
                            b_color = gui.color_picker(theme, (60, 0), (100, 20), "Text border", edit_theme.bcolor)
                            bg_color = gui.color_picker(theme, (60, 25), (100, 20), "Text background", edit_theme.bgcolor)
                            sub_screen.append("Edit Theme")
                        if gui.button(theme, (100, pos), (60, 20), "Remove", Input):
                            if gui.alert(theme, (0, 0), (150, 100), f"Are you sure you want to PERMANENTLY delete {Theme} forever!", "Yes", "No", Input, frame):
                                        popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),f"{Theme} has been deleted!")
                                        os.remove(f"{path}/Themes/{Theme}.json")
                                        Themes.remove(f"{Theme}.json")
                                        print(Themes)
                                        config["theme"] = new_Theme = Themes[0][:-5]
                        pos += 25
                    theme.change_Theme(new_Theme)

                elif sub_screen[-1] == "Edit Theme":
                    name.update(Input)
                    tcolor = t_color.get_color(Input)
                    bcolor = b_color.get_color(Input)
                    bgcolor = bg_color.get_color(Input)

                    if gui.button(theme, (0, 50), (100, 20), "Font", Input):
                        all_fonts = os.listdir(r'C:\Windows\fonts')
                        fonts = []
                        for font in all_fonts:
                            if font[-3:] == "ttf":
                                fonts.append(font[:-4])
                        fonts = gui.multiple_choice_input(theme,(0,0),(100,20),"font",theme.font_name,fonts,20)
                        font_size = gui.lable_text(theme,(0,25),(100,20),"Font Size",12)
                        main_screen.append("fonts")

                    if gui.button(theme, (0, current_h / (2 * scale) - 65), (100, 20), "Save Theme", Input):
                        new_theme = gui.Theme()
                        new_theme.screen_info(screen_info)
                        new_theme.colors((tcolor, bcolor, bgcolor))
                        new_theme.sound_info = theme.sound_info
                        new_theme.font_name = theme.font_name
                        new_theme.font_size = theme.font_size
                        try:
                            with open("Themes//" + str(name.text) + ".json", "w") as file:
                                file.write(json.dumps(new_theme.save_Theme()))
                                sub_screen.pop()
                            reset_screen = True
                        except Exception as e:
                            traceback.print_exc()
                            popUp = gui.pop_up(theme,(0,-current_h/(2*scale)-25),(0,-current_h/(2*scale)+15),2,3,(300,15),f"Unable to save {name.text}. Error : {e}")
                gui.lable(theme, (0, -current_h / (2 * scale) + 75), "Settings", in_box=True, size=(150, 20))

                if gui.button(theme, (0, current_h / (2 * scale) - 40), (100, 20), "Quit To Desktop", Input):
                    done = True

                if gui.button(theme, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                    if sub_screen[-1] == "main":
                        main_screen.pop()
                    else:
                        sub_screen.pop()
                        theme.sounds(volume=volume)

        except Exception as e:
            traceback.print_exc()
            in_game = False
            if main_screen == []:
                main_screen.append("main_menu")
            elif sub_screen == []:
                sub_screen.append("main")
            else:
                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 10, (-1, 15),f"Error in {main_screen[-1],sub_screen[-1]}. Error : {e}")
                if sub_screen == "main":
                    main_screen.pop()
                else:
                    sub_screen.pop()


#debug screen
        if debug:
            if gui.button(theme, (-current_w/(2*scale)+15,current_h/(2*scale)-7.5 ), (30, 20), "Test", Input):
                main_screen.append("Test")
            gui.lable_value(theme, (0-current_w/(2*scale), 0-current_h/(2*scale)), "ping=", ping , center = "top_left", in_box = False)
            gui.lable_value(theme, (0-current_w/(2*scale), 15-current_h/(2*scale)), "fps=", f"{round(fps,2)}/{config['target_fps']}", center ="top_left", in_box = False)
            gui.lable_value(theme, (0 - current_w / (2 * scale), 30 - current_h / (2 * scale)), "Active Keys=",Input.Keys_pressed,center="top_left", in_box=False)
            gui.lable_value(theme, (0 - current_w / (2 * scale), 45 - current_h / (2 * scale)), "Mouse",Input.mouse(),center="top_left", in_box=False)
            pygame.draw.line(display,(255,0,0),(0,screen[1]),(screen[0]*2,screen[1]))
            pygame.draw.line(display, (255, 0, 0), (screen[0],0), (screen[0], screen[1]*2))

        # pop ups
        popUp.update()
        try:
            time.sleep((p_frame+1/config["target_fps"])-time.perf_counter())
        except:
            pass
        fps = 1 / (time.perf_counter() - p_frame)
        p_frame = time.perf_counter()
        pygame.display.update()
        frame+=1

# make sure that video setting are usable
        if check_settings:
            check_settings = False
            if gui.alert(theme, (0, 0), (150, 100), "Do you want to save these settings?", "Yes", "No", Input, frame, 15):
                config["scale"] = scale
                config["screen size"] = [current_w, current_h]
                with open("conf.json", "w") as conf:
                    conf.write(json.dumps(config))
                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,
                                   (300, 15), "Setting Updated")
                sub_screen.pop()
            else:
                config = load_config()
                current_w = config["current_w"]
                current_h = config["current_h"]
                screen_mode = config["screen mode"]
                main_display = config["main_display"]
                scale = config["scale"]
                reset_screen = True
                popUp = gui.pop_up(theme, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,
                                   (300, 15), "Setting Reverted")

#exit code
config["screen mode"] = screen_mode
config["scale"] = scale
config["screen size"] = [current_w,current_h]
config.pop("current_w")
config.pop("current_h")
config["volume"] = volume


with open("conf.json", "w") as conf:
    conf.write(json.dumps(config))

if n.is_connected():
    n.send({"packet": "disconnect"})
    data = None
    timeout = time.perf_counter()+1
    while data == None or time.perf_counter() > timeout:
        data = n.receive("disconnected")
        time.sleep(0.1)
    if  data["packet"] == "disconnected":
        print("Disconnected form server")


for player in Players:
    player.save_player()

time.sleep(0.2)
print("done")