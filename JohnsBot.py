import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import logging
import math
import random

# Some sort of defense (we get spear headed pretty hard)
# move to intercept attackers to prevent them from getting behind our main wall
# back up to regroup if it is a losing fight

# avoid combining -- use 2d strength map of future moves

# we lose battles against equally sized opponents

logging.basicConfig(filename='johnboronkas.log',level=logging.DEBUG)

myID, game_map = hlt.get_init()
prev_game_map = game_map

totalGameTurns = 10 * math.sqrt(game_map.width * game_map.height)
currentGameTurn = 0

totalMapSquares = game_map.width * game_map.height
ownedMapSquares = 0

numberPlayers = game_map.starting_player_count

# Do map analysis here (up to 15 seconds)

hlt.send_init("johnboronkas")

def direction_had_square_last_turn(square, direction):
    prevSquare = prev_game_map.get_target(square, direction)

    fuzzValue = prevSquare.strength * 0.25
    if prevSquare.strength - fuzzValue <= square.strength <= prevSquare.strength + fuzzValue:
        return True
    else:
        return False

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
    bestPriority = 999999
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        currentPriority = get_priority(current)
        while distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)

            if current.owner != myID:
                currentPriority = get_priority(current)

                #logging.info("before: " + str(currentPriority))
                #logging.info("dist: " + str(distance))
                currentPriority += distance * (distance / 3)
                #logging.info("after: " + str(currentPriority))

                if currentPriority < bestPriority:
                    direction = d
                    #max_distance = distance
                    bestPriority = currentPriority

    return direction

def get_priority(square):
    # Prioritize squares based on their production and strength value
    squareStrength = square.strength
    squareProduction = square.production

    if squareProduction <= 0:
        squareProduction = 1
        squareStrength += 25

    if squareProduction <= 2:
        squareStrength += 25
    elif squareProduction <= 4:
        squareStrength += 0
    elif squareProduction <= 6:
        squareStrength -= 25
    else:
        squareStrength -= 25

    if square.owner != myID:
        if square.owner != 0 and currentGameTurn <= (totalGameTurns / 3):
            squareStrength += 25

        if square.owner != 0 and currentGameTurn >= (totalGameTurns / 3):
            squareStrength -= 25
        elif square.owner == 0 and currentGameTurn <= (totalGameTurns / 3):
            squareStrength -= 25

    return squareStrength / squareProduction

def assign_move(square):
    bestPriority = 999999 # best target (lower is better)
    bestPriorityDirection = None

    for direction, neighbor in enumerate(game_map.neighbors(square)):
        # Has weaker player enemy -- so take it
        #if neighbor.owner != myID and neighbor.owner != 0 and square.strength >= neighbor.strength * 1.30:


        # Has stronger player enemy -- so attack into it
        if neighbor.owner != myID and neighbor.owner != 0 and square.strength <= neighbor.strength * 1.30:

            priority = get_priority(neighbor)

            # Adjust priorityRatio acording to amount of damage we will do if we attack this square
            # Most damage we can do is 1020 (255 * 4), so we scale based on that.
            damage = 0
            neighborCount = 1
            for neighbor in game_map.neighbors(square):
                if neighbor.owner not in (0, myID):
                    neighborCount += 1
                    damage += neighbor.strength

            # Scale the damage down to priority, then subtract it
            priority -= (damage / 8)

            if priority < bestPriority:
                bestPriority = priority
                bestPriorityDirection = direction
            continue

        # Has netural map square
        if neighbor.owner == 0:
            # Only consider squares that we can take right now
            if square.strength > neighbor.strength or square.strength == 255:
                priority = get_priority(neighbor)

                if priority < bestPriority:
                    bestPriority = priority
                    bestPriorityDirection = direction

            continue

    if bestPriorityDirection is not None:
        return Move(square, bestPriorityDirection)

    if ownedMapSquares <= ((totalMapSquares / numberPlayers) / 2):# and currentGameTurn <= (totalGameTurns / 3):
        nextDirection = find_nearest_value_square_direction(square)

        if nextDirection is None:
            nextDirection = find_nearest_enemy_direction(square)
        elif direction_had_square_last_turn(square, nextDirection):
            nextDirection = find_nearest_enemy_direction(square)
    else:
        nextDirection = find_nearest_enemy_direction(square)

    nextSquare = game_map.get_target(square, nextDirection)

    if nextSquare.owner != myID and (square.strength > nextSquare.strength or square.strength == 255):
        return Move(square, nextDirection)
    elif nextSquare.owner != myID and square.strength <= nextSquare.strength:
        return Move(square, STILL)
    elif nextSquare.owner == myID and not direction_had_square_last_turn(square, nextDirection):
        # Higher production squares should spend less time moving
        if square.strength >= (square.production * (4 + square.production / 2)):
            return Move(square, nextDirection)
        else:
            return Move(square, STILL)
    else:
        return Move(square, STILL)

while True:
    # 1 second per turn
    game_map.get_frame()
    currentGameTurn += 1

    moves = list()
    squareCount = 0
    for square in game_map:
        if square.owner == myID:
            squareCount += 1
            moves.append(assign_move(square))

    ownedMapSquares = squareCount
    prev_game_map = game_map
    hlt.send_frame(moves)
