#!/usr/bin/env python3
import math
import time

import client as ct
import ast
import matplotlib.pyplot as plt
import networkx as nx
from hierarchy_pos import hierarchy_pos

class State:

    instances = 0

    action_offset = {
        "stay": (0, 0),
        "north": (0, -1),
        "south": (0, 1),
        "east": (1, 0),
        "west": (-1, 0)
    }

    goal_positions = None
    max_rounds = None
    obstacle_matrix = None

    @classmethod
    def set_obstacle_matrix(cls, obstacle_matrix):
        """Defines the obstacle matrix, where at indexes [x][y] 1 means there is an obstacle at position at (x,y),
        0 otherwise. Also defines the dimensions of the board"""
        cls.obstacle_matrix = obstacle_matrix
        cls.columns = len(obstacle_matrix)
        cls.rows = len(obstacle_matrix[0])

    @classmethod
    def set_goal_positions(cls, goal_positions):
        """Defines the goal positions for the round that will be examined by the algorithm"""
        cls.goal_positions = goal_positions

    @classmethod
    def set_max_rounds(cls, max_rounds):
        """Defines the duration of the game, which is also the depth of the search tree"""
        cls.max_rounds = max_rounds

    def __init__(self, is_max_turn, min_pos, max_pos, previous_round, graph=None, previous_name=None, action=None):
        """Defines the state's attributes and, if visualization is enabled (work in progress), adds a corresponding node
        and edge to the tree graph."""
        self.is_max_turn = is_max_turn
        self.min_pos = min_pos
        self.max_pos = max_pos
        self.round = previous_round + (1 if is_max_turn else 0)
        self.graph = graph
        self.name = "root"
        self.action = action

        # TODO: fix graph issues
        if self.graph is not None and (previous_name != None):
            self.name = previous_name+str("Max" if self.is_max_turn else "Min")+str(self.max_pos if self.is_max_turn else self.min_pos)
            graph.add_node(self.name)  # NetworkX
            graph.add_edge(previous_name, self.name, action=action)  # NetworkX

        State.instances += 1

    def result(self, action):
        """Defines the state that results from doing a certain action in the state.
        In other words, this function is the transition model.

        Parameters:
            action (string): action description string

        Returns:
            (State): the resulting state
        """
        if self.is_max_turn:
            new_max_pos = (self.max_pos[0] + self.action_offset[action][0],
                           self.max_pos[1] + self.action_offset[action][1])
            new_min_pos = self.min_pos
        else:
            new_min_pos = (self.min_pos[0] + self.action_offset[action][0],
                           self.min_pos[1] + self.action_offset[action][1])
            new_max_pos = self.max_pos
        return State(not self.is_max_turn, new_min_pos, new_max_pos, self.round,
                     graph=self.graph, previous_name=self.name, action=action)

    def utility(self):
        """Utility function (or payoff function). Defines the final numeric value for the game that ends in the state.
        Since the state knows which player is next and the game is a two-player game, there is no need to pass the
        player as an argument.

        Returns:
            (int) 0 if the minimizing player wins, 1 if the maximizing player wins
        """
        u = 1 if self.max_pos in self.goal_positions else 0
        if self.graph is not None:
            self.graph.nodes[self.name]["value"] = u
        return u

    def is_terminal(self):
        """Checks whether or not the game is over. Returns True if so, False otherwise.
        In other words, checks this state is a terminal state.

        Returns:
            (bool): whether or the state is a terminal state.
        """
        return self.max_pos in State.goal_positions or self.round >= State.max_rounds

    def is_legal(self, action):
        """Checks whether or not the next player can perform a certain action.

        Parameters:
            action (str): the action description string

        Returns:
            (bool): whether or not the next player can perform the given action
        """
        player_pos = self.max_pos if self.is_max_turn else self.min_pos
        other_pos = self.min_pos if self.is_max_turn else self.max_pos
        offset = self.action_offset[action]
        new_x = (player_pos[0] + offset[0]) % self.columns
        new_y = (player_pos[1] + offset[1]) % self.rows
        return all((
            State.obstacle_matrix[new_x][new_y] == 0,
            (new_x, new_y) != other_pos,
            (self.is_max_turn or (not self.is_max_turn and (new_x, new_y) not in State.goal_positions))))


    def actions(self):
        """Returns all actions that the next player is allowed to perform in its turn, ordered by the killer-moves
        heuristic.

        Returns:
            (list) list of strings representing all legal actions ("north", "south", "east", "west" or "stay")
        """
        a = [action for action in State.action_offset if self.is_legal(action)]
        return a

    def max_value(self):
        """Explores, in a tree-like fashion, the outcomes of all possible actions in the state from the perspective of
        the maximizing player.

        Returns:
            (int): the value to assign to this state, according to the minimax algorithm, from the perspective of the
            maximizing player.
        """
        if self.is_terminal():
            return self.utility()

        value = -1000
        for action in self.actions():
            value = max(value, self.result(action).min_value())

        if self.graph is not None:
            self.graph.nodes[self.name]["value"] = value
        return value

    def min_value(self):
        """Explores, in a tree-like fashion, the outcomes of all possible actions in a state from the perspective of the
        minimizing player.

        Returns:
            (int): the value to assign to this state, according to the minimax algorithm, from the perspective of the
            minimizing player.
        """
        if self.is_terminal():
            return self.utility()

        value = 1000
        for action in self.actions():
            value = min(value, self.result(action).max_value())

        if self.graph is not None:
            self.graph.nodes[self.name]["value"] = value
        return value

class Agent:
    """Describes an adversarial agent"""

    def __init__(self):
        """Simply initializes the agent"""
        self.current_state = None

    def set_state(self, state_description):
        """Defines the current state of the game from a state description dictionary provided by the Agent1 server

        Parameters:
            state_description (dict): the state description dictionary

        """
        self.current_state = State(state_description["agent_id"] == 0,
                                   state_description["agents"][0],
                                   state_description["agents"][1],
                                   state_description["round"],
                                   None,  # nx.Graph(),
                                   None,
                                   "root")

    def minimax_decision(self):
        """Returns the action description string that corresponds to the best action the agent can execute, that is, to
        the action that leads to the outcome with the best utility for the agent, assuming the adversary wants to
        minimize it.

        Returns:
            (str): the action description string.
        """
        a = {action: self.current_state.result(action).min_value() for action in self.current_state.actions()}

        if self.current_state.graph is not None:
            # From Joel's answer at https://stackoverflow.com/a/29597209/2966723

            labels = nx.get_node_attributes(self.current_state.graph, "value")
            edge_labels = nx.get_edge_attributes(self.current_state.graph, "action")
            # print(edge_labels)
            plt.figure(figsize=(20, 20))

            pos = hierarchy_pos(self.current_state.graph, "root", width=2 * math.pi, xcenter=0)
            new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}

            nx.draw(self.current_state.graph, new_pos, node_size=20, alpha=0.5, node_color="blue", labels=labels)
            nx.draw_networkx_edge_labels(self.current_state.graph, new_pos, edge_labels=edge_labels)
            plt.axis("equal")
            plt.show()

        return max(a, key=a.get)

def parse_last_dict(bad_string):
    """Returns the string that corresponds to the last open and closed curly brackets.
    This is necessary due to the way the server/client interaction works, so as to identify the last server response.
    Ideally, this would be unnecessary, but this had to be implemented due to time restrictions that prevented the group
    from exploring the software.

    Parameters:
        bad_string (str): the string to parse

    Returns:
        (str): the resulting good string

    """
    return bad_string[bad_string.rindex("{"):]


def main(rounds):
    """Game loop. Creates two clients and cycles between them.
    The first client is the minimizing player, or the human,
    and so the program waits for user input and sends the corresponding action value pair to the server.
    The second
    client is the maximizing player, and so the program calculates the best possible decision based on the minimax algorithm and sends
    the corresponding action value pair to the server.
    """
    client_min = ct.Client('127.0.0.1', 50000)
    client_max = ct.Client('127.0.0.1', 50000)
    res_min = client_min.connect()
    res_max = client_max.connect()
    if all(res != -1 for res in (res_min, res_max)):

        agent = Agent()
        State.set_max_rounds(rounds)

        while True:
            command, action = input("Min > ").split(" ")
            client_min.execute(command, action)

            state = ast.literal_eval(parse_last_dict(client_max.receiveData()))
            State.set_goal_positions(state["goals"])
            State.set_obstacle_matrix(state["obstacles"])
            agent.set_state(state)

            start = time.perf_counter()
            action = agent.minimax_decision()
            stop = time.perf_counter()

            print("Max > command", action)
            print("Elapsed time:", stop - start, " # of Nodes:", State.instances)
            State.instances = 0

            client_max.execute("command", action)

            if agent.current_state.result(action).is_terminal():
                input("O jogo terminou.")
                break

if __name__=="__main__":
    main(rounds=7)