import socket
from _thread import *
import time
import json
import os
import math
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


def client(conn,addr):
    global servers
    global clients
    reply = "null"
    data = ""

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


    while True:
        try:
            data = conn.recv(2048).decode("utf-8")
            if data == "":
                print(addr, "disconnected", "at", datetime.now().strftime("%I:%M:%S%p"))
                clients.remove(addr)
                break
            else:
                data = json.loads(data)
# ping server
                print(data)
                if data["packet"] == "ping":
                    reply = '{"packet":"ping"}'
# server management

# join a game server
                elif data["packet"] == "join_server":
                    reply = json.dumps({"packet":"new_server","server":str(server)})

# Leave a game server
                elif data["packet"] == "leave_server":
                    reply = json.dumps({"packet":"new_server","server":str(server)})

# create new server
                elif data["packet"] == "new_server":
                    server_IDs = []
                    for server in servers:
                        server_IDs.append(server["server_ID"])

                    server_ID = 0
                    while server_ID in server_IDs:
                        server_ID += 1
                    server = {"ID":server_ID}
                    servers.append(server)
                    reply = json.dumps({"packet":"new_server","server":server})

# get server list
                elif data["packet"] == "get_servers":
                    reply = json.dumps({"packet": "servers", "servers": servers})

# server data
                elif data["packet"] == "add_data":
                    servers[data["server"]][data["key"]] = data["data"]
                elif data["packet"] == "add_data_to_dict":
                    servers[data["server"]][data["key"]][data["key2"]] = data["data"]
                    print(servers[data["server"]][data["key"]])
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
                    reply = json.dumps({"packet": "get_data", "data": servers[data["server"]][data["key"]]})


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
                    server["name"] = data["name"]
                    server["password"] = data["password"]
                    server["type"] =  "PyChat"
                    server["message_list"] = []
                    server["messages"] = {}
                    servers.append(server)
                    servers.sort(key=sort_servers_by_ID)

                    reply = json.dumps({"packet":"new_chat","server":server})

                elif data["packet"] == "get_PyChats":
                    PyChat_servers = []
                    for server in servers:
                        if server["type"] == "PyChat":
                            PyChat_servers.append(server["name"])
                    reply = json.dumps({"packet": "PyChat_servers", "servers": PyChat_servers})

                elif data["packet"] == "join_PyChat":
                    reply = json.dumps({"packet": "join_PyChat", "server": "bad password"})
                    for server in servers:
                        if server["name"] == data["name"] and server["password"] == data["password"]:
                            reply = json.dumps({"packet": "join_PyChat", "server": server})
                            break


                elif data["packet"] == "send_message":
                    reply = "null"
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
                    reply = json.dumps(message)

# Disconnect from server

                elif data["packet"] == "disconnect":
                    print("disconnecting")
                    conn.sendall(str.encode('{"packet":"disconnected"}'))
                    break

            conn.sendall(str.encode(reply))
        except Exception:
            print(data)
            traceback.print_exc()
            print(f"{addr} lost conncection at {datetime.now().strftime('%I:%M:%S%p')}")
            break
    conn.close()

global servers
servers = []
global clients
clients = []


while True:
    conn, addr = s.accept()
    print("Connected to :", addr, "at",datetime.now().strftime("%I:%M:%S%p"))
    clients.append(addr)
    start_new_thread(client, (conn,addr))



