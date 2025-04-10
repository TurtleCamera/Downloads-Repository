import random
import copy

def simulate_qingque():
    tiles = {'A', 'B', 'C'}  # 3 types of tiles
    MAX_TILES = 4
    hand = []
    draws = 0

    # Keep looping until we have a matching hand (4 tiles of the same type)
    while len(hand) < MAX_TILES or len(set(hand)) > 1:
        # Draw a new tile
        new_tile = random.choice(list(tiles))
        draws += 1

        # Directly add the tile to the hand if we don't have 4 tiles yet
        if len(hand) < MAX_TILES:
            hand.append(new_tile)
        else:
            # Otherwise, check to see if it's possible to replace any of the
            # tiles with the newly-drawn tile in such a way that it doesn't
            # decrease the number of any group of existing matching tiles.

            # After considering all cases, only the two can happen:
            # 1) If replacing a tile increases the highest number of
            #    matching tiles, prioritize this new hand.
            # 2) If #1 doesn't happen, but replacing a tile does 
            #    increases the number of least matching tiles in the
            #    original hand, then keep this new hand.

            # First, check our current hand. Count the number of most
            # matching tiles and least matching tiles.
            # Highest count
            max_count_tiles = max(set(hand), key=hand.count)
            current_highest_count = hand.count(max_count_tiles)
            # Least count
            min_count_tiles = min(set(hand), key=hand.count)
            current_least_count = hand.count(min_count_tiles)

            # Loop through the tiles in the hand and try replacing them.
            best_next_hand = None
            for i in range(len(hand)):
                # Skip checking this index if the tile matches the one we drew.
                if(hand[i] == new_tile):
                    continue

                # If it's a different tile, try replacing it.
                next_hand = copy.deepcopy(hand)
                next_hand[i] = new_tile

                # Highest count for the new hand
                max_count_tiles = max(set(next_hand), key=next_hand.count)
                next_highest_count = next_hand.count(max_count_tiles)
                # Does this increase the highest number of matching tiles?
                if next_highest_count > current_highest_count:
                    # We can stop checking here because increasing the
                    # highest number of matching tiles is always the
                    # best choice for reaching 4 matching tiles.
                    best_next_hand = next_hand
                    break

                # Least count
                min_count_tiles = min(set(next_hand), key=next_hand.count)
                next_least_count = next_hand.count(min_count_tiles)
                # Does this increase the lowest number of matching tiles? Make
                # sure this also doesn't decrease the highest number of matching
                # tiles.
                if next_least_count > current_least_count and next_highest_count == current_highest_count:
                    # Store this hand, but don't break just in case we get the
                    # first case. This condition should only happen at most once
                    # per newly-drawn tile.
                    best_next_hand = next_hand
            
            # If the best_next_hand isn't None, then replace the current hand.
            if best_next_hand is not None:
                hand = best_next_hand

    return draws

def average_draws(num_simulations):
    total_draws = sum(simulate_qingque() for _ in range(num_simulations))
    avg_draws = total_draws / num_simulations
    return avg_draws

# Number of simulations
num_simulations = 10000000
average = average_draws(num_simulations)
print(f"Average number of draws to get 4 matching tiles: {average}")