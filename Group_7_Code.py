from globals import SIMULATION_START_TIME
from logger import create_log_file, log
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle

if __name__ == "__main__":
    create_log_file()  # Create the log file
    # Get the storage list:
    items_for_storage = get_items_for_storage()
    sorted_items_probabilities_list = get_items_list_sorted_by_probability()
    aisle = Aisle()
    # Start the storage process:
    aisle.store_items(items_for_storage, sorted_items_probabilities_list)
    print("aisle.storage_dict")
    print(aisle.storage_dict)
    print("aisle.storage")
    print(aisle.storage)
    # Create the requests:
    list_of_requests = [
        generate_random_requests(
            items_for_storage, sorted_items_probabilities_list, seed
        )
        for seed in range(0, 100, 10)
    ]  # Create a list of 10 groups of 40 requests, each with a different seed.
    print("list_of_requests")
    print(list_of_requests)
    current_time = SIMULATION_START_TIME
    # Start the fetching process:
    # TODO: Create a fetching process
