import pandas as pd


def create_results_csv(timestamp, metrics):
    """
    Create a CSV file based on the results of the simulation.

    The CSV file will be created under the the results directory,
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
    metrics_df.to_csv(f"results/{timestamp}_results.csv", encoding="utf-8")
