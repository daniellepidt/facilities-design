from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle, Event, EventType
import heapq

def create_shuttle_fetch(s,el): # Gets shuttle - for not duplicating code
    if not s.carrying:
        # If the shuttle is empty
        r = s.tasks.pop(0)
        s.carrying = aisle.storage[r[0]][r[1]][r[2]]
        s.position = r
        el.tasks.append(r[0])
        e = Event(current_time+s.horizontal_move_time*2*r[2]+s.load_time,EventType.ELEVATOR_LOAD,s.carrying,s)
        e.heappush(P)

         

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
    aisle_scores = aisle.calculate_travel_times_by_cell()[0]
    aisle_scores_sorted = aisle.calculate_travel_times_by_cell()[1]
    
    current_time = SIMULATION_START_TIME
    # Start the fetching process:
    # Preprocessing the requests:
    shuttles_tasks = {i:[] for i in range(8)}
    for r in list_of_requests:
        for key in r:
            while r[key] > 1:
                for s in aisle_scores_sorted:
                    print(aisle.storage[s[0][0]][s[0][1]][s[0][1]])
                    if aisle.storage[s[0][0]][s[0][1]][s[0][1]] in r.keys():
                        r[key] -= 1
                        shuttles_tasks[s[0][0]].append(s[0])
                        aisle_scores_sorted.remove(s)
                        break
    print(shuttles_tasks)
    print(aisle.shuttles)
    for n in shuttles_tasks: # Setting the tasks to the shuttles
        for s in aisle.shuttles:
            s.set_tasks(n)
    # First events
    el = aisle.elevator
    for s in aisle.shuttles:
        create_shuttle_fetch(s,el)
    event = heapq.heappop(P)
    curr_time = event.time
    


                    