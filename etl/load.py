import os
import pandas as pd

def save_processed_data(df: pd.DataFrame, filename: str):
    """
    Save cleaned (after transform.py) DataFrame to data/processed/ folder.
    """
    df.to_csv(f"{filename}", index=False)
    print(f"Saved processed data to: {filename}")
