from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle, Event, EventType
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
# Create the global requests:
REQUESTS = [
    generate_random_requests(
        ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST, seed
    )
    for seed in range(0, 100, 10)
]  # Create a list of 10 groups of 40 requests, each with a different seed.
print("list_of_requests")
print(REQUESTS)

def check_fetching(s):
    tasks = []
    for r in REQUESTS:
        for key in r.keys():
            if key in AISLE.storage[s.floor]:
                tasks.append(key)
    return tasks

def next_task_huristic(s):
    if not s.carrying:
        tasks = check_fetching(s)
        for t in tasks:
            pass


if __name__ == "__main__":
    create_log_file()  # Create the log file

    aisle_scores = AISLE.calculate_travel_times_by_cell()[0]
    aisle_scores_sorted = AISLE.calculate_travel_times_by_cell()[1]
    print(aisle_scores)
    print(aisle_scores_sorted)
    curr_time = SIMULATION_START_TIME
    # Start the fetching process
    # First events
    el = AISLE.elevator
    for s in AISLE.shuttles:
        next_task_huristic(s)
    event = heapq.heappop(P)
    curr_time = event.time
    


                    