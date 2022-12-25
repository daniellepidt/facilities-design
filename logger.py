"""
This file contains the functions which
generate the logs for the simulation.
"""
import logging
from datetime import datetime, timedelta
from globals import SIMULATION_START_TIME
from os import mkdir


def parser_simulation_time(seconds_from_start: int) -> str:
    return str(timedelta(seconds=seconds_from_start))


def log(seconds_from_start: int, log_data=""):
    """
    Log an event to the log file and print it to the console
    at the same time with the following format:

    HH:MM:SS {log_data}
    """
    simulation_time = parser_simulation_time(seconds_from_start)
    log_string = f"{simulation_time}\t{log_data}"
    logging.info(f"\t{log_string}")
    print(log_string)


def create_log_file(creation_time=SIMULATION_START_TIME) -> str:
    """
    Create a log file which will be used for logging all actions performed in this simulation.

    The function returns the timestamp under which the log file was saved,
    so it can be reused with the results CSV file.

    The log file will be created under the the logs directory,
    and will be under the name %Y_%m_%d_%H_%M_%S_log.log.
    """
    try:
        mkdir("logs")
    except OSError:
        pass
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"logs/{timestamp}_log.log"
    logging.basicConfig(filename=filename, encoding="utf-8", level=logging.DEBUG)
    log(creation_time, f"Created log file successfully with filename: {filename}")
    return timestamp
