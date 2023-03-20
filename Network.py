import socket
from _thread import *
import time
import json
import os
import math
from datetime import datetime

#50.71.208.175
class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
        self.server = "142.161.10.140"
        self.port = 25562
        self.addr = (self.server,self.port)
        self.data = []
        global send
        global receive
        send = []
        receive = []
        self.start = 0

    def connect(self):
        try:
            self.client.settimeout(1)
            self.client.connect(self.addr)
            start_new_thread(client, (self.client, self.addr))
            self.connected = True
        except socket.error as e:
            print(e)
            print("server is not running or could not be found")
            self.connected = False
            return self.connected

        return self.connected


    def send(self,data):
        global send
        send.append(json.dumps(data))

    def receive(self,packet):
        global receive
        for data in receive:
            if packet == data["packet"]:
                receive.remove(data)
                return data
        return None


    def is_connect(self):
        return self.connected

def client(conn,addr):
    global send
    global receive
    while True:
        try:
            for data in  send:
                conn.send(str.encode(str(data)))
                send.remove(data)
                packet = json.loads(conn.recv(2048).decode("utf-8"))
                if packet != None:
                    receive.append(packet)
        except Exception as e:
            print(f"{addr} lost conncection at {datetime.now().strftime('%I:%M:%S%p')}")
            break
        time.sleep(0.01)
    conn.close()