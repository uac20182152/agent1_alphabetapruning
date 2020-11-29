#Sequential_MAIN

# 2- Sequential_ A pre-fixed number of clients (usually 2) is defined and they interact with the environment only once
# each time in a round-robin style.
# Clients send a message to server to connect. Each time, server returns a message to client #1 with the actual state of
#the world. The client answers with an action. Meanwile server returns a message to client #2 with the modified state of
# the world (with the modifications resulted from client #1 action). Client #2 returns an action. Server returns a
# message to client #1 with the new world state modified by client #2, etc.
# Each new client receive a name.

# Communication between agents:
# After each movement, all agents receives information about the world.

#import socket_server as s
import game_board as gb
import socket
import sys
import random
import tkinter as tk
import time
import traceback

class GameManager:
    def __init__(self, root:object, board:object,images_directory:str):
        self.root = root
        self.board = board
        self.images_directory = images_directory
        self.nr_conn = 0
        self.round = 0

    # Note: player[2] is the color of the player.
    def initialize_player(self, dirImage, player, nr):
        '''Not only add a player to the board but also return a pointer to this player'''
#imageDir,name,image_name,x,y,dir,view_type,width=0,heigh=0,color="white"
        ag = gb.Player(dirImage,'player'+str(nr+1), 'agent'+str(nr+1),player[0], player[1], 'south', 'front',True, player[2])
        ag.set_home((player[0],player[1]))
        ag.close_eyes()
        # Add player ...
        self.board.add(ag, player[0], player[1])
        return ag

    def initialize_obstacles(self,dirImage,list_obstacles):
        i = 1
        for obst in list_obstacles:
           ob = gb.Obstacle(dirImage,'ob'+str(i), obst[0], obst[1], 'obstacle'+str(i), False)
           self.board.add(ob, obst[0],obst[1])
           i=i+1

    def initialize_goal(self,dirImage,list_goals):
        # goal = gb.Goal('goal1', 10, 12, 'goal', False)
        # self.board.add(goal, 10, 12)
        i=1
        for g in list_goals:
            goal = gb.Goal(dirImage,'goal'+str(i),g[0],g[1], 'goal'+str(i), False)
            self.board.add(goal,g[0],g[1])
            i = i + 1

    def initialize_bomb(self,dirImage,list_bombs,rows,columns):
        i = 1
        for b in list_bombs:
            bomb = gb.Bomb(dirImage,'bomb'+str(i),b[0],b[1])
            self.board.add(bomb,b[0],b[1])
            if b[0] >= rows - 1:
                new_b = 0
            else:
                new_b = b[0]+1
            bomb_s = gb.BombSound(dirImage,'bomb_sound_s'+str(i),new_b,b[1])
            self.board.add(bomb_s,new_b,b[1])
            if b[1] >= columns - 1:
                new_b = 0
            else:
                new_b = b[1]+1
            bomb_s = gb.BombSound(dirImage,'bomb_sound_e'+str(i),b[0],new_b)
            self.board.add(bomb_s,b[0],new_b)
            if b[0] <= 0:
                new_b = columns - 1
            else:
                new_b = b[0]-1
            bomb_s = gb.BombSound(dirImage,'bomb_sound_n'+str(i),new_b,b[1])
            self.board.add(bomb_s,new_b,b[1])
            if b[1] <= 0:
                new_b = rows - 1
            else:
                new_b = b[1]-1

            bomb_s = gb.BombSound(dirImage,'bomb_sound_w'+str(i),b[0],new_b)
            self.board.add(bomb_s, b[0],new_b)
            i = i + 1

    def initialize_weights(self,imageDir,rows:int,columns:int):
        print(columns)
        print(rows)
        patch = [[0 for x in range(rows)] for x in range(columns)]
        print(patch)
        weight = 1.0
        name=''
        for column in range(0, columns):
            for row in range(0, rows):
                print("column:", column)
                print("row:",row)
                res = random.uniform(0, 1.0)
                if res <= 0.3:
                    name = "patch_clear"
                    weight=1.0
                elif res <= 0.5:
                    weight = 1.1#2.0
                    name = "patch_lighter"
                elif res <= 0.7:
                    weight = 1.2 #4.0
                    name = "patch_middle"
                elif res <= 1.0:
                    weight = 1.3 #8.0
                    name = "patch_heavy"
                patch[column][row] = gb.Patch(imageDir,'patch' + str(column) + "-" + str(row), name, column, row, weight, False)
                #print(res)
                self.board.add(patch[column][row], column, row)


    def message_processing(self,i:int,nr_conn:int, agent:object,data:str,coloring = True):
        ''' This function will process all messages received and  keep the result in a data structure.
        nr_conn: number of connected agents
        i: agent id
        data: message to process
        '''
        print("BBBBBBBBB",data)
        type, value = data.split()
        res = ""
        # -----------------------
        # Jumping
        # -----------------------
        if type == 'moveto':
            agent[i].close_eyes()
            res = self.board.move_to(agent[i],eval(value))
            if not self.board.is_target_obstacle(res) and not self.board.is_inPlaceVisited(res):
                self.board.change_position(agent[i],res[0],res[1])
                # Keep info about all positions occupied by agents in board.
                self.board.set_placesVisited(res)
                if coloring:
                    self.board.print_position(agent[i], res[0], res[1])
        if type == 'command':

            # -----------------------
            # movements without considering the direction
            # of the face of the object but testing the objects
            # -----------------------
            #The world must know the initial position of the other agent[i]s!!!!!!
            if value == 'north':
                agent[i].close_eyes()
                res = self.board.move_north(agent[i], 'forward')
                if not self.board.is_target_obstacle(res):  # NO TERRITORY and not self.board.is_inPlaceVisited(res):
                    self.board.change_position(agent[i], res[0], res[1])
                    # Keep info about all positions occupied by agents in board.

                    # NO TERRITORY
                    # self.board.set_placesVisited(res)
                    # if coloring:
                    #    self.board.print_position(agent[i],res[0],res[1])

            elif value == 'south':
                agent[i].close_eyes()
                res = self.board.move_south(agent[i], 'forward')
                if not self.board.is_target_obstacle(res):  # NO TERRITORY and not self.board.is_inPlaceVisited(res):
                    self.board.change_position(agent[i], res[0], res[1])
                    # Keep info about all positions occupied by agents in board.

                    # NO TERRITORY
                    # self.board.set_placesVisited(res)
                    # if coloring:
                    #    self.board.print_position(agent[i],res[0],res[1])


            elif value == 'east':
                agent[i].close_eyes()
                res = self.board.move_east(agent[i], 'forward')
                if not self.board.is_target_obstacle(res):  # NO TERRITORY and not self.board.is_inPlaceVisited(res):
                    self.board.change_position(agent[i], res[0], res[1])
                    # Keep info about all positions occupied by agents in board.

                    # NO TERRITORY
                    # self.board.set_placesVisited(res)
                    # if coloring:
                    #    self.board.print_position(agent[i],res[0],res[1])

            elif value == 'west':
                agent[i].close_eyes()
                res = self.board.move_west(agent[i], 'forward')
                if not self.board.is_target_obstacle(res):  # NO TERRITORY and not self.board.is_inPlaceVisited(res):
                    self.board.change_position(agent[i], res[0], res[1])
                    # Keep info about all positions occupied by agents in board.

                    # NO TERRITORY
                    # self.board.set_placesVisited(res)
                    # if coloring:
                    #    self.board.print_position(agent[i],res[0],res[1])

            elif value == 'stay':
                pass

            elif value == "set_steps":
                res = self.board.set_stepsview(agent[i])
            elif value == "reset_steps":
                res = self.board.reset_stepsview(agent[i])

    #       elif value == "bye" or value == "exit":
    #            conn.close()
    #            exit(1)

            else:
                pass


        # Returned Values
        # Returned Values
        #The value returned is: [agendID,[pos_agent[0],pos_agent[1],...],obstacles,goals,positions_already_used]
        pos_agents = []
        for j in range(self.nr_conn):
             pos_agents.append(self.board.getagentposition(agent[j]))
        # test
        print("Position of all agents:", pos_agents)
        # Obstacles
        pos_obstacles = self.board.view_obstacles(agent[i])
        # test
        print('Obstacles:', pos_obstacles)
        pos_goals = self.board.getgoalsposition(agent[i])
        print("Goals:",pos_goals)
        positions_already_used = self.board.get_placesVisited()
        res = [i,pos_agents,pos_obstacles,pos_goals,positions_already_used]

        res = {"agent_id": i,
               "agents": pos_agents,
               "obstacles": pos_obstacles,
               "goals": pos_goals,
               "visited": positions_already_used,
               "round": self.round}

        return str(res)

    def world_state(self,id,nr_agents: int, agent):
        '''The world state returns the data concerning the present world. It builds a list with the following organization:
        [agendID,[pos_agent[0],pos_agent[1],...],obstacles,goals]
        where agentID is the actual agent and it corresponds to 0,1,2,3, etc.
        [pos_agent[0],...,pos_agent[n]] are the position of the first n+1 agents in the world.
        obstacles and goals are the position of obstacles and goals in the world.

        nr_agents: number of agents in the world
        agent: actual agent (to whom is sent the world state)
        id: actual agent id
        '''
        pos_agents = []
        for j in range(nr_agents):
            pos_agents.append(self.board.getagentposition(agent[j]))
        # Test
        print("Position of all agents:", pos_agents)
        pos_obstacles = self.board.view_obstacles(agent[id])
        print('Obstacles:', pos_obstacles)
        pos_goals = self.board.getgoalsposition(agent[id])
        print("Goals:", pos_goals)
        ws= [id, pos_agents, pos_obstacles, pos_goals]
        return ws

    def loop(self,host,port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            self.connections = dict()
            print("Listening...")
            #Get position of the agents ...
            # Initialize player (file has the agents' initial position)
            players_file = 'input_files/players_file.txt'
            f = open(players_file)
            players = []
            agents =[]  # Agents are the entities that will be used to address each agent
            #while nr_conn < max_nr_conn:
            l = f.readline()

            while l != '':
                s.listen()
                conn, addr = s.accept()
                #test
                print("Connection is:",conn)
                print("Adress is:",addr)
                self.connections[self.nr_conn]=(conn, addr)
                # test
                print("Nr. of connections:", self.nr_conn + 1, ".Connected by", addr)
                print(self.connections[self.nr_conn][1])
                l = l.split(",")
                player = (int(l[0]), int(l[1]),str(l[2]).rstrip())
                players.append(player)
                agent = self.initialize_player(self.images_directory, player, self.nr_conn)
                agents.append(agent)
                # Return the agent id as a tuple (id, <number>)
                ag_nr = str.encode(str('(id,' + str(self.nr_conn) + ')'))
                conn.sendto(ag_nr,addr)
                self.nr_conn += 1
                l = f.readline()
                self.root.update()
            f.close()
            #test
            print("Round-robin data receiving from clients.")
            print("Number of connections is: ", self.nr_conn)
            while True:
                    self.round += 1
                    for i in range(self.nr_conn):
                        print('Connected by', self.connections[i][1])
                        conn = self.connections[i][0]
                        # Send the state of the world first
                        #conn.sendall(ag_nr)
                        data = conn.recvfrom(1024)
                        #test
                        print("Server: Data received:", data[0].decode())
                        return_data = self.message_processing(i,self.nr_conn,agents,data[0].decode())
                        #The data returned is always the state of the world:
                        #-- map of the obstacles
                        #-- the position of other agents
                        #-- map of goals (points)
                        #-- bombs are invisible and are not yet considered.
                        encode_data = str.encode(return_data)
                        self.root.update()
                        # Send to all agents the new information
                        for j in range(self.nr_conn):
                          self.connections[j][0].sendto(encode_data,self.connections[j][1])
                        #conn.sendall(encode_data)
                        print("Data was sent to all clients!!!!!")
                        print("waiting 1 seconds...")
                        time.sleep(1)


def main():
    #Host and Port
    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    else:
        host = '127.0.0.1'
        port = 50000
    # Size of the world ...
    print("Starting the Game Board")
    gameboard_file = 'input_files/gameboard_file.txt'
    f = open(gameboard_file)
    l = f.readline().split(",")
    columns = int(l[0])
    rows = int(l[1])
    f.close()
    root = tk.Tk()
    images_directory = 'images/'
    board = gb.GameBoard(root,columns,rows)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    #BOARD MAANAGER
    gm = GameManager(root, board,images_directory)
    # BOARD BOARD:
    #Read from files: initial agents position

    # Read from files: obstacles ...
    obstacles_file = 'input_files/obstacles_file.txt'
    f = open(obstacles_file)
    obst_list = []
    for l in f.readlines():
        l = l.split(",")
        if len(l) > 1:
          obst_list.append( (int(l[0]),int(l[1])) )

    gm.initialize_obstacles(images_directory,obst_list)
    #initialize_obstacles(images_directory,[(0,1),(4,6),(7,6),(6,7),(8,8)])
    f.close()
    # Defining the position of 'goals' ...
    goal_file = 'input_files/goal_file.txt'
    f = open(goal_file)
    goal_list = []
    for l in f.readlines():
        if len(l) > 1:
          l = l.split(",")
          goal_list.append( (int(l[0]),int(l[1])) )
        #print(goal_list)https://aihub.org/
    gm.initialize_goal(images_directory,goal_list)
    f.close()
    # Defining the bombs position:
    bomb_file = 'input_files/bomb_file.txt'
    f = open(bomb_file)
    bomb_list = []
    for l in f.readlines():
        if len(l) > 1:
          l = l.split(",")
          bomb_list.append( (int(l[0]),int(l[1])) )
        #print(bomb_list)
    gm.initialize_bomb(images_directory,bomb_list,rows,columns)
    f.close()
    # Initialize weights ...
    gm.initialize_weights(images_directory,rows, columns)
    root.update()
    # SERVER SERVER:
    # Starting server ...
    print("Starting the server!"),
    #server = s.Server()
    # Loop ...
    gm.loop(host,port)

main()
