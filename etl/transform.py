import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np

def clean_ebd_data(filepath):
    """Reads and cleans only the EBD data file."""
    df = pd.read_csv(filepath, sep=None, engine='python')
    # debugging output
    # print("ebd df before")
    # print(df.head())

    # Normalize column names (lowercase, replace spaces with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Keep only the specified columns
    columns_to_keep = [
        "scientific_name", 
        "common_name", 
        "observation_count", 
        "observation_date", 
        "state_code", 
        "latitude", 
        "longitude"
    ]

    df = df[[col for col in columns_to_keep if col in df.columns]]
    # debugging output
    # print("ebd df after")
    # print(df.head())
    
    return df


def clean_status_data(filepath):
    """Reads and cleans only the Status and Trends data file."""
    df = pd.read_csv(filepath)
    # debugging output
    # print("status df before")
    # print(df.head())

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Replace missing values with 'n/a' - this may need to change later
    df.fillna("n/a", inplace=True)

    # Keep only the specified columns
    columns_to_keep = [
        "abundance_mean", 
        "total_pop_percent", 
        "region_code", 
        "season", 
        "start_date", 
        "end_date",
    ]

    df = df[[col for col in columns_to_keep if col in df.columns]]
    # debugging output
    # print("status df after")
    # print(df.head())
    
    return df

def merge_datasets(status_df, ebd_df):
    """
    Merge cleaned EBD and Status & Trends datasets based on:
    - Matching state_code (EBD) and region_code (Status) - on us-md
    - If Status row is 'year_round', apply to all
    - Otherwise, match observation_date to the one that fits in [start_date, end_date] to attach appropriate row
        - this will need to change because not all dates line up
    - end should be a dataframe with the same columns as ebd_df, but with abundance_mean, season, and total_pop_percent added from status_df
    """
    # Normalize strings
    ebd_df["state_code"] = ebd_df["state_code"].str.lower()
    status_df["region_code"] = status_df["region_code"].str.lower().str.replace("usa-", "us-")
    status_df["season"] = status_df["season"].str.lower()

    # Filter to MD only
    ebd_df = ebd_df[ebd_df["state_code"] == "us-md"]
    status_df = status_df[status_df["region_code"] == "us-md"]

    # Convert dates
    ebd_df["observation_date"] = pd.to_datetime(ebd_df["observation_date"], errors="coerce")
    status_df.loc[:, "start_date"] = pd.to_datetime(status_df["start_date"], errors="coerce")
    status_df.loc[:, "end_date"] = pd.to_datetime(status_df["end_date"], errors="coerce")

    # Separate year_round and seasonal data
    year_round = status_df[status_df["season"] == "year_round"]
    seasonal = status_df[status_df["season"] != "year_round"]

    # Merge: First, handle year_round (if present)
    if not year_round.empty:
        # Grab the one year_round row (assuming there's only one)
        yr_row = year_round.iloc[0][["abundance_mean", "total_pop_percent", "season"]]
        # Add to all EBD rows
        for col in yr_row.index:
            ebd_df[col] = yr_row[col]
        print("handled year_round data")
        return ebd_df

    # If not year_round, match to seasonal windows
    def match_season(row):
        obs_date = row["observation_date"]
        matched = seasonal[
            (seasonal["start_date"] <= obs_date) &
            (seasonal["end_date"] >= obs_date)
        ]
        if not matched.empty:
            best = matched.iloc[0]
            return pd.Series({
                "abundance_mean": best["abundance_mean"],
                "total_pop_percent": best["total_pop_percent"],
                "season": best["season"]
            })
        else:
        # catch all - need to change logic 
            return pd.Series({
                "abundance_mean": np.nan,
                "total_pop_percent": np.nan,
                "season": "n/a"
            })

    # Apply seasonal matching row-by-row
    seasonal_info = ebd_df.apply(match_season, axis=1)

    # Combine original EBD with matched seasonal info
    merged_df = pd.concat([ebd_df, seasonal_info], axis=1)

    return merged_df



def run_eda(df):
    """Run exploratory data analysis on the merged DataFrame."""
    print("Running EDA...")
    # Print the number of rows and columns in the dataset
    print(f"Data shape: {df.shape}")
    # Print a list of all column names in the dataset
    print(f"Columns: {df.columns.tolist()}")
    # make a folder to save output to
    os.makedirs("data/analyzed", exist_ok=True)
    # Fill missing values in string (object) columns with "n/a"
    for col in df.columns:
        if df[col].dtype == object:
            df[col].fillna("n/a", inplace=True)

    # If the column "season" exists, show the top 5 most common values
    if "season" in df.columns:
        print("Top 5 seasons:\n", df["season"].value_counts().head())

    # If the column "abundance_mean" exists, show basic stats
    if "abundance_mean" in df.columns:
        plt.figure(figsize=(8, 5))
        # Create a histogram with a smooth curve showing the distribution
        sns.histplot(df["abundance_mean"].dropna(), bins=30, kde=True)
        plt.title("Distribution of Abundance Mean")
        plt.xlabel("Abundance Mean")
        plt.ylabel("Frequency")
        plt.tight_layout()

        # Get species name for file naming
        species_name = "unknown_species"
        if "common_name" in df.columns:
            species_name = df["common_name"].iloc[0]
        elif "species" in df.columns:
            species_name = df["species"].iloc[0]

        # Sanitize species name: lowercase, replace spaces with _
        species_name = re.sub(r'\s+', '_', species_name.strip().lower())

        # Save the histogram
        filename = f"data/analyzed/abundance_mean_hist_{species_name}.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved {filename}")