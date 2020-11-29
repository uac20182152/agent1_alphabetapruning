#!/usr/bin/env python3
import socket
from queue  import Queue
#TEST
# This server accepts more than one client. But it has different ways of working with all the clients.
# 1- Synchronous_ A pre-fixed number of clients (e.g. 2) will interact with the server. Server will get info from these
# clients and for each turn it will receive their actions and randomly execute them in sequence. After their execution
# it returns the results for each one of the clients.
# A Queue is used to keep the results obtained by each thread.
# 2- Sequential_ A pre-fixed number of clients (usually 2) is defined and they interact with the environment only once
# each time in a round-robin style.
# Clients send a message to server to connect. Each time, server returns a message to client #1 with the actual state of
#the world. The client answers with an action. Meanwile server returns a message to client #2 with the modified state of
# the world (with the modifications resulted from client #1 action). Client #2 returns an action. Server returns a
# message to client #1 with the new world state modified by client #2, etc.
# 3- Asynchronous_ Clients send messages to server that treats them asynchronously by ascribing a thread fir each client.
#

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 50000       # Port to listen on (non-privileged ports are > 1023)
#EXAMPLE: Sequential (with a max_nr_conn = 2 by default)
class Server:
    def __init__(self):
        pass
    def run(self, max_nr_conn:int=2):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            nr_conn = 0
            connections = dict()
            print("Listening...")
            max_nr_conn = 2
            while nr_conn < max_nr_conn:
                s.listen()
                conn, addr = s.accept()
                connections[nr_conn] = (conn, addr)
                nr_conn += 1
                print("Nr. of connections:", nr_conn,".Connected by", addr)
            print("Round-robin data receiving from clients.")
            while True:
                for i in range(max_nr_conn):
                    print('Connected by', connections[i][1])
                    conn = connections[i][0]
                    data = conn.recv(1024)
#                    if not data:
#                        break
                    print(data.decode())
                    conn.sendall(data)


if __name__=="__main__":
    type = "Seq" #Other types: "Sync" and "unSync"
    server = Server()
    server.run(type)