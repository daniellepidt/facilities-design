""""
This file contains all the global variables
which don't change during thr run process.
"""

import os

SIMULATION_START_TIME = 0.0  # Measured in simulation time seconds.
ITEMS_IN_FETCH = 40  # Number of items in a "truck".
P = []  # Events heap


class PrivateError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
