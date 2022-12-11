from enum import Enum
import heapq as hq
import numpy as np
import uuid
from collections import Counter
from globals import ITEMS_IN_FETCH, SIMULATION_START_TIME, PrivateError
from logger import log


class EventType(Enum):
    ELEVATOR_MOVEMENT = 1
    SHUTTLE_FETCH = 2
    ELEVATOR_LOAD = 3
    ELEVATOR_UNLOAD = 4

    def __repr__(self):
        return self.name.lower().replace("_", " ")


class Item:
    def __init__(self, type):
        self.id = uuid.uuid4().hex  # Create a unique identifier for this item.


class Request:
    def __init__(
        self,
        item,
    ):
        self.item = item
        self.supply_time = None

    def __repr__(self):
        return f"Request for #{self.item}"

    def supplied(self, time):
        self.supply_time = time
        print()


class Event:
    def __init__(self, time, type=EventType.ELEVATOR_MOVEMENT, item=None, P=[]):
        self.time = time  # event time
        self.type = type  # event type
        self.item = item  # The Item related to the event
        self.P = P  # Heap used for events
        hq.heappush(P, self)  # add the event to the events list

    def __lt__(self, other_event):
        return self.time < other_event.time


class Aisle:
    def __init__(self, height=8, width=2, depth=16):
        self.height = height
        self.width = width
        self.depth = depth
        # Create an array of 'height' floors, with 'width' number of cells per 'depth'.
        self.storage = np.zeros((height, width, depth))
        self.storage_dict = {}
        # Only pass in elevation settings if any were added
        self.elevator = Elevator()
        self.shuttles = [Shuttle(floor) for floor in range(height)]
        (
            self.cell_travel_times_array,
            self.cell_travel_times_dict,
        ) = self.calculate_travel_times_by_cell()

    def __repr__(self):
        return "Aisle"

    def calculate_travel_times_by_cell(self):
        """
        Our basic assumption is that the elevator is the bottleneck 
        (single elevator VS 8 shuttles),
        so we would like to minimize the idle time of the elevator.
        Calculate a score for each cell according to
        minimum idle time of the elevator, in the worst case.
        """
        aisle_scores = self.storage.copy()
        positive_scores_dict = {}
        negative_scores_dict = {}
        zero_scores_dict = {}
        # Calculate the time it takes to collect an item from a particular cell in the worst case,
        # and then calculate idle time of the elevator.
        # The worst case - the elevator and the shuttle start to move together (and not one before the other).
        vertical_move_time = (
            self.elevator.vertical_move_time
        )  # Get the elevator travel time
        for h in range(self.height):
            # Get the shuttle action times:
            horizontal_move_time = self.shuttles[h].horizontal_move_time
            shuttle_load_time = self.shuttles[h].load_time
            elevator_move_time = h * vertical_move_time
            for w in range(self.width):
                for d in range(self.depth):
                    # Calculate:
                    shuttle_move_time = (
                        2 * (d * horizontal_move_time) + shuttle_load_time
                    )
                    # For each cell - calculate the idle time for the elevator (the cell grade)
                    score = shuttle_move_time - elevator_move_time
                    aisle_scores[h][w][d] = score
                    if score > 0:
                        positive_scores_dict[(h, w, d)] = score
                    elif score < 0:
                        negative_scores_dict[(h, w, d)] = score
                    else:
                        zero_scores_dict[(h, w, d)] = score
        # Sort the scores so that they result in minimum idle time in general, and for the elevator in particular:
        # 1. score 0 (no idle time; The elevator and the shuttle arrived at the same time). 
        # 2. negative scores - from the greater to the smaller (minimum idle time for the shuttle; The elevator is on its way)
        # 3. positive scores - from the smaller to the greater (minimum idle time for the elevator; The shuttle is on its way)
        zero_scores_sorted = sorted(zero_scores_dict.items(), key=lambda x: x[1])
        negative_scores_sorted = sorted(negative_scores_dict.items(), key=lambda x: x[1], reverse=True)
        positive_scores_sorted = sorted(positive_scores_dict.items(), key=lambda x: x[1])
        aisle_scores_sorted = zero_scores_sorted + negative_scores_sorted + positive_scores_sorted
        return aisle_scores, aisle_scores_sorted

    def store_items(
        self,
        items_for_storage: Counter,
        sorted_items_probabilities_list,
        simulation_time=SIMULATION_START_TIME,
    ):
        """
        Store the items in storage by this heuristic:
        First, by expectations (probability of item * request size):
        The more likely (according *expectation*) the item is,
        the more attractive cell it will be stored in (according to the score)
        (each time - store one unit of the item with the highest expectation).
        Then, by probabilities:
        The more likely (according *probability*) the item is,
        the more attractive cell it will be stored in (according to the score)
        (each time - store all the remaining units of the item with the highest probability).
        """
        height, width, depth = self.height, self.width, self.depth
        aisle_storage = self.storage.copy()
        items_for_storage_for_monitoring = items_for_storage.copy()
        item_storage_by_location_dict = {}

        # Get the probabilities for each item, and calculate expectations
        sorted_items_expectation_dict = {}
        for i in range(len(sorted_items_probabilities_list)):
            item_expectation = int(
                sorted_items_probabilities_list[i][1] * ITEMS_IN_FETCH
            )
            sorted_items_expectation_dict[
                sorted_items_probabilities_list[i][0]
            ] = item_expectation

        # Get the storing requests, and the cell scores
        _, available_cells_sorted = [cell[0] for cell in self.cell_travel_times_dict]

        # Make sure the request is reasonable
        total_num_units = sum(items_for_storage_for_monitoring.values())
        if total_num_units > height * width * depth:
            raise PrivateError(
                f"Number of items for storage is greater then the amount of storage available in the {self}."
            )

        # Store the items by the heuristic:
        # First, store according to expectations
        # each time - store one unit of the item with the highest expectation
        sort_by_expectation = True
        while (
            sort_by_expectation
        ):  # As long as one of the items has a expectation greater than 0
            # Select the next item to store:
            # check if this item is requested & if its expectation greater than 0
            for key, value in sorted_items_expectation_dict.items():
                if items_for_storage[key] > 0 and value > 0:
                    current_item = key
                    break

            # Select the next cell to store in (the available cell with the highest score)
            current_cell = available_cells_sorted.pop(0)

            # Store
            aisle_storage[current_cell[0]][current_cell[1]][
                current_cell[2]
            ] = current_item

            if not current_item in item_storage_by_location_dict:
                item_storage_by_location_dict[current_item] = [current_cell]
            else:
                item_storage_by_location_dict[current_item].append(current_cell)

            # Update number of units to be stored for this item
            items_for_storage[current_item] -= 1

            # Update the current items expectation,
            # and then sort the updated expectation dictionary
            sorted_items_expectation_dict[current_item] -= 1
            sorted_items_expectation_tuples = sorted(
                sorted_items_expectation_dict.items(), key=lambda x: x[1], reverse=True
            )
            sorted_items_expectation_dict = {
                k: v for k, v in sorted_items_expectation_tuples
            }

            # Check if there are more items to store by expectations
            if list(sorted_items_expectation_dict.values())[0] == 0:
                sort_by_expectation = False

        # Now, store the rest of the units according to probabilities
        # Each time - store all the remaining units of the item with the highest probability
        for (
            item_and_probability
        ) in (
            sorted_items_probabilities_list
        ):  # Store the items from the more likely item
            current_item = item_and_probability[0]
            if items_for_storage[current_item] > 0:  # If this item is requested
                for unit in range(items_for_storage[current_item]):
                    # Select the next cell to store in (the available cell with the highest score)
                    current_cell = available_cells_sorted.pop(0)
                    # Store
                    aisle_storage[current_cell[0]][current_cell[1]][
                        current_cell[2]
                    ] = current_item
                    if not current_item in item_storage_by_location_dict:
                        item_storage_by_location_dict[current_item] = [current_cell]
                    else:
                        item_storage_by_location_dict[current_item].append(current_cell)

                # Make sure we placed all the units for this item
                if items_for_storage_for_monitoring[current_item] < len(
                    item_storage_by_location_dict[current_item]
                ):
                    raise PrivateError(
                        f"Logical Error: Item {current_item} - not all the units stored"
                    )
                elif items_for_storage_for_monitoring[current_item] > len(
                    item_storage_by_location_dict[current_item]
                ):
                    raise PrivateError(
                        f"Logical Error: Item {current_item} - too many units stored"
                    )

        # Make sure the storing is reasonable:
        # The number of available cells and the number of required units to store
        # is the size of the all storage
        num_available_units = len(available_cells_sorted)
        if total_num_units + num_available_units != height * width * depth:
            raise PrivateError("Wrong storing")

        # Update the storage
        self.storage = aisle_storage
        self.storage_dict = item_storage_by_location_dict
        log(simulation_time, f"Completed loading {total_num_units} items into {self}.")
        # TODO: Create logic to output a pickle file with the selected
        # storage decision.
        # TODO: Add GUI showing the storage decision.


class Elevator:
    def __init__(self, vertical_move_time=2, unload_time=3):
        self.vertical_move_time = vertical_move_time
        self.unload_time = unload_time
        self.floor = 0  # Start on the groud floor
        self.carrying = None

    def __repr__(self):
        return "Elevator"


class Shuttle:
    def __init__(self, floor, horizontal_move_time=2, load_time=5, unload_time=5):
        self.floor = floor
        self.horizontal_move_time = horizontal_move_time
        self.load_time = load_time
        self.unload_time = unload_time
        self.position = 0
        self.carrying = None

    def __repr__(self):
        return f"Shuttle {self.floor + 1}"