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

import random
import typing
import numpy as np


    

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "dragonslayer",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "dragon",  # TODO: Choose head
        "tail": "bolt",  # TODO: Choose tail
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

    my_body = game_state["you"]["body"]
    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head["x"] == board_width-1:
        is_move_safe["right"] = False
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["y"] == board_height-1:
        is_move_safe["up"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself or opponents
    snakes = game_state['board']['snakes']
    for snake_n in snakes:
        snake_body = snake_n["body"]
        min_idx = 0
        #we can collide with another snake's head if we are longer than them
        if len(snake_body) < len(my_body):
            min_idx = 1
        for i in range(min_idx,len(snake_body)-1):
            if(snake_body[i]["x"] == my_head["x"]+1 and snake_body[i]["y"] == my_head["y"]):
                is_move_safe["right"] = False
            if(snake_body[i]["x"] == my_head["x"]-1 and snake_body[i]["y"] == my_head["y"]):
                is_move_safe["left"] = False
            if(snake_body[i]["y"] == my_head["y"]+1 and snake_body[i]["x"] == my_head["x"]):
                is_move_safe["up"] = False
            if(snake_body[i]["y"] == my_head["y"]-1 and snake_body[i]["x"] == my_head["x"]):
                is_move_safe["down"] = False
   
    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    print(safe_moves)
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    food = game_state['board']['food']
    foodDirection = {"right": False, "left":False, "up":False, "down":False}
    for foodPiece in food:
        if foodPiece["x"] == my_head["x"]:
            if foodPiece["y"] > my_head["y"]:
                foodDirection["up"]= True
            else:
                foodDirection["down"] = True
        if foodPiece["y"] == my_head["y"]:
            if foodPiece["x"] > my_head["x"]:
                foodDirection["right"] = True
            else:
                foodDirection["left"] = True
    next_move = None
    for dir in ["left","right", "up","down"]:
        if foodDirection[dir] and is_move_safe[dir]:
            next_move = dir
        elif next_move == None and is_move_safe[dir]:
            next_move = dir
    if next_move == None:
        next_move = "up"
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
from server import run_server
run_server({"info": info, "start": start, "move": move, "end": end})
