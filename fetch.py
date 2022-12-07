"""
This file contains the logic needed to create fetch orders
from a relevant pickle file.
"""

import pickle
from numpy.random import choice, seed
from globals import ITEMS_IN_FETCH, SIMULATION_START_TIME
from collections import Counter
from logger import log
from classes import Request


# TODO: Create a common functionality for getting the pickle file and use it in both functions.
def get_items_list_sorted_by_probability(file_name="prob_list.p"):
    """
    Extracts from the pickle file the pairs of items & probabilities,
    and returns them sorted in a descending order by probability.
    """
    with open(file_name, "rb") as file:
        prob_list = pickle.load(file)
    return sorted(prob_list, key=lambda x: x[1], reverse=True)

def generate_random_requests(items_for_storage: Counter) -> Counter:
    """
    Returns a dict by the format of {item: amount_requested}
    containing all of the randomly generated requests.
    """
    prob_list = get_items_list_sorted_by_probability()
    # Split the prob_list into two lists, of the items and their
    # respective probabilities:
    items, probabilities = map(list, zip(*prob_list))
    seed_value = 0
    while True:
        seed(seed_value)  # Seed the random number generator
        # Create a list of random requests:
        random_requests = sorted(choice(items, ITEMS_IN_FETCH, p=probabilities))
        # Transform into a dictionary by the format of
        # {item: amount_requested}:
        counts_by_item = Counter(random_requests)
        difference_from_allowed = counts_by_item - items_for_storage
        negative_values = [value < 0 for value in difference_from_allowed.values()]
        if not negative_values:
            break
        log(f"While using seed {seed_value}, generated an impossible request. Trying seed {seed_value + 1}.")
        seed_value += 1

    # TODO: Make sure that requests for specific items haven't exceeded the amount
    # available in storage.
    # TODO: Take care of cases where more then can be supply was requested:
    
    log_opening = f"Created the following {ITEMS_IN_FETCH} requests:"
    log(SIMULATION_START_TIME, log_opening)
    for key, value in counts_by_item.items():
        key_value_log = f"{key}:{value}"
        log(SIMULATION_START_TIME, key_value_log)
    # TODO: Decide if to use the Request class at all.
    # requests_list = [Request(item) for item in random_requests]
    # return requests_list
    return counts_by_item
