from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle, Event, Shuttle
from collections import Counter
import numpy as np
import heapq

# Get the storage list - making global for this file:
ITEMS_FOR_STORAGE = get_items_for_storage()
SORTED_ITEMS_PROBABILITIES_LIST = get_items_list_sorted_by_probability()
AISLE = Aisle()
# Start the storage process:
AISLE.store_items(ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST)
print("aisle.storage")
print(AISLE.storage)

# Create the global requests:
REQUESTS = [
    generate_random_requests(
        ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST, seed
    )
    for seed in range(0, 100, 10)
]  # Create a list of 10 groups of 40 requests, each with a different seed.
print("list_of_requests")
print(REQUESTS)

# For the fetching process:
storage_copy = AISLE.storage.copy()
aisle_scores = AISLE.calculate_travel_times_by_cell()[0]
s_for_times = AISLE.shuttles[0] # Just to get times
el_for_times = AISLE.elevator # Just to get times

# Functions for the fetching process:
# For finding the time of the last task
def find_max_element(heap) -> float:
    # Get no. of nodes
    n = len(heap)
    if n == 0: # If the heap is empty
        return 0.0
    max_element = heap[n // 2]
    for i in range(1 + n // 2, n):
        max_element = max(max_element,heap[i])
    return float(max_element.time)

# For event_generator - returns index
def check_fetching(relevant_times: np.array):
    if np.any(relevant_times) <= 0:
        relevant_times[relevant_times>0] = np.nan
        # חישוב מדד זמן בטלה לשאטל
        return np.unravel_index(np.nanargmax(),relevant_times.shape)
    else:
        # חישוב מדד זמן בטלה למעלית
        return np.unravel_index(np.argmin(relevant_times),relevant_times.shape)

# For generating fetching events - returns nothing
def event_generator(curr_time:int, request):
    while True:
        print("Creating new event: " + str(curr_time))
        # Get the unique values from the order
        # counts_by_item = Counter(request) - i think don't need
        # Building relevant locations matrix
        relevant_locations = AISLE.storage.copy()
        # Building events for every available shuttle
        for s in AISLE.shuttles:
            if not s.carrying:
                # If there is a relevant cell for the order
                for key in request.keys():
                    relevant_locations[relevant_locations==key] = 1.0
            else: # The shuttle is not available
                relevant_locations[:][s.floor] = 0.0
        relevant_locations[relevant_locations!=1.0] = 0.0
        """
        If there are any relevant locations = at least one shuttle is 
        availble and there is order to fetch
        """
        print("relevant_locations")
        print(relevant_locations)
        if np.any(relevant_locations) == 1.0:
            # Building relavant times matrix
            relevant_times = np.multiply(relevant_locations,aisle_scores)
            relevant_times[relevant_times==0.0] = np.inf
            max_time = find_max_element(P)
            available_time_range = curr_time - max_time
            relevant_times -= available_time_range
            print("relevant_times")
            print(relevant_times)
            i = check_fetching(relevant_times)
            if aisle_scores[i] <= 0: # If the elevator is idle
                """
                The event will end when the elevator will finish it's tasks,
                and because it is idle, we will sum the finish time of the last
                task, the time the shuttle goes to the item, loads it and goes
                back to the elevator, loads it to the elevetor, the elevator
                goes to the I/0 and then unloads to the truck.
                """
                Event(max_time+2*s_for_times.horizontal_move_time*i[1]+s_for_times.load_time+s_for_times.unload_time+el_for_times.vertical_move_time*i[0]+el_for_times.unload_time,storage_copy[i],AISLE.shuttles[i[0]])
            else: # If the shuttle is idle
                Event(max_time+2*el_for_times.vertical_move_time+s_for_times.unload_time+el_for_times.unload_time,storage_copy[i],AISLE.shuttles[i[0]])
            AISLE.shuttles[i[0]].carrying = storage_copy[i]
            request[storage_copy[i]]-=1
            storage_copy[i] = 0
        else:
            print("No relevant shuttle/items")
            break



if __name__ == "__main__":
    create_log_file()  # Create the log file

    # Start the fetching process 
    # elevator_tasks = [0]
    # shuttle_tasks = []
    # times = []
    request_c_max = []
    # Start of the simulation
    for request in REQUESTS:
        print("Starting to handle a new request")
        # Creating First events
        curr_time = SIMULATION_START_TIME
        event_generator(curr_time,request)
        event = heapq.heappop(P)
        curr_time = event.time
        while P:
            print("P:")
            print(P)
            print("The shuttle is available")
            event.shuttle.carrying = None
            event_generator(curr_time,request)
            print("Continiue to next event")
            event = heapq.heappop(P)
            curr_time = event.time
        request_c_max.append(curr_time)
print(request_c_max)    
    


                    