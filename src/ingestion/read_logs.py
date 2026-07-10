import pandas as pd


def load_logs(filepath):
    """
    Reads a CSV log file and converts its timestamp column to a proper datetime type.
    Input: filepath (string) - path to the CSV file
    Output: a pandas DataFrame with logs, ready for analysis
    """
    logs = pd.read_csv(filepath)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    return logs