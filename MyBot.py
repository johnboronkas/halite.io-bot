import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random

# in opening, focus more on creating bigger squares to focus fire the
# best one in the area

# Add overkill logic
# And combined attack

# focus on fighting towards high production zones

# Favor player targets over nutral targets (to a degree)

# Some sort of defense (we get spear headed pretty hard)
# move to intercept attackers to prevent them from getting behind our main wall
# back up to regroup if it is a losing fight

# instead of just going to nearest enemy, move to nearest enemy with the
# highest priorityRatio

myID, game_map = hlt.get_init()
hlt.send_init("PythonBot")

def find_nearest_enemy_direction(square):
    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 2
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        while current.owner == myID and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
        if distance < max_distance:
            direction = d
            max_distance = distance
    return direction

def assign_move(square):
    shouldGrow = False

    attackDirection = None

    bestPriorityRatio = 999 # best target
    bestPriorityRatioDirection = None

    for direction, neighbor in enumerate(game_map.neighbors(square)):

        # Needs to grow more
        if square.strength < square.production * 4:
            shouldGrow = True
            break

        # Has enemy
        if neighbor.owner != myID:
            neighborProduction = neighbor.production
            if neighborProduction == 0:
                neighborProduction = 1
            else:
                neighborProduction += 6
            priorityRatio = neighbor.strength / neighborProduction
            if priorityRatio < bestPriorityRatio:
                bestPriorityRatio = priorityRatio
                bestPriorityRatioDirection = direction
            continue

    if shouldGrow:
        return Move(square, STILL)

    if bestPriorityRatioDirection is not None:
        if game_map.get_target(square, bestPriorityRatioDirection).strength < square.strength:
            return Move(square, bestPriorityRatioDirection)
        else:
            return Move(square, STILL)
    else:
        border = any(neighbor.owner != myID for neighbor in game_map.neighbors(square))
        if not border:
            return Move(square, find_nearest_enemy_direction(square))
        else:
            return Move(square, STILL)

    return Move(square, STILL)


while True:
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
