#!/usr/bin/env python3
import socket
import time
import ast

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50000      # The port used by the server
class Client:
    def __init__(self,HOST='127.0.0.1',PORT=50000):
        self.host = HOST
        self.port = PORT
    def print_message(self,data):
        print("Data Received:",data)
    def connect(self):
#        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.port))
#            return(0)
#        except:
#            print('A connection error occurred!')
#            return(-1)
    def receiveData(self,sleep_t = 0.5):
        data = self.s.recv(20248)
        #print('Received',repr(data))
        msg = data.decode()
        #message(ast.literal_eval(data.decode()))
        time.sleep(sleep_t)
        return msg
    def execute(self,action,value,sleep_t = 0.5):
        #data = self.s.recv(20248)
        self.s.sendall(str.encode(action+" "+value))
        time.sleep(sleep_t)
        return 1
        #data = self.s.recv(2048)
        #print('Received', repr(data))
if __name__=="__main__":
    client = Client('127.0.0.1',50000)
    res = client.connect()
    if res !=-1:
        while True:
            action =""
            value =""
            msg = client.receiveData()
            # test
            client.print_message(msg)
            action, value = input("Insert action value pairs:").split()
            print("Action Value pair:", action, " ", value)
            client.execute(action,value)

