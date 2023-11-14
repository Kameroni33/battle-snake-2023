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
LOOK_AHEAD_FACTOR = 1
DEPTH_LIMIT = 6

COLLISION_VALUE = 0.0
NORMAL_VALUE = 0.1
FOOD_VALUE = 1.0


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Kam & Zach",
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
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
    head = body[0]   # Coordinates of "head"
    neck = body[1]   # Coordinates of "neck"
    tail = body[-1]  # Coordinated of "tail"

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
    best_moves = []
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
            starting_position = {}

            if direction == "up":
                starting_position = {"x": head["x"], "y": head["y"] + 1}
            elif direction == "down":
                starting_position = {"x": head["x"], "y": head["y"] - 1}
            elif direction == "right":
                starting_position = {"x": head["x"] + 1, "y": head["y"]}
            elif direction == "left":
                starting_position = {"x": head["x"] - 1, "y": head["y"]}

            new_board = copy.deepcopy(board)
            new_board[head["x"]][head["y"]] = -1

            new_thread = Thread(target=next_move, args=(new_board, starting_position, 1, length if length < DEPTH_LIMIT else DEPTH_LIMIT, safe_moves[1], index))
            threads.append(new_thread)
            new_thread.start()

        for t in range(len(threads)):
            threads[t].join()

        for j in range(len(safe_moves[0])):
            if safe_moves[1][j] > best_score:
                best_moves = [safe_moves[0][j]]
                best_score = safe_moves[1][j]
            elif safe_moves[1][j] == best_score:
                best_moves.append(safe_moves[0][j])

        best_move = random.choice(best_moves)

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


def next_move(board, position, count, depth, result, result_index) -> float:
    weight = 1 / count * LOOK_AHEAD_FACTOR
    threads = []
    thread_scores = [0 for _ in range(4)]
    score = 0

    # BASE CASE:

    if count == depth:
        return score

    # RECURSIVE CASES:

    # direction: UP
    if position["y"] + 1 >= len(board[0]) or board[position["x"]][position["y"] + 1] < 0:
        up_score = 0
    else:
        if board[position["x"]][position["y"] + 1] > 0:
            up_score = FOOD_VALUE * weight
        else:
            up_score = NORMAL_VALUE * weight
        # update board and current position
        new_board = copy.deepcopy(board)
        new_board[position["x"]][position["y"] + 1] = -1
        new_position = {"x": position["x"], "y": position["y"] + 1}
        # recursively find next score
        up_thread = Thread(target=next_move, args=(new_board, new_position, count + 1, depth, thread_scores, 0))
        threads.append(up_thread)
        up_thread.start()

    # direction: DOWN
    if position["y"] <= 0 or board[position["x"]][position["y"] - 1] < 0:
        down_score = 0
    else:
        if board[position["x"]][position["y"] - 1] > 0:
            down_score = FOOD_VALUE * weight
        else:
            down_score = NORMAL_VALUE * weight
        # update board and current position
        new_board = copy.deepcopy(board)
        new_board[position["x"]][position["y"] - 1] = -1
        new_position = {"x": position["x"], "y": position["y"] - 1}
        # recursively find next score
        down_thread = Thread(target=next_move, args=(new_board, new_position, count + 1, depth, thread_scores, 1))
        threads.append(down_thread)
        down_thread.start()

    # direction: RIGHT
    if position["x"] + 1 >= len(board) or board[position["x"] + 1][position["y"]] < 0:
        right_score = 0
    else:
        if board[position["x"] + 1][position["y"]] > 0:
            right_score = FOOD_VALUE * weight
        else:
            right_score = NORMAL_VALUE * weight
        # update board and current position
        new_board = copy.deepcopy(board)
        new_board[position["x"] + 1][position["y"]] = -1
        new_position = {"x": position["x"] + 1, "y": position["y"]}
        # recursively find next score
        right_thread = Thread(target=next_move, args=(new_board, new_position, count + 1, depth, thread_scores, 2))
        threads.append(right_thread)
        right_thread.start()

    # direction: LEFT
    if position["x"] <= 0 or board[position["x"] - 1][position["y"]] < 0:
        left_score = 0
    else:
        if board[position["x"] - 1][position["y"]] > 0:
            left_score = FOOD_VALUE * weight
        else:
            left_score = NORMAL_VALUE * weight
        # update board and current position
        new_board = copy.deepcopy(board)
        new_board[position["x"] - 1][position["y"]] = -1
        new_position = {"x": position["x"] - 1, "y": position["y"]}
        # recursively find next score
        left_thread = Thread(target=next_move, args=(new_board, new_position, count + 1, depth, thread_scores, 3))
        threads.append(left_thread)
        left_thread.start()

    for i in range(len(threads)):
        threads[i].join()

    up_score += thread_scores[0]
    down_score += thread_scores[1]
    right_score += thread_scores[2]
    left_score += thread_scores[3]

    result[result_index] = (up_score + down_score + right_score + left_score) / 3


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
