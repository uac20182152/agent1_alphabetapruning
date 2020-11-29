#!/usr/bin/env python3
import math
import time

import client as ct
import ast
import matplotlib.pyplot as plt
import networkx as nx
from hierarchy_pos import hierarchy_pos


action_dict = {
    "stay": (0, 0),
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0)
}

instances = 1


def result(state, action, graph):
    """Defines the state that results from doing a certain action in a certain state.
    In other words, it is the transition model.

    Parameters:
        state (dict): state description dictionary
        action (string): action description string
        graph (networkx.Graph): graph, used for visualization, may be None.

    Returns:
        state(dict): state description dictionary of the resulting state
    """
    new_state = state.copy()
    new_state["agent_id"] = (state["agent_id"] + 1) % 2
    new_state["agents"] = state["agents"].copy()
    new_state["agents"][new_state["agent_id"]] = tuple([new_state["agents"][new_state["agent_id"]][i] + action_dict[action][i] for i in range(2)])
    if state["agent_id"] == 1:
        new_state["round"] += 1

    if graph is not None:
        new_state["node_name"] = state["node_name"]+str(new_state["agent_id"])+action  # NetworkX
        # print(new_state["node_name"])  # NetworkX
        graph.add_node(new_state["node_name"], **new_state)  # NetworkX
        graph.add_edge(new_state["node_name"], state["node_name"], action=action)  # NetworkX

    global instances
    instances += 1
    return new_state


def utility(state, max_rounds):
    """Utility function (or payoff function). Defines the final numeric value for the game that ends in the given state.
    Since the given state description dictionary identifies the previous player and the game is a two-player game, there
    is no need to pass the player as an argument.

    Parameters:
        state (dict): state description dictionary
        max_rounds (int): number of rounds the minimizing player has to reach the goal

    Returns:
        0 (int) if the minimizing player wins
        1 (int) if the maximizing player wins
    """
    if state["agents"][0] in state["goals"]:
        return 0
    elif state["round"] >= max_rounds:
        return 1


def terminal_test(state, max_rounds):
    """Checks whether or not the game is over. Returns True if so, False otherwise.
    In other words, checks if a given state is a terminal state.

    Parameters:
        state (dict): state description dictionary
        max_rounds (int): number of rounds the minimizing player has to reach the goal

    Returns:
        (bool): whether or not the game is over.
    """
    return state["agents"][0] in state["goals"] or state["round"] >= max_rounds


def can_move(state, action):
    """Checks whether or not the next player can move in a certain direction.

    Parameters:
        state (dict): the state description dictionary
        action (str): the action description string

    Returns:
        (bool): whether or not the next player can perform the given action
    """

    cols, rows = [len(lista) for lista in (state["obstacles"], state["obstacles"][0])]
    self_pos, other_pos = (state["agents"][(state["agent_id"] + i) % 2] for i in (1, 0))
    new_self_x = (self_pos[0] + action_dict[action][0]) % cols
    new_self_y = (self_pos[1] + action_dict[action][1]) % rows
    return all((
        state["obstacles"][new_self_x][new_self_y] == 0,
        (new_self_x, new_self_y) != other_pos,
        not (state["agent_id"] == 0 and (new_self_x, new_self_y) in state["goals"])
    ))


def manhattan_distance(pos1,pos2):
    """ The Manhattan distance between two positions

    Parameters:
        pos1 (tuple or list): a position
        pos2 (tuple or list): another position

    Returns:
        (int or float): the Manhattan distance between pos1 and pos2
    """
    return abs(pos2[0]-pos1[0]) + abs(pos2[1]-pos1[1])


def killer_moves(state, action):
    """Heuristic ordering function for the actions, based on the Manhattan distance to the goal or related tiles.

    Parameters:
        state (dict): the state description dictionary
        action (str): the action to rank

    Returns:
        (int): if it's the maximizing player's turn, returns the Manhattan distance from the position resulting from
        the action to the goal-adjacent tile that is closest to the minimizing player. If it's the minimizing player's
        turn, returns the Manhattan distance from position that results from the action to the goal.
    """
    min_pos = state["agents"][0]
    closest_goal = sorted(state["goals"], key=lambda x: manhattan_distance(x, min_pos))[0]
    if state["agent_id"] == 0:
        hypothetical_pos = (state["agents"][1][0] + action_dict[action][0],
                            state["agents"][1][1] + action_dict[action][1])
        goal_adjacent_pos = sorted([(closest_goal[0]+i, closest_goal[1]+j) for i, j in action_dict.values()],
                                   key=lambda x: manhattan_distance(x,min_pos))[0]
        return manhattan_distance(hypothetical_pos, goal_adjacent_pos)
    else:
        hypothetical_pos = (min_pos[0] + action_dict[action][0], min_pos[1] + action_dict[action][1])
        return manhattan_distance(hypothetical_pos, closest_goal)

def killer_moves2(state, action):
    """Heuristic ordering function for the actions, based on the Manhattan distance to the goal or related tiles.

        Parameters:
            state (dict): state description dictionary
            action (str): the action to rank

        Returns:
            (int): if it's the maximizing player's turn, returns the Manhattan distance from the position resulting
            from the action to the goal-adjacent tile that is closest to the minimizing player. If it's the
            minimizing player's turn, returns the Manhattan distance from position that results from the action to
            the goal.
        """
    min_pos = state["agents"][0]
    closest_goal = min(state["goals"], key=lambda x: manhattan_distance(x, min_pos))
    if state["agent_id"] == 0:
        hypothetical_pos = (state["agents"][1][0] + action_dict[action][0],
                            state["agents"][1][1] + action_dict[action][1])
        dx, dy = closest_goal[0]-min_pos[0], closest_goal[1]-min_pos[1]
        if dx >= 0 and dx >= abs(dy):
            return manhattan_distance(hypothetical_pos, (closest_goal[0] + 1, closest_goal[1]))
        if dx <= 0 and dx >= abs(dy):
            return manhattan_distance(hypothetical_pos, (closest_goal[0] - 1, closest_goal[1]))
        if dy >= 0 and dx < abs(dy):
            return manhattan_distance(hypothetical_pos, (closest_goal[0], closest_goal[1] + 1))
        if dy <= 0 and dx < abs(dy):
            return manhattan_distance(hypothetical_pos, (closest_goal[0], closest_goal[1] - 1))
    else:
        hypothetical_pos = (min_pos[0] + action_dict[action][0],
                            min_pos[1] + action_dict[action][1])
        return manhattan_distance(hypothetical_pos, closest_goal)

def actions(state):
    """Returns all actions that the next player is allowed to do in the next ply.

    Parameters:
        state (dict): state description dictionary

    Returns:
        list: list of strings representing actions ("north", "south", "east", "west", "stay")
    """
    actions = [direction for direction in action_dict if can_move(state, direction)]
    #return actions  # Uncomment for naive Alpha-beta pruning
    return sorted(actions, key=lambda x: killer_moves2(state, x))  # Comment out for naive Alpha-beta pruning


def max_value(state, alpha, beta, rounds, graph, action):
    """Explores, in a tree-like fashion, the outcomes of all possible actions in a state from the perspective of the
    minimizing player, without ever exploring the outcomes that could have no influence on the final decision.

    Parameters:
        state (dict): state description dictionary
        alpha (int): the value of the best choice found so far in the path for the maximizing player
        beta (int): the value of the best choice found so far in the path for the minimizing player
        graph (networkx.Graph): graph, used for visualization, may be None
        action (str): the action that resulted in the state that the function is given

    Returns:
        (str): the action that resulted in the value to assign to this state
        (int): the value to assign to this state, according to the minimax algorithm, from the perspective of the
        minimizing player.
    """
    action = action
    if terminal_test(state, rounds):
        if graph is not None:
            state["value"] = utility(state, rounds) # NetworkX
            graph.nodes[state["node_name"]]["value"] = utility(state, rounds)  # NetworkX
        return action, utility(state, rounds)
    value = -1000
    for a in actions(state):
        action, value = max((action, value),
                            (a, min_value(result(state, a, graph), alpha, beta, rounds, graph, a)[1]),
                            key=lambda x: x[1])
        if value >= beta:
            return action, value
        alpha = max(alpha, value)

    if graph is not None:
        state["value"] = value # NetworkX
        graph.nodes[state["node_name"]]["value"] = value  # NetworkX

    return action, value


def min_value(state, alpha, beta, rounds, graph, action):
    """Explores, in a tree-like fashion, the outcomes of all possible actions in a state from the perspective of the
    minimizing player, without ever exploring the outcomes that could have no influence on the final decision.

    Parameters:
        state (dict): state description dictionary
        alpha (int): the value of the best choice found so far in the path for the maximizing player
        beta (int): the value of the best choice found so far in the path for the minimizing player
        graph (networkx.Graph): graph, used for visualization, may be None
        action (str): the action that resulted in the state that the function is given

    Returns:
        (str): the action that resulted in the value to assing to this state
        (int): the value to assign to this state, according to the minimax algorithm, from the perspective of the
        minimizing player.
    """

    action = action
    if terminal_test(state, rounds):
        if graph is not None:
            state["value"] = utility(state, rounds)  # NetworkX
            graph.nodes[state["node_name"]]["value"] = utility(state, rounds)  # NetworkX
        return action, utility(state, rounds)
    value = 1000
    for a in actions(state):
        action, value = min((action, value),
                            (a, max_value(result(state, a, graph), alpha, beta, rounds, graph, a)[1]),
                            key=lambda x: x[1])
        if value <= alpha:
            return action, value
        beta = min(beta, value)

    if graph is not None:
        state["value"] = value  # NetworkX
        graph.nodes[state["node_name"]]["value"] = value  # NetworkX
    return action, value


def alpha_beta_search(state, rounds, graph=None):
    """Returns the action description string that corresponds to the best action the agent can execute, that is, to the
    action that leads to the outcome with the best utility for the agent, assuming the adversary wants to minimize it.
    This search is optimized using a technique called alpha-beta pruning, a technique that prevents the minimax
    algorithm from exploring outcomes that have no possible influence on the final decision

    Parameters:
        state (dict): state description dictionary. The state of the environment before the agent moves.
        graph (Graph or None): graph for visualization

    Returns:
        (str): the action description string.
    """


    if graph is not None:
        graph.add_node("root", **state)
    a, v = max_value(state, -1000, 1000, rounds, graph, "stay")

    if graph is not None:
        labels = nx.get_node_attributes(graph, "value")
        edge_labels = nx.get_edge_attributes(graph, "action")
        # print(edge_labels)
        plt.figure(figsize=(20, 20))

        pos = hierarchy_pos(graph, "root", width=2 * math.pi, xcenter=0)
        new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}

        nx.draw(graph, new_pos, node_size=20, alpha=0.5, node_color="blue", labels=labels)
        nx.draw_networkx_edge_labels(graph, new_pos, edge_labels=edge_labels)
        plt.axis("equal")
        plt.show()

    return a


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


def main(rounds=5, visualization=False):
    """Game loop. Creates two clients and cycles between them.
    The first client is the minimizing player, or the human,
    and so the program waits for user input and sends the corresponding action value pair to the server.
    The second client is the maximizing player, and so the program calculates the best possible decision based on the
    minimax algorithm with alpha-beta pruning and sends the corresponding action value pair to the server.

    Parameters:
        None

    Returns:
        None
    """
    client_min = ct.Client('127.0.0.1', 50000)
    client_max = ct.Client('127.0.0.1', 50000)
    res_min = client_min.connect()
    res_max = client_max.connect()
    if all(res != -1 for res in (res_min, res_max)):
        print("Round: 1")
        while True:
            action, value = input("Min > ").split(" ")
            client_min.execute(action, value)

            state = ast.literal_eval(parse_last_dict(client_max.receiveData()))
            state["node_name"] = "root"

            start = time.perf_counter()
            g = nx.Graph() if visualization else None
            value = alpha_beta_search(state, rounds, g)
            stop = time.perf_counter()

            print("Max >", action, value)
            global instances
            print("Elapsed time:", stop - start, "Generated nodes:", instances)
            if visualization:
                print("Graph nodes: ",g.number_of_nodes())
            client_max.execute("command", value)

            if terminal_test(result(state, value, None), rounds):
                input("O jogo terminou.")
                break
            instances = 1
            print("Round: ",state["round"]+1)

if __name__=="__main__":
    main(rounds=5, visualization=True)
