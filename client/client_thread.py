#!/usr/bin/env python3

# ver 3.0 Agent I
# This client thread will keep data read in a list shared by three threads.
# The list must be accesssed using the lock defined in the execute.
# Each thread has a method that executes in an infinite loop.

import socket
import time
import ast
import threading

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50000      # The port used by the server
class Client:
    def __init__(self,HOST='127.0.0.1',PORT=50000):
        self.host = HOST
        self.port = PORT
        self.data_list =[]
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
    #Thread test
    def test_data(self):
        while True:
            self.lock.acquire()
            for v in self.data_list:
                print(v)
            print("---------------")
            self.lock.release()
            time.sleep(5)
            # Alternative: if there is data on data_list, remove it and process it.
            # Note: changes in data_list must be protected with lock!
    # Threaded
    def receiveData(self,sleep_t = 0.5):
        while True:
          data = self.s.recv(20248)
          print('Received',repr(data))
          msg = data.decode()
          #message(ast.literal_eval(data.decode()))
          time.sleep(sleep_t)
          self.lock.acquire()
          print("Added information to list")
          self.data_list.append(msg)
          self.lock.release()
    # Threaded
    def executeData(self,sleep_t = 0.5):
        while True:
          #data = self.s.recv(20248)
          action, value = input("Insert action value pairs:").split()
          print("Action Value pair:", action, " ", value)
          self.s.sendall(str.encode(action+" "+value))
          time.sleep(sleep_t)


    # Execute three threads: one for receiving data, other for send data to server. The test is used to print data received.
    def execute(self):
        # Defining a Lock
        self.lock = threading.Lock()
        # Threading receiving data
        threading.Thread(target=self.receiveData).start()
        # Threading sending data
        threading.Thread(target=self.executeData).start()
        threading.Thread(target=self.test_data).start()



if __name__=="__main__":
    client = Client('127.0.0.1',50000)
    res = client.connect()
    if res !=-1:
        client.execute()


