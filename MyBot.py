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

# Do map analysis here (up to 15 seconds)

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

def assign_move(square):
    shouldGrow = False # weak squares need to grow before moving
    isBorder = False # border squares don't move unless they have a chance to attack

    bestPriorityRatio = 999 # best target (lower is better)
    bestPriorityRatioDirection = None
    
    hasPlayerTarget = False # we prioritise player targets over netural targets
    
    lowestProductionFriendly = 999 # friendly that needs the most help
    lowestProductionFriendlyDirection = None

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
        
            # Prioritize squares with any amount of production (0 production squares don't have any return on investment)
            neighborProduction = neighbor.production
            if neighborProduction == 0:
                neighborProduction = 1
            else:
                neighborProduction += 5
                
            # priorityRatio is usually around 3 to 25 (lower is better)
            priorityRatio = neighbor.strength / neighborProduction
            
            # Adjust priorityRatio acording to amount of damage we will do if we attack this square
            # Most damage we can do is 1020 (255 * 4), so we scale based on that.
            damage = sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))
            
            # Scale the damage down to priority, then subtract it
            priorityRatio -= (damage / 10)
            
            if priorityRatio < bestPriorityRatio:
                bestPriorityRatio = priorityRatio
                bestPriorityRatioDirection = direction
            continue
            
        # Has a friendly (fallthrough)
        if neighbor.owner == myID:
            # Don't run if we already have a player target
            if hasPlayerTarget:
                continue
                
            # Support the surrounding square with the lowest production
            # NEVER allow a move that would cause a combination of 220 ish or more
            if square.production > neighbor.production and (square.strength + neighbor.strength) <= 220:
                if neighbor.production < lowestProductionFriendly:
                    lowestProductionFriendlyDirection = direction
                    
            # no continue, fallthrough to next section
            
            
        # Has netural map block
        if neighbor.owner == 0:
            isBorder = True
            
            # Don't reassign a target if we already have a human target
            if hasPlayerTarget:
                continue
        
            # Only consider attacks that we can take right now
            if square.strength > neighbor.strength:
                neighborProduction = neighbor.production
                if neighborProduction == 0:
                    neighborProduction = 1
                else:
                    neighborProduction += 5
                
                priorityRatio = neighbor.strength / neighborProduction
                
                if priorityRatio < bestPriorityRatio:
                    bestPriorityRatio = priorityRatio
                    bestPriorityRatioDirection = direction
            continue

    if shouldGrow:
        return Move(square, STILL)

    if bestPriorityRatioDirection is not None:
        return Move(square, bestPriorityRatioDirection)
    else:
        # Move towards the closest border if this square isn't on the border
        # NEVER allow a move that would cause a combination of 220 ish or more
        if not isBorder:
            closestDirection = find_nearest_enemy_direction(square)
            nextSquare = game_map.get_target(square, closestDirection)
            
            if (square.strength + nextSquare.strength) <= 220:
                return Move(square, find_nearest_enemy_direction(square))
            else:
                # TODO what to do instead?
                return Move(square, STILL)
            
        else:
            # On a border but don't have enough strength to attack.
            # So Move the high production squares towards lower production squares
            if lowestProductionFriendlyDirection is not None:
                return Move(square, lowestProductionFriendlyDirection)

    return Move(square, STILL)


while True:
    # 1 second per turn
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
