"""
This file is used to transform a pickled file
into a list of items and then
load them into an Aisle.
Also, this file is used to store all the necessary items.
"""

import pickle
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
    log_opening = f"Got the following {sum(items_for_storage.values())} items for storage:"
    log(SIMULATION_START_TIME, log_opening)
    log(SIMULATION_START_TIME, items_for_storage)
    return Counter(items_for_storage)
