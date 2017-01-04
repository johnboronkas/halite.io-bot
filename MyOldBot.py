import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import logging
import random

# focus fire best common square in the area

# focus on fighting towards high production zones

# Some sort of defense (we get spear headed pretty hard)
# move to intercept attackers to prevent them from getting behind our main wall
# back up to regroup if it is a losing fight

# avoid combining

logging.basicConfig(filename='johnboronkas.log',level=logging.DEBUG)

distancePriority = random.uniform(-5.0, 5.0) # 1.5 # -5 to 5
logging.info("distancePriority: " + str(distancePriority))

zeroSquareProduction = random.uniform(0, 5) # 0 to 5
logging.info("zeroSquareProduction: " + str(zeroSquareProduction))

squareProductionValue = random.uniform(0, 10) # 0 to 10
logging.info("squareProductionValue: " + str(squareProductionValue))

ownedSquareStrength = random.uniform(0, 255) # 0 to 255
logging.info("ownedSquareStrength: " + str(ownedSquareStrength))

squareShouldGrowValue = random.uniform(0, 15) # 0 to 15
logging.info("squareShouldGrowValue: " + str(squareShouldGrowValue))

wastedStrengthValue = random.uniform(0, 510) # 0 to 510
logging.info("wastedStrengthValue: " + str(wastedStrengthValue))

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
    direction = None
    max_distance = min(game_map.width, game_map.height) / 2
    bestPriority = 999
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        currentPriority = get_priority(current)
        while distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)

        if current.owner != myID:
            currentPriority = get_priority(current)

            # Scale based on distance
            currentPriority += float(distance * distancePriority) # VALUE distancePriority

            if current.owner != myID and currentPriority < bestPriority:
                direction = d
                max_distance = distance
                bestPriority = currentPriority

    return direction

def get_priority(square):
    # Prioritize squares based on their production and strength value
    squareProduction = square.production
    if squareProduction == 0:
        squareProduction += zeroSquareProduction # VALUE zeroSquareProduction
    else:
        squareProduction *= (squareProduction + squareProductionValue) # VALUE squareProductionValue

    # Treat non-neutral squares as stronger (since they are probably protected)
    squareStrength = square.strength
    if square.owner != 0 or square.owner != myID:
        squareStrength += ownedSquareStrength # VALUE ownedSquareStrength

    priorityRatio = squareStrength / float(squareProduction)
    return priorityRatio

def assign_move(square):
    shouldGrow = False # weak squares need to grow before moving

    bestAttackRatio = 999 # best target (lower is better)
    bestAttackRatioDirection = None

    hasPlayerTarget = False # we prioritise player targets over netural targets

    for direction, neighbor in enumerate(game_map.neighbors(square)):
        # Needs to grow more
        if square.strength < square.production * squareShouldGrowValue: # VALUE squareShouldGrowValue
            shouldGrow = True
            break

        # Has player enemy
        if neighbor.owner != myID and neighbor.owner != 0:
            # Redirect our attack to a player if we haven't already
            if not hasPlayerTarget:
                bestAttackRatio = 999
                bestAttackRatioDirection = None
                hasPlayerTarget = True

            priorityRatio = get_priority(neighbor)

            # Adjust priorityRatio acording to amount of damage we will do if we attack this square
            # Most damage we can do is 1020 (255 * 4), so we scale based on that.
            damage = sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))

            # Scale the damage down to priority, then subtract it
            priorityRatio = priorityRatio - (damage / 8)

            if priorityRatio < bestAttackRatio:
                bestAttackRatio = priorityRatio
                bestAttackRatioDirection = direction
            continue

        # Has netural map square
        if neighbor.owner == 0:
            # Only consider squares that we can take right now
            if square.strength > neighbor.strength:
                priorityRatio = get_priority(neighbor)

                if priorityRatio < bestAttackRatio:
                    bestAttackRatio = priorityRatio
                    bestAttackRatioDirection = direction

            continue

    if shouldGrow:
        return Move(square, STILL)

    if bestAttackRatioDirection is not None:
        return Move(square, bestAttackRatioDirection)

    # We have only friendlies around us.
    # Move towards the closest high priority square that we don't own.
    nearestBestSquareDirection = find_nearest_value_square_direction(square)
    if nearestBestSquareDirection is None:
        # No best high priority square, so move towards the border
        return Move(square, find_nearest_enemy_direction(square))

    nextSquare = game_map.get_target(square, nearestBestSquareDirection)

    # Only move against a netural square if we can take it.
    if nextSquare.owner == 0:
        if square.strength > nextSquare.strength:
            return Move(square, nearestBestSquareDirection)
        else:
            return Move(square, STILL)

    elif nextSquare.owner == myID:
        # Move is into our own square
        # Only move into our own square if we don't waste "too much" production
        if (square.strength + nextSquare.strength) <= wastedStrengthValue: # VALUE wastedStrengthValue
            return Move(square, nearestBestSquareDirection)

    return Move(square, STILL)


while True:
    # 1 second per turn
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
