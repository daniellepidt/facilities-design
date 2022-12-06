"""
This file is used to transform a pickled file
into a list of items and then
load them into an Aisle.
Also, this file is used to store all the necessary items.
"""

import pickle
from classes import Aisle
from fetch import extract_probs
from logger import log
from globals import SIMULATION_START_TIME
from functools import reduce


def create_aisle():
    aisle = Aisle()
    return aisle

def get_items_for_storage(file_name="storage_list.p") -> dict[int]:
    """
    Returns a dict by the format of {item: amount_requested}
    containing all of the items needed for storage.
    """
    with open(file_name, "rb") as file:
        storage_list = pickle.load(file)
    # Transform into a dictionary by the format of
    # {item: amount_requested}:
    counts_by_item = {item[0]: item[1] for item in storage_list}
    log_opening = "Got the following items for storage:"
    log(SIMULATION_START_TIME, log_opening)
    for key, value in counts_by_item.items():
        key_value_log = f"{key}:{value}"
        log(SIMULATION_START_TIME, key_value_log)
    return counts_by_item


def time_preprocess():
    """
    Calculate a score for each cell according to 
    the collection time from it, in the worst case.
    The best score is the smallest score.
    """    
    # Create an aisle and define its parameters
    aisle = create_aisle()
    height = aisle.height
    width = aisle.width
    depth = aisle.depth   
    aisle_scores = aisle.storage
    aisle_scores_dict = {}

    # Calculate the time it takes to collect an item from a particular cell in the worst case.
    # The worst case - the elevator and the shuttle start to move together (and not one before the other).
    for h in range(height):
        for w in range(width):
            for d in range(depth):
                # Get the relevant parameters 
                vertical_move_time = aisle.elevator.vertical_move_time
                horizontal_move_time = aisle.shuttles[h].horizontal_move_time
                shuttle_load_time = aisle.shuttles[h].load_time 
                # Calculate
                elevator_move_time = h * vertical_move_time
                shuttle_move_time = 2*(d * horizontal_move_time) + shuttle_load_time
                socre = max(elevator_move_time, shuttle_move_time) + elevator_move_time
                aisle_scores[h][w][d] = socre
                aisle_scores_dict[(h, w, d)] = socre 
    # Sort the dictionary according to its values - from the smallest to the largest
    # that is, from the most attractive cell (closest) to the unattractive cell.
    aisle_scores_sorted = sorted(aisle_scores_dict.items(), key=lambda x:x[1])
    return aisle_scores, aisle_scores_sorted


def storing():
    """
    Store the items in storage by this heuristic: 
    The more likely (according probability) the item is, 
    the more attractive cell it will be stored (according to a score).
    """
    # Create an aisle and define its parameters
    aisle = create_aisle()
    height = aisle.height
    width = aisle.width
    depth = aisle.depth   
    aisle_storing = aisle.storage
    aisle_storing_dict = {}

    # Get the probabilities for each item, the storing requests, and the cell scores
    prob_list_sort = extract_probs()
    aisle_scores, aisle_scores_sotred = time_preprocess()
    available_cells_sorted = [cell[0] for cell in aisle_scores_sotred]
    counts_by_item = get_items_for_storage()

    # Make sure the request is reasonable
    total_required_units = counts_by_item.values()
    total_num_units = reduce(lambda a, b: a+b, total_required_units)
    if total_num_units > height * width * depth:
        raise ("Impossible to store all items in this storage")

    # Store the items by the heuristic
    for item_prob in prob_list_sort: # Store the items from the more likely item
        item = item_prob[0]
        if item in counts_by_item.keys(): # If this item is requested
            for unit in range(counts_by_item[item]): # Store all its unit in the current attractive cells
                current_cell = available_cells_sorted.pop(0)
                aisle_storing[current_cell[0]][current_cell[1]][current_cell[2]] = item
                if not item in aisle_storing_dict:
                    aisle_storing_dict[item] = [current_cell]
                else:
                    aisle_storing_dict[item].append(current_cell)

            # Make sure we placed all the units for this item
            if counts_by_item[item] < len(aisle_storing_dict[item]):
                print ("item %d - not all the units stored" % (item))
            elif counts_by_item[item] > len(aisle_storing_dict[item]):
                print ("item %d - too many units stored" % (item))

    # Make sure the storing is reasonable:
    # The number of available cells and the number of required units to store
    # is the size of the all storage
    num_available_units = len(available_cells_sorted)
    if total_num_units + num_available_units != height * width * depth:
        print("Wrong storing")

    return aisle_storing, aisle_storing_dict

aisle_storing, aisle_storing_dict = storing()
