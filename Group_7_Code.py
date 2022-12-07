from globals import SIMULATION_START_TIME
from logger import create_log_file, log
from storage import get_items_for_storage, store_items_in_aisle
from fetch import generate_random_requests
from classes import Aisle

if __name__ == "__main__":
    create_log_file()  # Create the log file
    # Get the storage list:
    storage_list = get_items_for_storage()
    aisle = Aisle()
    # Start the storage process:
    item_storage_by_location_dict = store_items_in_aisle(storage_list, aisle)
    print(item_storage_by_location_dict)
    print(aisle.storage)
    # Create the requests:
    requests = generate_random_requests(storage_list)
    current_time = SIMULATION_START_TIME
    # Start the fetching process:
    # TODO: Create a fetching process
