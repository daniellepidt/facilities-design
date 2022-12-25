from logger import log
from globals import create_dir_if_missing
import pandas as pd

def create_retrival_pickle_file(timestamp: float, request_number: int, data: list) -> None:
    """
    Use the request number and data in order to create a
    pickle file containing a list of lists with the results
    by the following format:
    [ item, location, finished_loading_to_elevator, finished_unloading_at_io ]

    All files will be saved under the retrival_results directory
    """
    log(timestamp, f"Attempting to save the retrival results for request #{request_number}...")
    try:
        filename = f"Group_7_retrival_{request_number}.p"
        with open(filename, "wb") as file:
            import pickle
            pickle.dump(data, file)
        log(timestamp, f"Retrival results Pickle file saved @ {filename}.")
    except Exception as e:
        log(timestamp, f"Failed to save retrival results Pickle file.\nError: {e}")


def create_unified_results_csv(timestamp: float, metrics: pd.DataFrame) -> None:
    """
    Create a CSV file based on the results of the simulation.

    The CSV file will be created under the the unified_results directory,
    and will be under the name %Y_%m_%d_%H_%M_%S_results.csv.
    """
    metrics_df = pd.DataFrame(metrics)
    existing_columns = metrics_df.columns.tolist()

    columns = ["height", "depth"] + existing_columns[5:]
    for col in columns:
        metrics_df[f"cumulative_{col}"] = metrics_df.groupby("request_index")[
            col
        ].cumsum()
        metrics_df[f"total_cumulative_{col}"] = metrics_df[col].cumsum()
    all_new_columns = [
        [col, f"cumulative_{col}", f"total_cumulative_{col}"] for col in columns
    ]
    metrics_df.to_csv(f"unified_results/{timestamp}_results.csv", encoding="utf-8")
