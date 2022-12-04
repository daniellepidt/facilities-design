from enum import Enum
import heapq as hq
import numpy as np
import uuid
from collections.abc import Sequence

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
    def __init__(
        self, height=8, width=2, depth=16, elevator_settings=None, shuttle_settings=None
    ):
        self.height = height
        self.width = width
        self.depth = depth
        # Create an array of 'height' floors, with 'width' number of cells per 'depth'.
        self.storage = np.zeros((height, width, depth))
        # Only pass in elevation settings if any were added
        self.elevator = Elevator(**elevator_settings)
        self.shuttles = [Shuttle(floor, **shuttle_settings) for floor in range(height)]

    def __repr__(self):
        return "Aisle"

    def load_items(self, items: list[list[int, int]]):
        """
        Load a list of items by the format of
        [item, number available] in to the Aisle's storage
        property, using a defined heuristic.
        """
        # TODO: Create loading logic
        pass


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
