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
import numpy.typing as npt
from enum import Enum
#Perimeter of the area that the snake looks at when determining where to go
LOOKAHEAD_DIST = 5
MAX_SIDE_LOOK = 3

#Number of empty squares in a direction at which point the snake stops looking for
#free space and starts chasing food 
MIN_AREA = 5 
#Number of moves that the code tries to predict for other snakes
#  (it simply predicts that they continue to go in the same direction)
PREDICTION_DIST =3 

SERVER_PORT = 8000

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "dragonslayer",  # TODO: Your Battlesnake Username
        "color": "#3FAFFF",  # TODO: Choose color
        "head": "dragon",  # TODO: Choose head
        "tail": "bolt",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

class Dir(Enum):
    LEFT=0
    UP=1
    RIGHT=2
    DOWN=3
class BoardSquare(Enum):
    EMPTY = 0
    FOOD = 1
    SNAKE = 2
    SNAKE_PROJECTION = 3

DirectionVectors = {
    Dir.LEFT : np.array([-1,0]),
    Dir.UP : np.array([0,1]),
    Dir.RIGHT : np.array([1,0]),
    Dir.DOWN : np.array([0, -1])
}



#Use an integer array for better performance
#Array is indexed first by x coordinate, then by y coordinate
#Each square is represented by a 3-element array
#First element represents type of object-- index into boardsquare enum
#For snake:
#       -Element 2: id of snake that it is
#       -Element 3: distance of snake segment from tail
#For snake projection:
#       -Element 2: id of snake that may enter the square
#        -Element 3: # of moves until that snakes head will enter 
 
def createBoardArray(game_state: typing.Dict)-> npt.NDArray:
    arr = np.zeros((game_state["board"]["width"], game_state["board"]["height"], 3), np.int32)
    #place food pieces on board
    for foodPiece in game_state["board"]["food"]:
        arr[foodPiece["x"]][foodPiece["y"]].put([0,1,2],[BoardSquare.FOOD.value, 0,0])
    for i in range(0,len(game_state["board"]["snakes"])):
        currentSnake = game_state["board"]["snakes"][i]
        #place current locations of snake segments
        for j in range(1,len(currentSnake["body"])):
            bodySegment = currentSnake["body"][j]
            arr[bodySegment["x"]][bodySegment["y"]].put([0,1,2],[BoardSquare.SNAKE.value,i,len(currentSnake["body"]) - j-1])
        currentHeadPos = np.array([currentSnake["head"]["x"], currentSnake["head"]["y"]])
        direction = np.array([currentSnake["head"]["x"] - currentSnake["body"][1]["x"],
                      currentSnake["head"]["y"] - currentSnake["body"][1]["y"]])
        #place projected future locations of snake segments
        for j in range (1,PREDICTION_DIST+1):
            headPos = currentHeadPos + direction * j
            if (min(headPos[0],headPos[1]) > 0 and headPos[0] < game_state["board"]["width"]
                    and headPos[1] < game_state["board"]["height"]):
                if arr[headPos[0],headPos[1]][0] == BoardSquare.EMPTY.value:
                    arr[headPos[0],headPos[1]].put([0,1,2],[BoardSquare.SNAKE_PROJECTION.value,i,j])
    return arr
def inBounds(location: npt.NDArray[(2)], board_array) -> bool:
    return (location[0] >= 0 and location[1] >= 0
        and location[0] < len(board_array)
        and location[1] < len(board_array[0]))

def exploreDirection(direction: Dir, snake: typing.Dict, board_array: npt.NDArray):
    print('Explore Direction: '+direction.name)
    #current snake head position
    position = np.array([snake["head"]["x"], snake["head"]["y"]])
    #direction in which to explore
    directionVec = DirectionVectors[direction]
    perpVec = np.flip(directionVec)
    #distance to closest food item in region
    dstFood = len(board_array) + 100

    if(not inBounds(position+directionVec,board_array)): return {'foodDistance':100000000000, 'area':0,'snakeHeadCollision':None}
    locationsToExplore = set([tuple(position+directionVec)])
    clearSquares = 0
    snakeHeadCollision = None
    for i in range(1,LOOKAHEAD_DIST+1):
        print('Round '+str(i) +' Exploring locations: '+str(locationsToExplore))
        nextLocations = set()
        for locationTuple in locationsToExplore:
            location = np.array(locationTuple)
            square = board_array[location[0],location[1]]
            #if this point  will not be occupied by a deadly snake when we arrive
            if ((square[0] != BoardSquare.SNAKE.value or square[2] < i-1)
                    and (square[0] != BoardSquare.SNAKE_PROJECTION.value or square[2]>i)):
                #if this point is food, update distance to food
                if square[0] == BoardSquare.FOOD.value:
                    dstFood = min(dstFood,i)
                clearSquares += 1
                #add new locations in the same direction relative to the current pos
                #that can be reached through this location
                newLoc = location + directionVec
                if inBounds(newLoc,board_array): nextLocations.add(tuple(newLoc))
                #We don't want to double back on ourselves in the perpendicular direction so
                #we only add the perpendicular vector with the same sign as our
                #initial perpendicular displacement
                if(math.abs(np.dot(location-position, perpVec)) < MAX_SIDE_LOOK):
                    if np.dot(location-position, perpVec) >=0 and inBounds(location+perpVec,board_array):
                        nextLocations.add(tuple(location + perpVec))
                    if np.dot(location-position,perpVec) <=0 and inBounds(location-perpVec,board_array):
                        nextLocations.add(tuple(location-perpVec))
            #If our head will arrive at the square at the same time as the head of another snake
            elif(square[0] == BoardSquare.SNAKE_PROJECTION.value and square[2]==i and snakeHeadCollision == None):
                #Record that snake
                snakeHeadCollision = {'id': square[1], 'dist':square[2]}
        locationsToExplore = nextLocations
    return {'foodDistance': dstFood, 'area':clearSquares, 'snakeHeadCollision':snakeHeadCollision}


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_snake = game_state['you']
    snake_list = game_state['board']['snakes']
    board_array = createBoardArray(game_state)
    print(board_array)
    area=0
    foodDist = len(board_array)+10000
    moveDirection = None
    snakeHeadCollision = None
    
    currentDirection = np.array([my_snake['head']['x'] - my_snake['body'][1]['x'],
                                my_snake['head']['y'] - my_snake['body'][1]['y']])
    
    #we cannot reverse direction
    safeDirections = [d for d in Dir if (DirectionVectors[d] != currentDirection*-1).any()]
    for direction in safeDirections:
        info = exploreDirection(direction, my_snake, board_array)
        #If we can eat another snake, move toward its head
        if (info['snakeHeadCollision'] != None and 
                len(snake_list[info['snakeHeadCollision']['id']]['body']) < len(my_snake['body']) and
                (snakeHeadCollision == None or snakeHeadCollision['dist'] > info['snakeHeadCollison']['dist'])):
            moveDirection = direction
            snakeHeadCollision = info['snakeHeadCollision']
        #If we are below the minimum open area try to move in a direction with more open spaces
        elif (area < MIN_AREA and info['area'] > area):
            moveDirection = direction
            area = info['area']
            foodDist = info['foodDistance']
        #Otherwise move in the direction closest to food
        elif (foodDist > info['foodDistance']):
            moveDirection = direction
            area= info['area']
            foodDist = info['foodDistance']
    print(f"MOVE {game_state['turn']}: {moveDirection}")
    return {"move" : moveDirection.name.lower()}


# Start server when `python main.py` is run
from server import run_server
run_server({"info": info, "start": start, "move": move, "end": end},port=SERVER_PORT)
