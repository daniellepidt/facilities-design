"""
This file is used to transform a pickled file
into a list of items and then
load them into an Aisle.
"""

import pickle
from classes import Aisle
from logger import log
from globals import SIMULATION_START_TIME


def create_aisle():
    aisle = Aisle()


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
