import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_data(file_path: str, output_filename: str):
    """
    Reads a CSV or TXT file and writes it as a CSV to 'data/extracted/' folder.
    Uses the delimiter based on file extension: 
    - .csv assumes comma-separated
    - .txt assumes tab-separated
    """
    try:
        # Determine delimiter by file extension
        if file_path.endswith('.txt'):
            sep = '\t'
        elif file_path.endswith('.csv'):
            sep = ','
        else:
            raise ValueError("Unsupported file type. Only .csv and .txt files are supported.")
        
        logger.info(f"Reading: {file_path} with sep='{sep}'")
        df = pd.read_csv(file_path, low_memory=False, sep=sep)  # reads the file into a DataFrame
        df.to_csv(output_filename, index=False)  # writes the DataFrame to a CSV file
        logger.info(f"Saved extracted data to {output_filename}")
        return df
    
    except Exception as e:
        logger.error(f"Failed to extract data from {file_path}: {e}", exc_info=True)
        raise
