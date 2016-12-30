import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random

# focus fire best common square in the area

# focus on fighting towards high production zones

# Some sort of defense (we get spear headed pretty hard)
# move to intercept attackers to prevent them from getting behind our main wall
# back up to regroup if it is a losing fight

# TODO PICKUP large squares get afraid to move to avoid combining (move all squares )
# High to low helping causes "dancing"

myID, game_map = hlt.get_init()

# Do map analysis here (up to 15 seconds)
# TODO Find closest area with highest production furthest from any enemy

hlt.send_init("johnboronkas")

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
    
def find_nearest_value_square_direction(square):
    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 4
    bestPriority = 999
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        currentPriority = get_priority(current)
        while current.owner == myID and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
            currentPriority = get_priority(current)
        if currentPriority < bestPriority:
            direction = d
            max_distance = distance
            bestPriority = currentPriority
    return direction
    
def get_priority(square):
    # Prioritize squares with any amount of production (0 production squares don't have any return on investment)
    squareProduction = square.production
    if squareProduction == 0:
        squareProduction = 1
    else:
        squareProduction += 6
        
    # priorityRatio is usually around 3 to 25 (lower is better)
    priorityRatio = square.strength / squareProduction
    
    return priorityRatio

def assign_move(square):
    shouldGrow = False # weak squares need to grow before moving
    isBorder = False # border squares don't move unless they have a chance to attack

    bestPriorityRatio = 999 # best target (lower is better)
    bestPriorityRatioDirection = None
    
    hasPlayerTarget = False # we prioritise player targets over netural targets

    for direction, neighbor in enumerate(game_map.neighbors(square)):
        # Needs to grow more
        if square.strength < square.production * 4:
            shouldGrow = True
            break

        # Has player enemy
        if neighbor.owner != myID and neighbor.owner != 0:
            isBorder = True
        
            # Redirect our attack to a player if we haven't already
            if not hasPlayerTarget:
                bestPriorityRatio = 999
                bestPriorityRatioDirection = None
                hasPlayerTarget = True
        
            priorityRatio = get_priority(neighbor)
            
            # Adjust priorityRatio acording to amount of damage we will do if we attack this square
            # Most damage we can do is 1020 (255 * 4), so we scale based on that.
            damage = sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))
            
            # Scale the damage down to priority, then subtract it
            priorityRatio -= (damage / 8)
            
            if priorityRatio < bestPriorityRatio:
                bestPriorityRatio = priorityRatio
                bestPriorityRatioDirection = direction
            continue
            
        # Has netural map block
        if neighbor.owner == 0:
            isBorder = True
        
            # Only consider attacks that we can take right now
            if square.strength > neighbor.strength:
                priorityRatio = get_priority(neighbor)
                
                if priorityRatio < bestPriorityRatio:
                    bestPriorityRatio = priorityRatio
                    bestPriorityRatioDirection = direction
            continue

    if shouldGrow:
        return Move(square, STILL)

    if bestPriorityRatioDirection is not None:
        return Move(square, bestPriorityRatioDirection)
    else:
        # Move towards the closest high priority square.
        nearestBestSquareDirection = find_nearest_value_square_direction(square)
        nextSquare = game_map.get_target(square, nearestBestSquareDirection)
        
        if (square.strength + nextSquare.strength) <= 255:
            return Move(square, nearestBestSquareDirection)
        else:
            # TODO what to do instead?
            return Move(square, STILL)

    return Move(square, STILL)


while True:
    # 1 second per turn
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
