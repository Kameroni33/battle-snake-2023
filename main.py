# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com
import math
import random
import typing


# CONSTANTS



# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Kam + Zach",  # TODO: Your Battlesnake Username
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

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    heuristic = 1

    FOOD_WEIGHT = 1
    ENEMY_WEIGHT = 0


    next_move()
    next_move()
    next_move()

    body = game_state["you"]["body"]  # 2D array of {x: int, y: int}
    head = body[0]  # Coordinates of "head"
    neck = body[1]  # Coordinates of "neck"

    if neck["x"] < head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif neck["x"] > head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif neck["y"] < head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif neck["y"] > head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if head["x"] == 0:  # Head is on left wall, don't move left
        is_move_safe["left"] = False

    if head["x"] + 1 == board_width:  # Head is on right wall, don't move right
        is_move_safe["right"] = False

    if head["y"] == 0:  # Head is on bottom wall, don't move down
        is_move_safe["down"] = False

    if head["y"] + 1 == board_height:  # Head is on top wall, don't move up
        is_move_safe["up"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_length = game_state["you"]["length"]

    for i in range(2, (my_length - 1)):
        if head["x"] + 1 == body[i]["x"] and head["y"] == body[i]["y"]:
            is_move_safe["right"] = False
        elif head["x"] - 1 == body[i]["x"] and head["y"] == body[i]["y"]:
            is_move_safe["left"] = False
        if head["y"] + 1 == body[i]["y"] and head["x"] == body[i]["x"]:
            is_move_safe["up"] = False
        elif head["y"] - 1 == body[i]["y"] and head["x"] == body[i]["x"]:
            is_move_safe["down"] = False

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    # opponents = game_state['board']['snakes']

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)
    #for i in safe_moves:
     #   print(safe_moves)
      #  next_move = safe_moves.pop()
       # break

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    for direction in safe_moves:



    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


def collision(points: list[dict[int]], location: dict[int]) -> bool:
    """
    Check if `location` collides with any of the given `points`.
    Returns `true` if collision, otherwise `false`.

    :param points: occupied points on map
    :param location: location to be validated
    :return: bool
    """
    for point in points:
        if location["x"] ==

def next_move(body, count, depth) -> float:
    score = 0
    weight = 1 / count

    # BASE CASE:

    if count == depth:
        return score

    # RECURSIVE CASES:

    if "NORTH" == "collision":
        north_score = 0
    else:
        if food:
            north_score = FOOD_VALUE * weight
        else:
            north_score = NORMAL_VALUE * weight

        body = body # shift it
        north_score += next_move(body, count+1, depth)

    if "EAST" == "collision":
        east_score = 0
    else:
        body = body # shift it
        east_score = next_move(body, count+1, depth)

    if "SOUTH" == "collision":
        south_score = 0
    else:
        body = body # shift it
        south_score = next_move(body, count+1, depth)

    if "WEST" == "collision":
        west_score = 0
    else:
        body = body # shift it
        west_score = next_move(body, count+1, depth)

    # return some combination of these values
    return (north_score + east_score + south_score + west_score) / 3



# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
