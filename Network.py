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
        self.server = "142.161.10.140"
        self.port = 25562
        self.addr = (self.server,self.port)
        self.data = []
        global send
        global receive
        global connected
        send = ""
        receive = []
        self.start = 0
        connected = False

    def connect(self):
        global connected
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.client.settimeout(1)
            self.client.connect(self.addr)
            start_new_thread(client, (self.client, self.addr))
            connected = True
        except socket.error as e:
            print(e)
            print("server is not running or could not be found")
            connected = False


    def send(self,data):
        global send
        send+=json.dumps(data)+"&"

    def receive(self,packet):
        global receive
        for data in receive:
            if packet == data["packet"]:
                receive.remove(data)
                return data
        return None

    def is_connected(self):
        global connected
        return connected

def client(conn,addr):
    global send
    global receive
    global connected
    while True:
        try:
            if send != "":
                if len(send.encode('utf-8')) > 2048:
                    print("packet to big")
                start = time.perf_counter()
                conn.send(str.encode(send))
                send = ""
                packets = conn.recv(2048).decode("utf-8")
                if packets != None:
                    packets = packets.split("&")
                    for packet in packets:
                        if packet != "" and packet != "null":
                            receive.append(json.loads(packet))
                print(f"packet took {time.perf_counter() - start} to send and receive" )
        except Exception as e:
            print(e)
            print(f"{addr} lost conncection at {datetime.now().strftime('%I:%M:%S%p')}")
            connected = False
            break
        time.sleep(0.01)
    conn.close()