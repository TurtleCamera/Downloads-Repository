from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1 

# Tree node. To be used to construct a game tree. 
class Node: 
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (copy.deepcopy(state[0]), state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        # Check if there are any non-Nones in the list
        return_value = True
        for child in self.children:
            if (not (child == None)):
                return_value = False

        # if(self.player_type == MAX_PLAYER):
        #     print(return_value)

        return (return_value)

# AI agent. Determine the next move.
class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3): 
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    # (Hint) Useful functions: 
    # self.simulator.current_state, self.simulator.set_state, self.simulator.move

    # TODO: build a game tree from the current node up to the given depth
    def build_tree(self, node = None, depth = 0):
        # If we reached the bottom of the tree, then just do
        # nothing (maybe set the children array to nothing,
        # so the is_terminal function will return True)
        if (depth == 0):
            node.children = []
            return

        # Build the tree depending on what type of player this is
        if (node.player_type == MAX_PLAYER):
            # Deep copy the current tiles
            current_tiles = copy.deepcopy(node.state[0])
            current_score = node.state[1]

            # For each direction, reset the game to the current state
            # and pick a direction to move in
            
            # Up
            self.simulator.set_state(current_tiles, current_score)
            if(self.simulator.move(0)):
                # Don't go down the tree if we didn't actually move
                child_node_up = Node(self.simulator.current_state(), CHANCE_PLAYER)
                self.build_tree(child_node_up, depth - 1)
                node.children.append(child_node_up)
            else:
                # Put a filler node
                node.children.append(None)
            
            # Left
            self.simulator.set_state(current_tiles, current_score)
            if(self.simulator.move(1)):
                # Don't go down the tree if we didn't actually move
                child_node_left = Node(self.simulator.current_state(), CHANCE_PLAYER)
                self.build_tree(child_node_left, depth - 1)
                node.children.append(child_node_left)
            else:
                # Put a filler node
                node.children.append(None)
            
            # Down
            self.simulator.set_state(current_tiles, current_score)
            if(self.simulator.move(2)):
                # Don't go down the tree if we didn't actually move
                child_node_down = Node(self.simulator.current_state(), CHANCE_PLAYER)
                self.build_tree(child_node_down, depth - 1)
                node.children.append(child_node_down)
            else:
                # Put a filler node
                node.children.append(None)
            
            # Right
            self.simulator.set_state(current_tiles, current_score)
            if(self.simulator.move(3)):
                # Don't go down the tree if we didn't actually move
                child_node_right = Node(self.simulator.current_state(), CHANCE_PLAYER)
                self.build_tree(child_node_right, depth - 1)
                node.children.append(child_node_right)
            else:
                # Put a filler node
                node.children.append(None)

            # if node.children:
            #     print(node.children)
            
            # Shouldn't have to handle the case of terminating nodes here. If the
            # list is empty, it should automatically be terminating
        elif (node.player_type == CHANCE_PLAYER):
            # Deep copy the current tiles
            current_tiles = copy.deepcopy(node.state[0])
            current_score = node.state[1]

            # First, we need to get the list of coordinates for all open tiles
            self.simulator.set_state(current_tiles, current_score)
            open_tile_coords = copy.deepcopy(self.simulator.get_open_tiles())

            # For each open tile, add a 2 tile
            for coordinate in open_tile_coords:
                # Put a new 2-tile
                self.simulator.set_state(current_tiles, current_score)
                i = coordinate[0]
                j = coordinate[1]
                self.simulator.tile_matrix[i][j] = 2

                # Create a new node
                child_node = Node(self.simulator.current_state(), MAX_PLAYER)

                # Go down the tree
                self.build_tree(child_node, depth - 1)

                # Add the child node to the list of children
                node.children.append(child_node)
            
            # Shouldn't have to handle the case of terminating nodes here. If the
            # list is empty, it should automatically be terminating

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node = None):
        # If we're at a leaf node, just return the score
        if node.is_terminal():
            return (None, node.state[1])

        # What type of node are we on?
        if (node.player_type == MAX_PLAYER):
            # TODO: delete this random choice but make sure the return type of the function is the same
            return_value = (random.randint(0, 3), 0)

            # Loop through the children nodes to determine which direction to choose
            for direction in range(4):
                # Make sure it's not a "None" emtry (couldn't move in that direction)
                if (not (node.children[direction] == None)):
                    expectimax_value = self.expectimax(node.children[direction])
                    expectimax_value = expectimax_value[1]  # The only time the direction really matters is at the root node
                    if (expectimax_value > return_value[1]):
                        return_value = (direction, expectimax_value)
            
            # Return the direction and value
            return return_value
        elif (node.player_type == CHANCE_PLAYER):
            # TODO: delete this random choice but make sure the return type of the function is the same
            return_value = (None, 0)

            # Loop through the children nodes to sum the 
            for child in node.children: 
                expectimax_value = self.expectimax(child)
                # print(expectimax_value)
                expectimax_value = expectimax_value[1]  # The only time the direction really matters is at the root node
                return_value = (None, expectimax_value + return_value[1])
            
            # The value we return is the "average" of all the children's expectimax values
            return (None, return_value[1] / len(node.children))

    # Return decision at the root
    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        # print(self.root.children)
        direction, _ = self.expectimax(self.root)
        return direction

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax_ec(self, node = None):
        # If we're at a leaf node, just return the score
        if node.is_terminal():
            # Open tiles heuristic
            self.simulator.set_state(copy.deepcopy(node.state[0])) # Copy board state
            open_tiles_heuristic = len(self.simulator.get_open_tiles()) * 15    # "15 points" for each open tile

            # Max tile in corner heuristic
            max_tile = max([max(self.simulator.tile_matrix[0]), max(self.simulator.tile_matrix[1]), max(self.simulator.tile_matrix[2]), max(self.simulator.tile_matrix[3])])
            is_on_corner = self.simulator.tile_matrix[0][0] == max_tile or self.simulator.tile_matrix[0][3] == max_tile or self.simulator.tile_matrix[3][0] == max_tile or self.simulator.tile_matrix[0][3] == max_tile

            # Sum all the differences of adjacent tiles
            total_differences = 0
            for row in range(4):
                for col in range(4):
                    # Make sure we don't go out of bounds in each direction
                    # Left
                    if col - 1 > 0:
                        total_differences += abs(self.simulator.tile_matrix[row][col] - self.simulator.tile_matrix[row][col - 1])
                    # Right
                    if col + 1 < 0:
                        total_differences += abs(self.simulator.tile_matrix[row][col] - self.simulator.tile_matrix[row][col + 1])
                    # Down
                    if row + 1 < 0:
                        total_differences += abs(self.simulator.tile_matrix[row][col] - self.simulator.tile_matrix[row + 1][col])
                    # Down
                    if row - 1 > 0:
                        total_differences += abs(self.simulator.tile_matrix[row][col] - self.simulator.tile_matrix[row - 1][col])
            
            # Make sure this value isn't too big
            # total_differences /= 100000

            # Penalty for tiles not near the border
            total_away_from_border_penalty = 0
            for row in range(4):
                for col in range(4):
                    # Set some high value
                    penalty_amount = 100000
                    penalty_amount = min(penalty_amount, row)
                    penalty_amount = min(penalty_amount, col)
                    penalty_amount = min(penalty_amount, 3 - row)
                    penalty_amount = min(penalty_amount, 3 - col)

                    # Multiply that value with the tile value and add it to the total
                    total_away_from_border_penalty += penalty_amount * self.simulator.tile_matrix[row][col]
            
            # total_away_from_border_penalty /= 100000

            # Add all the heuristics together
            heuristic_value = 0
            heuristic_value += open_tiles_heuristic
            if is_on_corner:
                heuristic_value += 10
            heuristic_value -= total_differences
            heuristic_value -= total_away_from_border_penalty
            # print(node.state[1], open_tiles_heuristic, total_differences, total_away_from_border_penalty)
            return (None, node.state[1] + heuristic_value)

        # What type of node are we on?
        if (node.player_type == MAX_PLAYER):
            # TODO: delete this random choice but make sure the return type of the function is the same
            return_value = (random.randint(0, 3), 0)

            # Loop through the children nodes to determine which direction to choose
            for direction in range(4):
                # Make sure it's not a "None" emtry (couldn't move in that direction)
                if (not (node.children[direction] == None)):

                    # Compute expectimax value
                    expectimax_value = self.expectimax_ec(node.children[direction])
                    expectimax_value = expectimax_value[1]  # The only time the direction really matters is at the root node

                    # Choose this direction?
                    if (expectimax_value > return_value[1]):
                        return_value = (direction, expectimax_value)
            
            # Return the direction and value
            return return_value
        elif (node.player_type == CHANCE_PLAYER):
            # TODO: delete this random choice but make sure the return type of the function is the same
            return_value = (None, 0)

            # Loop through the children nodes to sum the 
            for child in node.children: 
                expectimax_value = self.expectimax_ec(child)
                # print(expectimax_value)
                expectimax_value = expectimax_value[1]  # The only time the direction really matters is at the root node
                return_value = (None, expectimax_value + return_value[1])
            
            # The value we return is the "average" of all the children's expectimax values
            return (None, return_value[1] / len(node.children))

    # TODO (optional): implement method for extra credits
    def compute_decision_ec(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax_ec(self.root)
        return direction

