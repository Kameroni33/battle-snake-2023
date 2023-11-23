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
# import copy
# from threading import Thread

# Constants
LOOK_AHEAD_FACTOR = 0.1
DEPTH_LIMIT = 10

COLLISION_VALUE = 0.0
NORMAL_VALUE = 0.5
FOOD_VALUE = 1.0


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

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    # =========================================================================
    # STEP 0: Construct state of the board
    # =========================================================================
    board = [[0 for column in range(board_width)] for row in range(board_height)]

    # place all food as [1] (must come before snake placement)
    for food in game_state["board"]["food"]:
        board[food["x"]][food["y"]] = 1

    # place all snakes as [-1]
    # print(game_state["board"]["snakes"])
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
        for segment in range(snake["length"]):
            if snake["id"] == id:
                my_snake.add_node(snake["body"][(snake["length"] - 1) - segment]["x"], snake["body"][(snake["length"] - 1) - segment]["y"])
            board[snake["body"][segment]["x"]][snake["body"][segment]["y"]] = -1

    # place initial head and tail
    # print(f'My Snake: head at ({my_snake.head.getx}, {my_snake.head.gety}), tail at ({my_snake.tail.getx}, {my_snake.tail.gety})')
    board[body[0]["x"]][body[0]["y"]] = -2
    board[body[-1]["x"]][body[-1]["y"]] = -3

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
    best_score = 0

    for direction, is_safe in is_move_safe.items():
        if is_safe:
            safe_moves[0].append(direction)
            safe_moves[1].append(0)

    if len(safe_moves) == 0:
        print(f"*** No safe moves detected! ***")
        best_move = "down"  # picked arbitrary
    else:
        best_move = safe_moves[0][0]

        # print("Original Board State")
        # print_board(board)
        board[my_snake.head.getx()][my_snake.head.gety()] = -1  # head now becomes "body"

        current_best_moves = []

        for index in range(len(safe_moves[0])):
            direction = safe_moves[0][index]
            if direction == "up":
                my_snake.add_node(my_snake.head.getx(), my_snake.head.gety() + 1)
            elif direction == "down":
                my_snake.add_node(my_snake.head.getx(), my_snake.head.gety() - 1)
            elif direction == "right":
                my_snake.add_node(my_snake.head.getx() + 1, my_snake.head.gety())
            elif direction == "left":
                my_snake.add_node(my_snake.head.getx() - 1, my_snake.head.gety())

            new_score = next_move(board, my_snake, 1)
            safe_moves[1][index] = new_score

            if new_score > best_score:
                current_best_moves = [direction]
                best_score = new_score
            elif new_score == best_score:
                current_best_moves.append(direction)

        choice = random.randint(0, len(current_best_moves)-1)
        best_move = current_best_moves[choice]

    print(f"SAFE MOVES: {[safe_move for safe_move in safe_moves[0]]}")
    print(f"SCORES: {[safe_move for safe_move in safe_moves[1]]}")
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
            if value == -1:
                print_string += "X "
            elif value == -2:
                print_string += "H "
            elif value == -3:
                print_string += "T "
            elif value > 0:
                print_string += "O "
            else:
                print_string += "  "
        print_string += "=" + "\n"
    print_string += ("=" * (len(board[0]) * 2 + 3))

    print(print_string)


def next_move(board, snake, count) -> float:
    weight = 1 / (count * LOOK_AHEAD_FACTOR)

    next_scores = 0
    num_next_scores = 0

    score = 0

    # BASE CASE:

    if count == DEPTH_LIMIT:
        snake.head = snake.head.prev
        return score

    # EVALUATE CURRENT POSITION:

    current_position = board[snake.head.getx()][snake.head.gety()]
    if current_position < 0:
        score = COLLISION_VALUE * weight
        snake.head = snake.head.prev
        return score
    elif current_position > 0:
        # move head forward
        board[snake.head.getx()][snake.head.gety()] = -2
        score = FOOD_VALUE * weight
        ate = True
    else:
        # move head forward
        board[snake.head.getx()][snake.head.gety()] = -2
        score = NORMAL_VALUE * weight
        ate = False

    # FOR DEBUGGING ===========================================================
    # print_board(board)
    board[snake.head.getx()][snake.head.gety()] = -1  # head now become "body"
    # =========================================================================

    # move tail forward
    board[snake.tail.getx()][snake.tail.gety()] = 0
    snake.tail = snake.tail.next
    board[snake.tail.getx()][snake.tail.gety()] = -3

    # RECURSIVE CASES:

    # direction: UP
    if snake.head.gety() + 1 < len(board[0]) and board[snake.head.getx()][snake.head.gety() + 1] >= 0:
        # print(f"Testing Up ({count})")
        num_next_scores += 1
        # move head forward
        snake.add_node(snake.head.getx(), snake.head.gety() + 1)
        # recursively find next score
        next_scores += next_move(board, snake, count + 1)

    # direction: DOWN
    if snake.head.gety() > 0 and board[snake.head.getx()][snake.head.gety() - 1] >= 0:
        # print(f"Testing Down ({count})")
        num_next_scores += 1
        # move head forward
        snake.add_node(snake.head.getx(), snake.head.gety() - 1)
        # recursively find next score
        next_scores += next_move(board, snake, count + 1)

    # direction: RIGHT
    if snake.head.getx() + 1 < len(board) and board[snake.head.getx() + 1][snake.head.gety()] >= 0:
        # print(f"Testing Right ({count})")
        num_next_scores += 1
        # move head forward
        snake.add_node(snake.head.getx() + 1, snake.head.gety())
        # recursively find next score
        next_scores += next_move(board, snake, count + 1)

    # direction: LEFT
    if snake.head.getx() > 0 and board[snake.head.getx() - 1][snake.head.gety()] >= 0:
        # print(f"Testing Left ({count})")
        num_next_scores += 1
        # move head forward
        snake.add_node(snake.head.getx() - 1, snake.head.gety())
        # recursively find next score
        next_scores += next_move(board, snake, count + 1)

    # return tail to original position
    snake.tail = snake.tail.prev
    board[snake.tail.getx()][snake.tail.gety()] = -3

    # return head to original position
    board[snake.head.getx()][snake.head.gety()] = 1 if ate else 0
    snake.head = snake.head.prev

    if num_next_scores > 0:
        # add average score of next moves
        score += (next_scores / num_next_scores)

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

    def get_next(self):
        return self.next

    def get_prev(self):
        return self.prev


class Snake:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_node(self, x, y):
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
