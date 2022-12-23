from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log, parser_simulation_time
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
from classes import Aisle, Event
from collections import Counter
import numpy as np
import heapq


def find_max_element(heap) -> float:
    """
    Find a Heap objects event with the latest time,
    and return that time value as a float.
    """
    # Get no. of nodes
    n = len(heap)
    if n == 0:  # If the heap is empty
        return 0.0
    max_element = heap[n // 2]
    for i in range(1 + n // 2, n):
        max_element = max(max_element, heap[i])
    return float(max_element.time)


# For event_generator - returns index
def check_fetching(relevant_times: np.ndarray) -> tuple[int]:
    """
    A function which receives the relevant_times Numpy array,
    and return the index of the the best cell from which to
    fetch an item.
    The index returns as a tuple of (i,j,k).
    """
    if np.any(relevant_times <= 0.0):
        relevant_times[relevant_times > 0.0] = np.nan
        # חישוב מדד זמן בטלה לשאטל
        return np.unravel_index(np.nanargmax(relevant_times), relevant_times.shape)
    else:
        # חישוב מדד זמן בטלה למעלית
        return np.unravel_index(np.argmin(relevant_times), relevant_times.shape)


# For generating fetching events - returns nothing
def event_generator(aisle: Aisle, curr_time: float, request: Counter) -> None:
    """
    Generates events
    """
    shuttle_load_time = aisle.shuttles[0].load_time
    shuttle_unload_time = aisle.shuttles[0].unload_time
    shuttle_horizontal_move_time = aisle.shuttles[0].horizontal_move_time
    elevator_unload_time = aisle.elevator.unload_time
    elevator_vertical_move_time = aisle.elevator.vertical_move_time
    while True:
        # Get the unique values from the order
        # counts_by_item = Counter(request) - i think don't need
        # Building relevant locations matrix
        relevant_locations = aisle.storage.copy()
        # Building events for every available shuttle
        for key in request.keys():
            relevant_locations[relevant_locations == key] = 1.0
        # for s in aisle.shuttles:
        #     if s.carrying:  # The shuttle is not available
        #         relevant_locations[:][s.floor] = 0.0
        relevant_locations[relevant_locations != 1.0] = 0.0
        """
        If there are any relevant locations = at least one shuttle is 
        availble and there is an order to fetch
        """
        if np.any(relevant_locations == 1.0):
            # Building relavant times matrix
            
            next_time_elevator_is_free = find_max_element(P)
            
            fetch_time_matrix = np.zeros((aisle.height, aisle.width, aisle.depth))
            for h in range(aisle.height):
                # Get the shuttle action times:
                horizontal_move_time = aisle.shuttles[h].horizontal_move_time
                shuttle_load_time = aisle.shuttles[h].load_time
                elevator_time_to_floor = h * aisle.elevator.vertical_move_time
                # elevator_time_to_floor = elevator_vertical_move_time * h
                elevator_arrival_to_floor_time = (
                    next_time_elevator_is_free + elevator_time_to_floor
                )
                for w in range(aisle.width):
                    for d in range(aisle.depth):
                        # Calculate:
                        shuttle_move_time = (
                            2 * (d * horizontal_move_time) + shuttle_load_time
                        )
                        shuttle_fetch_time = (
                            aisle.shuttles[h].current_tasks_completion_time
                            + shuttle_move_time
                            + shuttle_load_time
                        )
                        time_until_shuttle_and_elevator_meet = max(
                            elevator_arrival_to_floor_time, shuttle_fetch_time
                        )
                        item_unloaded_to_io_time = (
                            time_until_shuttle_and_elevator_meet
                            + shuttle_unload_time
                            + elevator_time_to_floor
                            + elevator_unload_time
                        )
                        # For each cell - calculate the idle time for the elevator (the cell grade)
                        fetch_time_matrix[h][w][d] = item_unloaded_to_io_time



            relevant_times = np.multiply(relevant_locations, fetch_time_matrix)
            relevant_times[relevant_times == 0.0] = np.inf
            # for s in aisle.shuttles:
            #     relevant_times[:][s.floor] += max(
            #         s.current_tasks_completion_time
            #     )
            
            # available_time_range = curr_time - next_time_elevator_is_free
            # relevant_times += available_time_range
            # relevant_times -= next_time_elevator_is_free
            i = check_fetching(relevant_times)  # i is an (i,j,k) index
            elevator_time_to_floor = elevator_vertical_move_time * i[0]
            elevator_arrival_to_floor_time = (
                next_time_elevator_is_free + elevator_time_to_floor
            )
            shuttle_fetch_time = (
                aisle.shuttles[i[0]].current_tasks_completion_time
                + (2 * shuttle_horizontal_move_time * i[2])
                + shuttle_load_time
            )
            time_until_shuttle_and_elevator_meet = max(
                elevator_arrival_to_floor_time, shuttle_fetch_time
            )

            item_unloaded_to_io_time = (
                time_until_shuttle_and_elevator_meet
                + shuttle_unload_time
                + elevator_time_to_floor
                + elevator_unload_time
            )
            item = aisle.storage[i]
            events_list.append([i, item, item_unloaded_to_io_time])
            Event(
                item_unloaded_to_io_time, item, aisle.shuttles[i[0]], i
            )
            log(
                curr_time,
                f"Shuttle #{i[0]} will bring item {int(item)} from {i} at {parser_simulation_time(int(shuttle_fetch_time))}.",
            )
            aisle.shuttles[i[0]].carrying = item
            aisle.shuttles[i[0]].current_tasks_completion_time = time_until_shuttle_and_elevator_meet + shuttle_unload_time
            request[item] -= 1
            if request[item] == 0:
                request.pop(item)
            aisle.storage[i] = 0
        else:
            # log(curr_time, "No relevant shuttles or items found for fetch.")
            break


if __name__ == "__main__":
    create_log_file()  # Create the log file
    # Get the storage list - making global for this file:
    ITEMS_FOR_STORAGE = get_items_for_storage()
    SORTED_ITEMS_PROBABILITIES_LIST = get_items_list_sorted_by_probability()

    # Create the global requests:
    REQUESTS = [
        generate_random_requests(
            ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST, seed
        )
        for seed in range(0, 100, 10)
    ]  # Create a list of 10 groups of 40 requests, each with a different seed.

    request_c_max = []
    # Start of the simulation
    for request in REQUESTS:
        print(sum(request.values()))
        aisle = Aisle()
        # Start the storage process:
        aisle.store_items(get_items_for_storage(), SORTED_ITEMS_PROBABILITIES_LIST)
        # print("aisle.storage")
        # print(aisle.storage)
        # For the fetching process:
        # storage_copy = aisle.storage.copy()
        aisle_scores = aisle.cell_travel_times_array
        curr_time = SIMULATION_START_TIME
        events_list = []
        print("Starting to handle a new request") # TODO: Replace with log function
        print(request)
        # Creating First events
        event_generator(aisle, curr_time, request)
        event = heapq.heappop(P)
        curr_time = event.time
        while P:
            log(
                int(curr_time),
                f"The elevator unloaded item {int(event.item)} from {event.location}. {sum(request.values())} items left for collection.",
            )
            event.shuttle.carrying = None
            event_generator(aisle, curr_time, request)
            # print("Continue to next event")
            event = heapq.heappop(P)
            curr_time = event.time
        request_c_max.append(curr_time)
        print(sum(request.values()))
        log(curr_time, f"Finished a requests round with C_max: {request_c_max}")
log(curr_time, f"Finished all requests rounds with C_max: {request_c_max}")
