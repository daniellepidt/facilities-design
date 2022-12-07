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
from globals import SIMULATION_START_TIME


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
    The more likely (according probability) the item is,
    the more attractive cell it will be stored in (according to the score).
    """
    height, width, depth = aisle.height, aisle.width, aisle.depth
    item_storage_by_location_dict = {}

    # Get the probabilities for each item, the storing requests, and the cell scores
    sorted_items_probabilities_list = get_items_list_sorted_by_probability()
    aisle_scores, aisle_scores_sorted = calculate_travel_times_by_cell(aisle)
    available_cells_sorted = [cell[0] for cell in aisle_scores_sorted]

    # Make sure the request is reasonable
    total_num_units = sum(items_for_storage.values())
    if total_num_units > height * width * depth:
        raise ("Impossible to store all items in this storage")

    # Store the items by the heuristic
    for (
        item_and_probability
    ) in sorted_items_probabilities_list:  # Store the items from the more likely item
        item = item_and_probability[0]
        if item in items_for_storage.keys():  # If this item is requested
            for unit in range(
                items_for_storage[item]
            ):  # Store all its unit in the current attractive cells
                # TODO: Add functionality which takes into consideration the
                # expected n*p for each item and doesn't store beyond needed in attractive locations.
                current_cell = available_cells_sorted.pop(0)
                aisle.storage[current_cell[0]][current_cell[1]][current_cell[2]] = item
                if not item in item_storage_by_location_dict:
                    item_storage_by_location_dict[item] = [current_cell]
                else:
                    item_storage_by_location_dict[item].append(current_cell)

            # Make sure we placed all the units for this item
            if items_for_storage[item] < len(item_storage_by_location_dict[item]):
                raise (f"Logical Error: Item {item} - not all the units stored")
            elif items_for_storage[item] > len(item_storage_by_location_dict[item]):
                raise (f"Logical Error: Item {item} - too many units stored")

    # Make sure the storing is reasonable:
    # The number of available cells and the number of required units to store
    # is the size of the all storage
    num_available_units = len(available_cells_sorted)
    if total_num_units + num_available_units != height * width * depth:
        print("Wrong storing")

    # TODO: Create logic to output a pickle file with the selected
    # storage decision.

    # TODO: Add GUI showing the storage decision.

    return item_storage_by_location_dict
