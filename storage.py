"""
This file is used to transform a pickled file
into a list of items and then
load them into an Aisle.
Also, this file is used to store all the necessary items.
"""

import pickle
from classes import Aisle
from fetch import get_items_list_sorted_by_probability
from collections import Counter
from logger import log
from globals import ITEMS_IN_FETCH, SIMULATION_START_TIME, PrivateError


def get_items_for_storage(file_name="storage_list.p") -> Counter:
    """
    Returns a Counter by the format of {item: amount_requested}
    containing all of the items needed for storage.
    """
    with open(file_name, "rb") as file:
        storage_list = pickle.load(file)
    # Transform into a dictionary by the format of
    # {item: amount_requested}:
    items_for_storage = {item[0]: item[1] for item in storage_list}
    log_opening = "Got the following items for storage:"
    log(SIMULATION_START_TIME, log_opening)
    for key, value in items_for_storage.items():
        key_value_log = f"{key}:{value}"
        log(SIMULATION_START_TIME, key_value_log)
    return Counter(items_for_storage)


def calculate_travel_times_by_cell(aisle: Aisle):
    """
    Calculate a score for each cell according to
    the collection time from it, in the worst case.
    The best score is the smallest score.
    """
    aisle_scores = aisle.storage
    aisle_scores_dict = {}
    # Calculate the time it takes to collect an item from a particular cell in the worst case.
    # The worst case - the elevator and the shuttle start to move together (and not one before the other).
    vertical_move_time = (
        aisle.elevator.vertical_move_time
    )  # Get the elevator travel time
    for h in range(aisle.height):
        # Get the shuttle action times:
        horizontal_move_time = aisle.shuttles[h].horizontal_move_time
        shuttle_load_time = aisle.shuttles[h].load_time
        for w in range(aisle.width):
            for d in range(aisle.depth):
                # Calculate:
                elevator_move_time = h * vertical_move_time
                shuttle_move_time = 2 * (d * horizontal_move_time) + shuttle_load_time
                score = max(elevator_move_time, shuttle_move_time) + elevator_move_time
                aisle_scores[h][w][d] = score
                aisle_scores_dict[(h, w, d)] = score
    # Sort the dictionary according to its values - from the smallest to the largest
    # that is, from the most attractive cell (closest) to the unattractive cell.
    aisle_scores_sorted = sorted(aisle_scores_dict.items(), key=lambda x: x[1])
    return aisle_scores, aisle_scores_sorted


def store_items_in_aisle(items_for_storage: Counter, aisle: Aisle):
    """
    Store the items in storage by this heuristic:
    First, by expectations (probability of item * request size):
    The more likely (according *expectation*) the item is,
    the more attractive cell it will be stored in (according to the score)
    (each time - store one unit of the item with the highest expectation).
    Then, by probabilities:  
    The more likely (according *probability*) the item is,
    the more attractive cell it will be stored in (according to the score)
    (each time - store all the remaining units of the item with the highest probability).
    """
    height, width, depth = aisle.height, aisle.width, aisle.depth
    aisle_storage = aisle.storage.copy()
    items_for_storage_for_monitoring = items_for_storage.copy()
    item_storage_by_location_dict = {}

    # Get the probabilities for each item, and calculate expectations
    sorted_items_probabilities_list = get_items_list_sorted_by_probability()
    sorted_items_expectation_dict = {}
    for i in range(len(sorted_items_probabilities_list)):
        item_expectation = int(sorted_items_probabilities_list[i][1] * ITEMS_IN_FETCH)
        sorted_items_expectation_dict[sorted_items_probabilities_list[i][0]] = item_expectation

    # Get the storing requests, and the cell scores
    aisle_scores, aisle_scores_sorted = calculate_travel_times_by_cell(aisle)
    available_cells_sorted = [cell[0] for cell in aisle_scores_sorted]

    # Make sure the request is reasonable
    total_num_units = sum(items_for_storage_for_monitoring.values())
    if total_num_units > height * width * depth:
        raise PrivateError("Impossible to store all items in this storage")

    # Store the items by the heuristic

    # First, store according to expectations
    # each time - store one unit of the item with the highest expectation
    sort_by_expectation = True
    while sort_by_expectation: # As long as one of the items has a expectation greater than 0
        # Select the next item to store:
        # check if this item is requested & if its expectation greater than 0
        for key, value in sorted_items_expectation_dict.items():
            if items_for_storage[key] > 0  and value > 0:
                current_item = key
                break
        
        # Select the next cell to store in (the available cell with the highest score)
        current_cell = available_cells_sorted.pop(0)
        
        # Store
        aisle_storage[current_cell[0]][current_cell[1]][current_cell[2]] = current_item

        if not current_item in item_storage_by_location_dict:
            item_storage_by_location_dict[current_item] = [current_cell]
        else:
            item_storage_by_location_dict[current_item].append(current_cell)

        # Update number of units to be stored for this item
        items_for_storage[current_item] -= 1

        # Update the current items expectation, 
        # and then sort the updated expectation dictionary
        sorted_items_expectation_dict[current_item] -= 1
        sorted_items_expectation_tuples = sorted(sorted_items_expectation_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_items_expectation_dict = {k: v for k, v in sorted_items_expectation_tuples}
        
        # Check if there are more items to store by expectations
        if list(sorted_items_expectation_dict.values())[0] == 0:
            sort_by_expectation = False            
    
    # Now, store the rest of the units according to probabilities
    # Each time - store all the remaining units of the item with the highest probability
    for (
        item_and_probability
    ) in sorted_items_probabilities_list:  # Store the items from the more likely item
        current_item = item_and_probability[0]
        if items_for_storage[current_item] > 0:  # If this item is requested
            for unit in range(
                items_for_storage[current_item]
            ):  
                # Select the next cell to store in (the available cell with the highest score)
                current_cell = available_cells_sorted.pop(0)
                # Store
                aisle_storage[current_cell[0]][current_cell[1]][current_cell[2]] = current_item
                if not current_item in item_storage_by_location_dict:
                    item_storage_by_location_dict[current_item] = [current_cell]
                else:
                    item_storage_by_location_dict[current_item].append(current_cell)

            # Make sure we placed all the units for this item
            if items_for_storage_for_monitoring[current_item] < len(item_storage_by_location_dict[current_item]):
                raise PrivateError (f"Logical Error: Item {current_item} - not all the units stored")
            elif items_for_storage_for_monitoring[current_item] > len(item_storage_by_location_dict[current_item]):
                raise PrivateError (f"Logical Error: Item {current_item} - too many units stored")

    # Make sure the storing is reasonable:
    # The number of available cells and the number of required units to store
    # is the size of the all storage
    num_available_units = len(available_cells_sorted)
    if total_num_units + num_available_units != height * width * depth:
        raise PrivateError ("Wrong storing")

    # Update the storage
    aisle.storage = aisle_storage
    
    # TODO: Create logic to output a pickle file with the selected
    # storage decision.

    # TODO: Add GUI showing the storage decision.
    
    return item_storage_by_location_dict

"""
items_for_storage = get_items_for_storage()
aisle = Aisle()
print(store_items_in_aisle(items_for_storage, aisle))
"""