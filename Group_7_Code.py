from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle, Event, Shuttle
from collections import Counter
import numpy as np
import heapq

# def create_shuttle_fetch(s,el): # Gets shuttle - for not duplicating code
#     if not s.carrying:
#         # If the shuttle is empty
#         r = s.tasks.pop(0)
#         s.carrying = aisle.storage[r[0]][r[1]][r[2]]
#         s.position = r
#         el.tasks.append(r[0])
#         e = Event(current_time+s.horizontal_move_time*2*r[2]+s.load_time,EventType.ELEVATOR_LOAD,s.carrying,s)
#         e.heappush(P)
# Get the storage list - making global:
ITEMS_FOR_STORAGE = get_items_for_storage()
SORTED_ITEMS_PROBABILITIES_LIST = get_items_list_sorted_by_probability()
AISLE = Aisle()
# Start the storage process:
AISLE.store_items(ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST)
print("aisle.storage_dict")
print(AISLE.storage_dict)
print("aisle.storage")
print(AISLE.storage)
storage_copy = AISLE.storage.copy()
# Create the global requests:
REQUESTS = [
    generate_random_requests(
        ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST, seed
    )
    for seed in range(0, 100, 10)
]  # Create a list of 10 groups of 40 requests, each with a different seed.
print("list_of_requests")
print(REQUESTS)

aisle_scores = AISLE.calculate_travel_times_by_cell()[0]

def find_max_element(heap):
    n = len(heap)
    max_element = heap[n // 2]
    for i in range(1 + n // 2, n):
        max_element = max(max_element,heap[i])
    return max_element

def check_fetching(relevant_times: np.array):
    if np.any(relevant_times) <= 0:
        relevant_times[relevant_times>0] = 0
        # חישוב מדד זמן בטלה לשאטל
        return np.unravel_index(np.nanargmax(np.where(relevant_times != 0, relevant_times, np.nan)),relevant_times.shape)
    else:
        # חישוב מדד זמן בטלה למעלית
        return np.unravel_index(np.argmin(relevant_times))


def event_generator(curr_time, request):
    while True:
        # Get the unique values from the order
        counts_by_item = Counter(request)
        # Building relevant locations matrix
        relevant_locations = AISLE.storage.copy()
        for s in AISLE.shuttles:
            if not s.carrying:
                relevant_locations[:][s.floor] = 1.0
            else:
                relevant_locations[:][s.floor] = 0.0
        if np.any(relevant_locations) == 1.0:
            # Building relavant times matrix
            relevant_times = np.multiply(relevant_locations,aisle_scores)
            relevant_times[relevant_times==0.0] = np.inf
            available_time_range = curr_time - find_max_element(P).time
            relevant_times -= available_time_range
            i = check_fetching(relevant_times)
            Event()#Need to fill
            storage_copy[i] = 0
            request.remove(storage_copy[i])
        else:
            break



if __name__ == "__main__":
    create_log_file()  # Create the log file

    curr_time = SIMULATION_START_TIME
    # Start the fetching process
    # Creating First events
    
    # Start of the simulation
    for request in REQUESTS:
        event_generator(curr_time,request)
        event = heapq.heappop(P)
        curr_time = event.time
        while P:
            event.shuttle.carrying = None
            event_generator(curr_time,request)
            event = heapq.heappop(P)
            curr_time = event.time
    
    


                    