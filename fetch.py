"""
This file contains the logic needed to create fetch orders
from a relevant pickle file.
"""

import pickle
from numpy.random import choice, seed
from globals import ITEMS_IN_FETCH, SIMULATION_START_TIME
from collections import Counter
from logger import log


def get_items_list_sorted_by_probability(file_name="prob_list.p") -> list[list]:
    """
    Extracts from the pickle file the pairs of items & probabilities,
    and returns them sorted in a descending order by probability.
    """
    with open(file_name, "rb") as file:
        prob_list = pickle.load(file)
    return sorted(prob_list, key=lambda x: x[1], reverse=True)


def generate_random_requests(
    items_for_storage: Counter, sorted_items_probabilities_list, seed_input=0
) -> Counter:
    """
    Returns a dict by the format of {item: amount_requested}
    containing all of the randomly generated requests.
    """
    # Split the sorted_items_probabilities_list into two lists, of the items and their
    # respective probabilities:
    items, probabilities = map(list, zip(*sorted_items_probabilities_list))
    seed_value = seed_input
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
        log(
            SIMULATION_START_TIME,
            f"While using seed {seed_value}, generated an impossible request. Trying seed {seed_value + 1}.",
        )
        seed_value += 1

    log_opening = f"Created request #{seed_value // 10} with the following {sum(counts_by_item.values())} items:"
    log(SIMULATION_START_TIME, log_opening)
    log(SIMULATION_START_TIME, counts_by_item)
    try:
        filename = f"request_{seed_value // 10}.p"
        with open(filename, "wb") as file:
            pickle.dump(random_requests, file)
        log(SIMULATION_START_TIME, f"Request Pickle file saved @ {filename}.")
    except Exception as e:
        log(SIMULATION_START_TIME, f"Failed to save request Pickle file.\nError: {e}")

    return counts_by_item
