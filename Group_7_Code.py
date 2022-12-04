from globals import SIMULATION_START_TIME
from logger import create_log_file, log
from storage import get_items_for_storage
import numpy as np
from fetch import create_requests

if __name__ == "__main__":
    create_log_file()  # Create the log file
    # Get the storage list:
    storage_list = get_items_for_storage()

    # Start the storage process:
    # TODO: Create a storage process

    np.random.seed(0)  # Seed the random number generator
    # Create the requests:
    requests = create_requests()
    current_time = SIMULATION_START_TIME
    # Start the fetching process:
    # TODO: Create a fetching process
