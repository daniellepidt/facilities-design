"""
This file contains the logic needed to create fetch orders
from a relevant pickle file.
"""

import pickle
from numpy.random import choice
from globals import ITEMS_IN_FETCH, SIMULATION_START_TIME
from collections import Counter
from logger import log
from classes import Request


def create_requests(file_name="prob_list.p") -> dict[int]:
    """
    Returns a dict by the format of {item: amount_requested}
    containing all of the randomly generated requests.
    """
    with open(file_name, "rb") as file:
        prob_list = pickle.load(file)
    # Split the prob_list into two lists, of the items and their
    # respective probabilities:
    items, probabilities = map(list, zip(*prob_list))
    # Create a list of random requests,
    # by the seed declared outside of this function:
    random_requests = sorted(choice(items, ITEMS_IN_FETCH, p=probabilities))
    # Transform into a dictionary by the format of
    # {item: amount_requested}:
    counts_by_item = Counter(random_requests)
    log_opening = f"Created the following {ITEMS_IN_FETCH} requests:"
    log(SIMULATION_START_TIME, log_opening)
    for key, value in counts_by_item.items():
        key_value_log = f"{key}:{value}"
        log(SIMULATION_START_TIME, key_value_log)
    # TODO: Decide if to use the Request class at all.
    # requests_list = [Request(item) for item in random_requests]
    # return requests_list
    return counts_by_item
