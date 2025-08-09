import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def save_processed_data(df: pd.DataFrame, filename: str):
    """
    Save cleaned (after transform.py) DataFrame to data/processed/ folder.
    """
    try:
        df.to_csv(filename, index=False)
        logger.info(f"Saved processed data to: {filename}")
    except Exception as e:
        logger.error(f"Failed to save processed data to {filename}: {e}", exc_info=True)
        raise
