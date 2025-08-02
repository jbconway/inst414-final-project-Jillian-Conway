import os
import pandas as pd

def extract_data(file_path: str, output_filename: str):
    """
    Reads a CSV or TXT file and writes it as a CSV to 'data/extracted/' folder.
    Uses the delimiter based on file extension: 
    - .csv assumes comma-separated
    - .txt assumes tab-separated
    """
    # Determine delimiter by file extension
    if file_path.endswith('.txt'):
        sep = '\t'
    elif file_path.endswith('.csv'):
        sep = ','
    else:
        # fallback or raise error if unknown
        raise ValueError("Unsupported file type. Only .csv and .txt files are supported.")
    
    print(f"Reading: {file_path} with sep='{sep}'")
    df = pd.read_csv(file_path, low_memory=False, sep=sep)

    output_path = os.path.join(output_filename)
    df.to_csv(output_path, index=False)
    print(f"Extracted and saved to {output_path}")
    return df
