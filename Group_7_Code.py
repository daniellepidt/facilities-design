from globals import SIMULATION_START_TIME, P
from logger import create_log_file, log, parser_simulation_time
from storage import get_items_for_storage
from fetch import get_items_list_sorted_by_probability, generate_random_requests
import pickle
from classes import Aisle, Event
from collections import Counter
import numpy as np
import heapq
from output import create_retrival_pickle_file, create_unified_results_csv


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


# For generating fetching events - returns nothing
def event_generator(
    aisle: Aisle, curr_time: float, request: Counter, request_index: int
) -> None:
    """
    Generates events
    """
    while True:
        relevant_locations = aisle.storage.copy()  # Building relevant locations matrix
        for key in request.keys():
            relevant_locations[
                relevant_locations == key
            ] = 1.0  # Assign all relevant items' locations into 1.0
        relevant_locations[
            relevant_locations != 1.0
        ] = 0.0  # Assign all irrelevant items' locations into 0.0

        if np.any(
            relevant_locations == 1.0
        ):  # If there are any relevant locations = there is at least one order to fetch
            # Building relavant times matrix
            relevant_times = np.multiply(
                relevant_locations, aisle.scores_cells_of_idle_time_array
            )
            relevant_times[relevant_times == 0.0] = np.inf
            next_time_elevator_is_free = find_max_element(P)
            relevant_times -= next_time_elevator_is_free
            i = None
            # Choose the cell on the lowest floor, to ensure minimal idle time
            for s in aisle.shuttles:
                # Calculate the idle time of the shuttle, according to the shuttle's last mission
                relevant_times[:][s.floor] += s.current_tasks_completion_time
                # If a cell provides idle time for the shuttle (and not for the elevator)
                if np.any(relevant_times[:][s.floor] <= 0.0):
                    relevant_times[relevant_times > 0.0] = np.nan
                    i = list(
                        np.unravel_index(
                            np.nanargmax(relevant_times[:][s.floor]),
                            relevant_times[:][s.floor].shape,
                        )
                    )
                    i.insert(0, s.floor)
                    i = tuple(i)  # i is an (i,j,k) index
                    break
            # If there is necessarily idle time for the elevator
            if i == None:
                i = np.unravel_index(np.argmin(relevant_times), relevant_times.shape)

            elevator_time_to_floor = aisle.elevator.vertical_move_time * i[0]
            elevator_arrival_to_floor_time = (
                next_time_elevator_is_free + elevator_time_to_floor
            )
            shuttle_fetch_time = (
                aisle.shuttles[i[0]].current_tasks_completion_time
                + (2 * aisle.shuttles[i[0]].horizontal_move_time * i[1])
                + aisle.shuttles[i[0]].load_time
            )
            time_until_shuttle_and_elevator_meet = max(
                elevator_arrival_to_floor_time, shuttle_fetch_time
            )

            item_unloaded_to_io_time = (
                time_until_shuttle_and_elevator_meet
                + aisle.shuttles[i[0]].unload_time
                + elevator_time_to_floor
                + aisle.elevator.unload_time
            )
            item = aisle.storage[i]
            request_metrics.append(
                [
                    item,
                    [i[0], i[1], i[2]],
                    time_until_shuttle_and_elevator_meet
                    + aisle.shuttles[i[0]].unload_time,
                    item_unloaded_to_io_time,
                ]
            )
            simulation_metrics.append(
                {
                    "request_index": request_index,
                    "height": i[0],
                    "width": i[2],
                    "depth": i[1],
                    "fetched_item": item,
                    "time_to_fulfillment": item_unloaded_to_io_time
                    - next_time_elevator_is_free,
                    "elevator_idle_time": max(
                        shuttle_fetch_time - elevator_arrival_to_floor_time, 0
                    ),  # If the elevator arrives before the shuttle, then it has idle time.
                    "shuttle_idle_time": max(
                        elevator_arrival_to_floor_time - shuttle_fetch_time, 0
                    ),  # If the shuttle arrives before the elevator, then it has idle time.
                }
            )
            Event(item_unloaded_to_io_time, item, aisle.shuttles[i[0]], i)
            log(
                curr_time,
                f"Shuttle #{i[0]} will bring item {int(item)} from {i} at {parser_simulation_time(int(shuttle_fetch_time))}.",
            )
            aisle.shuttles[i[0]].current_tasks_completion_time = (
                time_until_shuttle_and_elevator_meet + aisle.shuttles[i[0]].unload_time
            )
            request[item] -= 1
            if request[item] == 0:
                request.pop(item)
            aisle.storage[i] = 0
        else:
            # Stop looking for items to assign to the shuttle.
            break


if __name__ == "__main__":
    timestamp = create_log_file()  # Create the log file
    # Get the storage list - making global for this file:
    ITEMS_FOR_STORAGE = get_items_for_storage()
    SORTED_ITEMS_PROBABILITIES_LIST = get_items_list_sorted_by_probability()

    # Code for generating test requets:
    # REQUESTS = [
    #     generate_random_requests(
    #         ITEMS_FOR_STORAGE, SORTED_ITEMS_PROBABILITIES_LIST, seed
    #     )
    #     for seed in range(0, 100, 10)
    # ]  # Create a list of 10 groups of 40 requests, each with a different seed.
    
    # Code for getting the actual requests for analysis:
    REQUESTS = []
    for i in range(1,11):
        file_name = f"./requests/request_items_{i}.p"
        with open(file_name, "rb") as file:
            request_items = pickle.load(file)
        REQUESTS.append(Counter(request_items))
    log(SIMULATION_START_TIME, "All requests were created.")

    # Create metrics:
    request_c_max = []
    simulation_metrics = []  # Total simulation metrics for data analysis.

    # Start of the simulation
    for index, request in enumerate(REQUESTS):
        request_metrics = (
            []
        )  # Metrics for this request only, and for outputing Pickle file.
        curr_time = SIMULATION_START_TIME  # = 0
        log(curr_time, f"Handling request #{index}:")
        log(curr_time, request)
        aisle = Aisle()
        # Start the storage process:
        aisle.store_items(get_items_for_storage(), SORTED_ITEMS_PROBABILITIES_LIST)
        event_generator(aisle, curr_time, request, index)  # Creating 40 events
        while P:
            event = heapq.heappop(P)
            curr_time = event.time
            log(
                int(curr_time),
                f"The elevator unloaded item {int(event.item)} from {event.location}. {sum(request.values())} items left for collection.",
            )
        request_c_max.append(curr_time)
        create_retrival_pickle_file(curr_time, index, request_metrics)
        log(curr_time, f"Finished a requests round with C_max: {curr_time}")
log(curr_time, f"Finished all requests rounds with C_max: {request_c_max}")

create_unified_results_csv(timestamp, simulation_metrics)
log(curr_time, f"Created results file under: results/{timestamp}_results.csv")
