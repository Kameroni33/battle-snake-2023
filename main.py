# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.

import random
import time
import typing
import copy
from threading import Thread

# Constants
LOOK_AHEAD_FACTOR = 15
DEPTH_LIMIT = 7

COLLISION_VALUE = 0.0
NORMAL_VALUE = 0.1
FOOD_VALUE = 50.0


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Kam & Zach",
        "color": "#FDD835",
        "head": "top-hat",
        "tail": "rose",
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    start_time = time.perf_counter()

    is_move_safe = {
        "up": True,
        "down": True,
        "left": True,
        "right": True
    }

    id = game_state["you"]["id"]
    body = game_state["you"]["body"]
    length = game_state["you"]["length"]
    head = body[0]  # Coordinates of "head"
    neck = body[1]  # Coordinates of "neck"
    tail = body[-1]  # Coordinates of "tail"
    my_snake = Snake()
    my_snake.append(tail['x'], tail['y'])
    my_snake.append(neck['x'], neck['y'])
    my_snake.append(head['x'], head['y'])

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    # =========================================================================
    # STEP 0: Construct state of the board
    # =========================================================================
    board = [[0 for column in range(board_width)] for row in range(board_height)]

    # place all snakes as [-1]
    for snake in game_state["board"]["snakes"]:
        if snake["id"] != id:
            if snake["body"][0]["x"] + 1 < board_width:
                board[snake["body"][0]["x"] + 1][snake["body"][0]["y"]] = -1
            if snake["body"][0]["x"] - 1 >= 0:
                board[snake["body"][0]["x"] - 1][snake["body"][0]["y"]] = -1
            if snake["body"][0]["y"] + 1 < board_height:
                board[snake["body"][0]["x"]][snake["body"][0]["y"] + 1] = -1
            if snake["body"][0]["y"] - 1 >= 0:
                board[snake["body"][0]["x"]][snake["body"][0]["y"] - 1] = -1
        for segment in range(snake["length"] - 1):
            board[snake["body"][segment]["x"]][snake["body"][segment]["y"]] = -1

    # place all food as [1]
    for food in game_state["board"]["food"]:
        board[food["x"]][food["y"]] = 1

    # print_board(board)

    # =========================================================================
    # STEP 1: Avoid colliding with ourselves or the border
    # =========================================================================

    if neck["x"] < head["x"] or head["x"] <= 0:
        is_move_safe["left"] = False

    if neck["x"] > head["x"] or head["x"] >= board_width - 1:
        is_move_safe["right"] = False

    if neck["y"] < head["y"] or head["y"] <= 0:
        is_move_safe["down"] = False

    if neck["y"] > head["y"] or head["y"] >= board_height - 1:
        is_move_safe["up"] = False

    for i in range(2, (length - 1)):
        if head["x"] + 1 == body[i]["x"] and head["y"] == body[i]["y"]:
            is_move_safe["right"] = False
        elif head["x"] - 1 == body[i]["x"] and head["y"] == body[i]["y"]:
            is_move_safe["left"] = False
        elif head["y"] + 1 == body[i]["y"] and head["x"] == body[i]["x"]:
            is_move_safe["up"] = False
        elif head["y"] - 1 == body[i]["y"] and head["x"] == body[i]["x"]:
            is_move_safe["down"] = False

    # =========================================================================
    # STEP 2: Determine next best move
    # =========================================================================

    safe_moves = [[], []]
    best_move = "down"
    best_score = 0

    for direction, is_safe in is_move_safe.items():
        if is_safe:
            safe_moves[0].append(direction)
            safe_moves[1].append(0)

    if len(safe_moves) == 0:
        print(f"*** No safe moves detected! ***")
        best_move = "down"  # picked arbitrary
    else:
        threads = []
        for index in range(len(safe_moves[0])):
            direction = safe_moves[0][index]

            if direction == "up":
                my_snake.append(my_snake.head.getx(), my_snake.head.gety() + 1)
            elif direction == "down":
                my_snake.append(my_snake.head.getx(), my_snake.head.gety() - 1)
            elif direction == "right":
                my_snake.append(my_snake.head.getx() + 1, my_snake.head.gety())
            elif direction == "left":
                my_snake.append(my_snake.head.getx() - 1, my_snake.head.gety())

            # new_board = copy.deepcopy(board)
            # new_board[head["x"]][head["y"]] = -1

            new_score = next_move(board, my_snake, 1)
            safe_moves[1][index] = new_score

            if new_score > best_score:
                best_move = direction
                best_score = new_score

    print(f"SAFE MOVES: {[safe_move for safe_move in safe_moves]}")
    print(f"SCORES: {safe_moves}")
    print(f"BEST MOVE: {best_move}")

    end_time = time.perf_counter()
    print(f"TIME: {round((end_time - start_time) * 1000)}ms")

    # return next move
    print(f"MOVE {game_state['turn']}: {best_move}")
    return {"move": best_move}


def print_board(board: [[int]]) -> None:
    print_string = ("=" * (len(board[0]) * 2 + 3)) + "\n"
    for row in range(len(board)):
        print_string += "= "
        for column in range(len(board[0])):
            value = board[column][-(row + 1)]
            if value < 0:
                print_string += "x "
            elif value > 0:
                print_string += "o "
            else:
                print_string += "  "
        print_string += "=" + "\n"
    print_string += ("=" * (len(board[0]) * 2 + 3))

    print(print_string)


def next_move(board, snake, count) -> float:
    weight = 1 / (count * LOOK_AHEAD_FACTOR)
    ate = False

    # Evaluate position
    if board[snake.head.getx()][snake.head.gety()] > 0:
        print("IRAN")
        score = FOOD_VALUE * weight
        ate = True
    else:
        score = NORMAL_VALUE * weight
        board[snake.tail.getx()][snake.tail.gety()] = 0
        snake.tail = snake.tail.next

    # BASE CASE:

    if count == DEPTH_LIMIT:
        return score

    # RECURSIVE CASES:

    # direction: UP
    if snake.head.gety() + 1 < len(board[0]) and board[snake.head.getx()][snake.head.gety() + 1] >= 0:
        # update board and current position
        # new_board = copy.deepcopy(board)
        board[snake.head.getx()][snake.head.gety() + 1] = -1
        snake.append(snake.head.getx(), snake.head.gety() + 1)
        # recursively find next score
        score += next_move(board, snake, count + 1)

    # direction: DOWN
    if snake.head.gety() > 0 and board[snake.head.getx()][snake.head.gety() - 1] >= 0:
        # update board and current position
        #new_board = copy.deepcopy(board)
        board[snake.head.getx()][snake.head.gety() - 1] = -1
        snake.append(snake.head.getx(), snake.head.gety() - 1)
        # recursively find next score
        score += next_move(board, snake, count + 1)

    # direction: RIGHT
    if snake.head.getx() + 1 < len(board) and board[snake.head.getx() + 1][snake.head.gety()] >= 0:
        # update board and current position
        #new_board = copy.deepcopy(board)
        board[snake.head.getx() + 1][snake.head.gety()] = -1
        snake.append(snake.head.getx() + 1, snake.head.gety())
        # recursively find next score
        score += next_move(board, snake, count + 1)

    # direction: LEFT
    if snake.head.getx() > 0 and board[snake.head.getx() - 1][snake.head.gety()] >= 0:
        # update board and current position
        #new_board = copy.deepcopy(board)
        board[snake.head.getx() - 1][snake.head.gety()] = -1
        snake.append(snake.head.getx() - 1, snake.head.gety())
        # recursively find next score
        score += next_move(board, snake, count + 1)

    if ate:
        board[snake.head.getx()][snake.head.gety()] = 1
    else:
        snake.tail = snake.tail.prev
        board[snake.tail.getx()][snake.tail.gety()] = -1
        board[snake.head.getx()][snake.head.gety()] = 0
    snake.head = snake.head.prev

    return score


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.next = None
        self.prev = None

    def gety(self):
        return self.y

    def getx(self):
        return self.x


class Snake:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, x, y):
        new_node = Node(x, y)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.head.next = new_node
            new_node.prev = self.head
            self.head = new_node


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
