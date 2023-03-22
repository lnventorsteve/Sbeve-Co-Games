import socket
from _thread import *
import time
import json
import os
import math
import random
from datetime import datetime
import traceback

with open ("Server/config.txt","r") as config:
    server = config.readline().split(" = ")[-1].strip("\n")
    port = int(config.readline().split(" = ")[-1])

print(server,port)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

bound = False
while not bound:
    try:
        s.bind((server, port))
        print("bound port " + str(port))
        bound = True
    except socket.error as e:
        print("failed to bind to port "+str(port))
        print(e)


s.listen()

print("Waiting for a connection, Server Started")


class Player_class:
    def __init__(self):
        self.name = "No Name"
        self.color1 = (255, 0, 0)
        self.color2 = (0, 255, 0)
        self.color3 = (0, 0, 255)
        self.score = 0


def client(conn,addr,client_ID):
    global servers
    global clients
    reply = "null"
    data = ""
    Connected = True
    def add_message(data):
        name = data["player"]
        new_message = data["message"]
        new_message = (new_message.split('\\n'))
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S:%f:%p")
        servers[data["ID"]]["messages"][current_time] = {}
        for message in new_message:
            servers[data["ID"]]["messages"][current_time]["message"] = message
            servers[data["ID"]]["messages"][current_time]["player"]  = name
            servers[data["ID"]]["message_list"].append(current_time)

    def sort_servers_by_ID(server):
        return server["ID"]

    def leave_snake(client,server):
        client_name = servers[server]["clients"][client]
        servers[server]["Snakes"].pop(client_name)
        servers[data["server"]]["clients"].pop(client)


    while Connected:
        try:
            _data = conn.recv(2048).decode("utf-8")
            if _data == "":
                print(addr, "disconnected", "at", datetime.now().strftime("%I:%M:%S%p"))
                clients.remove(addr)
                break
            else:
                _data = _data.split("&")
                reply = ""
                for each in _data:
                    if each == "":
                        break
                    data = json.loads(each)
# ping server

                    if data["packet"] == "ping":
                        reply += '{"packet":"ping"}&'
# server management
                    elif data["packet"] == "get_server_info":
                        reply += json.dumps({"packet": "server_info", "server_info": servers[data["server"]]["server_info"]}) + "&"

# join a game server
                    elif data["packet"] == "join_server":
                        servers[data["server"]]["clients"][client_ID] = data["name"]
                        reply += json.dumps({"packet":"join_server","clients":servers[data["server"]]["clients"]}) + "&"

# Leave a game server
                    elif data["packet"] == "leave_server":
                        name = servers[data["server"]]["server_info"]["Name"]
                        if name == "Snake":
                            leave_snake(client_ID,data["server"])
                        reply += json.dumps({"packet":"leave_server"}) + "&"

# create new server
                    elif data["packet"] == "new_server":
                        server_IDs = []
                        for server in servers:
                            server_IDs.append(server["ID"])

                        server_ID = 0
                        while server_ID in server_IDs:
                            server_ID += 1
                        server = {"ID":server_ID,"clients":{}}
                        servers.append(server)
                        reply += json.dumps({"packet":"new_server","server":server}) + "&"

# get server list
                    elif data["packet"] == "get_servers":
                        server_list = []
                        for server in servers:
                            if server["server_info"]["Type"] == "game":
                                server_list.append({"name":server["server_info"]["Name"],"ID":server["ID"]})
                        reply += json.dumps({"packet": "servers", "servers": server_list}) + "&"

# server data
                    elif data["packet"] == "add_data":
                        servers[data["server"]][data["key"]] = data["data"]
                    elif data["packet"] == "add_data_to_dict":
                        servers[data["server"]][data["key"]][data["key2"]] = data["data"]
                    elif data["packet"] == "append_data":
                        temp = servers[data["server"]][data["key"]]
                        temp.append(data["data"])
                        servers[data["server"]][data["key"]] = temp
                    elif data["packet"] == "remove_data":
                        servers[data["server"]].remove(data["key"])
                    elif data["packet"] == "pop_data":
                        temp = servers[data["server"]][data["key"]]
                        temp.pop()
                        servers[data["server"]][data["key"]] = temp

                    elif data["packet"] == "get_data":
                        reply += json.dumps({"packet": data["key"], "data": servers[data["server"]][data["key"]]}) + "&"
#snake
                    elif data["packet"] == "snake_data":
                        servers[data["server"]]["Snakes"][data["name"]] = {}
                        servers[data["server"]]["Snakes"][data["name"]]["snake"] = data["snake"]
                        servers[data["server"]]["Snakes"][data["name"]]["direction"] = data["direction"]
                        servers[data["server"]]["Snakes"][data["name"]]["body"] = data["body"]
                        servers[data["server"]]["Snakes"][data["name"]]["eyes"] = data["eyes"]
                        snakes_to_send = {}
                        for snake in servers[data["server"]]["Snakes"]:
                            if snake != data["name"]:
                                snakes_to_send[snake] = servers[data["server"]]["Snakes"][snake]

                        reply += json.dumps({"packet": "snake_data", "Snakes": snakes_to_send,"Apples":servers[data["server"]]["Apples"]}) + "&"

                    elif data["packet"] == "ate_apple":
                        ax ,ay = data["apple"]
                        apple = []
                        apple.append(ax)
                        apple.append(ay)
                        servers[data["server"]]["Apples"].remove(apple)
                        timeout = time.perf_counter() + 0.08
                        ax = random.randrange(0, servers[data["server"]]["server_info"]["Grid"][0])
                        ay = random.randrange(0, servers[data["server"]]["server_info"]["Grid"][1])
                        snakes_ = []
                        for name in servers[data["server"]]["Snakes"]:
                            for each in servers[data["server"]]["Snakes"][name]["snake"]:
                                ex, ey = each
                                snakes_.append((ex, ey))
                        while (ax, ay) in snakes_:
                            ax = random.randrange(0, servers[data["server"]]["server_info"]["Grid"][0])
                            ay = random.randrange(0, servers[data["server"]]["server_info"]["Grid"][1])
                            if time.perf_counter() > timeout:
                                ax = -1
                                ay = -1
                                break
                        apple = []
                        apple.append(ax)
                        apple.append(ay)
                        servers[data["server"]]["Apples"].append(apple)


# PyChat
                    elif data["packet"] == "new_PyChat":
                        server_IDs = []
                        for server in servers:
                            server_IDs.append(server["ID"])

                        server_ID = 0
                        while server_ID in server_IDs:
                            server_ID += 1
                        server = {}
                        server["ID"] = server_ID
                        server["server_info"] = {}
                        server["server_info"]["Name"] = data["name"]
                        server["server_info"]["Type"] =  "PyChat"
                        server["password"] = data["password"]
                        server["message_list"] = []
                        server["messages"] = {}
                        servers.append(server)
                        servers.sort(key=sort_servers_by_ID)

                        reply += json.dumps({"packet":"new_chat","server":server}) + "&"

                    elif data["packet"] == "get_PyChats":
                        PyChat_servers = []
                        for server in servers:
                            if server["server_info"]["Type"] == "PyChat":
                                PyChat_servers.append(server["server_info"]["Name"])
                        reply += json.dumps({"packet": "PyChat_servers", "servers": PyChat_servers}) + "&"

                    elif data["packet"] == "join_PyChat":
                        reply = json.dumps({"packet": "join_PyChat", "server": "bad password"})
                        for server in servers:
                            if server["server_info"]["Name"] == data["name"] and server["password"] == data["password"]:
                                reply = json.dumps({"packet": "join_PyChat", "server": server}) + "&"
                                break


                    elif data["packet"] == "send_message":
                        if data["message"] != "":
                            if data["message"][0] == "/":
                                if data["message"] == "/clear":
                                    servers[data["ID"]]["messages"] = {}
                                    add_message(data)
                                else:
                                    now = datetime.now()
                                    current_time = now.strftime("%I:%M:%S:%f:%p")
                                    servers[data["ID"]]["messages"][current_time] = {}
                                    servers[data["ID"]]["messages"][current_time]["message"] = f"{data['message'][1:]} is an unknown command use /help to see all commands"
                                    servers[data["ID"]]["messages"][current_time]["player"] = "Server"
                                    servers[data["ID"]]["message_list"].append(current_time)
                            else:
                                add_message(data)



                    elif data["packet"] == "get_messages":
                        if data["last message"] == None:
                            i=0
                        else:
                            try:
                                i = servers[data["ID"]]["message_list"].index(data["last message"])+1
                            except:
                                i = 0
                        messages_to_send = servers[data["ID"]]["message_list"][i:]
                        m = {}
                        for message in messages_to_send:
                            m[message] = servers[data["ID"]]["messages"][message]
                        message = {"packet": "messages" ,"messages":m}
                        reply += json.dumps(message)  + "&"

# Disconnect from server

                    elif data["packet"] == "disconnect":
                        print(f"disconnecting form {addr} at {datetime.now().strftime('%I:%M:%S%p')}")
                        conn.sendall(str.encode('{"packet":"disconnected"}'))
                        Connected = False

            if len(reply.encode('utf-8')) > 2048:
                print("packet to big")
            if reply == "":
                reply = "null"
            conn.sendall(str.encode(reply))
        except Exception:
            print(data)
            traceback.print_exc()
            print(f"{addr} lost conncection at {datetime.now().strftime('%I:%M:%S%p')}")
            break
    for server in servers:
        if server["server_info"]["Type"] != "PyChat":
            if client_ID in server["clients"]:
                if server["server_info"]["Type"] == "Snake":
                    leave_snake(client_ID, server["ID"])


    conn.close()

global servers
servers = []
global clients
clients = {}


while True:
    conn, addr = s.accept()
    print("Connected to :", addr, "at",datetime.now().strftime("%I:%M:%S%p"))

    client_IDs = []
    for each in clients:
        client_IDs.append(clients[each])
    client_ID = 0
    while client_ID in client_IDs:
        client_ID += 1
    clients[addr] = client_ID
    start_new_thread(client, (conn,addr,client_ID))