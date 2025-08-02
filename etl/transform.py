import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np

def clean_ebd_data(filepath):
    """Reads and cleans the EBD data file."""
    df = pd.read_csv(filepath, sep=None, engine='python')
    print("ebd df before")
    print(df.head())

    # Normalize column names (lowercase, replace spaces with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")


    # Keep only the specified columns (normalize names to match these)
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
    print("ebd df after")
    print(df.head())
    
    return df


def clean_status_data(filepath):
    """Reads and cleans the Status and Trends data file."""
    df = pd.read_csv(filepath)
    print("status df before")
    print(df.head())

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Replace missing values with 'n/a'
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
    print("status df after")
    print(df.head())
    
    return df

# def merge_datasets(status_df, ebd_df):
#     """
#     Merge cleaned EBD and Status & Trends datasets based on:
#     - Matching region_code (Status) and state_code (EBD)
#     - If Status row is 'year_round', apply to all
#     - Otherwise, match observation_date to [start_date, end_date] (even if it crosses year)
#     """

#     # Normalize strings
#     ebd_df["state_code"] = ebd_df["state_code"].str.lower()
#     status_df["region_code"] = status_df["region_code"].str.lower()
#     status_df["season"] = status_df["season"].str.lower()
#     print("normalized strings")

#     # Filter to MD only
#     ebd_df = ebd_df[ebd_df["state_code"] == "us-md"]
#     status_df = status_df[status_df["region_code"] == "us-md"]
#     print("filtered to MD only")

#     # Convert dates
#     ebd_df["observation_date"] = pd.to_datetime(ebd_df["observation_date"], errors="coerce")
#     status_df["start_date"] = pd.to_datetime(status_df["start_date"], errors="coerce")
#     status_df["end_date"] = pd.to_datetime(status_df["end_date"], errors="coerce")
#     print("converted dates")

#     # Separate year_round and seasonal data
#     year_round = status_df[status_df["season"] == "year_round"]
#     seasonal = status_df[status_df["season"] != "year_round"]
#     print("separated year_round and seasonal data")

#     # Merge: First, handle year_round (if present)
#     if not year_round.empty:
#         yr_row = year_round.iloc[0][["abundance_mean", "total_pop_percent", "season"]]
#         for col in yr_row.index:
#             ebd_df[col] = yr_row[col]
#         print("handled year_round data")
#         return ebd_df

#     print("no year_round data; matching seasonal windows")

#     # Default values for no match
#     default_vals = pd.Series({
#         "abundance_mean": None,
#         "total_pop_percent": None,
#         "season": "n/a"
#     })

#     # Helper function for seasonal matching
#     def match_season(row):
#         obs_date = row["observation_date"]

#         for _, season_row in seasonal.iterrows():
#             start = season_row["start_date"]
#             end = season_row["end_date"]

#             if pd.isnull(start) or pd.isnull(end) or pd.isnull(obs_date):
#                 continue

#             # Handle season that wraps into next year
#             if end < start:
#                 in_range = (obs_date >= start) or (obs_date <= end)
#             else:
#                 in_range = (obs_date >= start) and (obs_date <= end)

#             if in_range:
#                 return pd.Series({
#                     "abundance_mean": season_row["abundance_mean"],
#                     "total_pop_percent": season_row["total_pop_percent"],
#                     "season": season_row["season"]
#                 })

#         return default_vals

#     # Apply seasonal matching
#     seasonal_info = ebd_df.apply(match_season, axis=1)
#     print("applied seasonal matching")

#     # Combine EBD with matched seasonal info
#     merged_df = pd.concat([ebd_df, seasonal_info], axis=1)
#     print("combined EBD with seasonal info")

#     return merged_df

def merge_datasets(status_df, ebd_df):
    """
    Merge cleaned EBD and Status & Trends datasets based on:
    - Matching region_code (EBD) and state_code (Status)
    - If Status row is 'year_round', apply to all
    - Otherwise, match observation_date to [start_date, end_date] to attach appropriate row
    """
    # Normalize strings
    ebd_df["state_code"] = ebd_df["state_code"].str.lower()
    status_df["region_code"] = status_df["region_code"].str.lower().str.replace("usa-", "us-")
    status_df["season"] = status_df["season"].str.lower()
    print("normalized strings")

    # Filter to MD only
    ebd_df = ebd_df[ebd_df["state_code"] == "us-md"]
    status_df = status_df[status_df["region_code"] == "us-md"]
    print("filtered to MD only")

    # Convert dates
    ebd_df["observation_date"] = pd.to_datetime(ebd_df["observation_date"], errors="coerce")
    status_df.loc[:, "start_date"] = pd.to_datetime(status_df["start_date"], errors="coerce")
    status_df.loc[:, "end_date"] = pd.to_datetime(status_df["end_date"], errors="coerce")


    # Separate year_round and seasonal data
    year_round = status_df[status_df["season"] == "year_round"]
    seasonal = status_df[status_df["season"] != "year_round"]
    print("separated year_round and seasonal data")

    # Merge: First, handle year_round (if present)
    if not year_round.empty:
        # Grab the one year_round row (assuming there's only one)
        yr_row = year_round.iloc[0][["abundance_mean", "total_pop_percent", "season"]]
        # Add to all EBD rows
        for col in yr_row.index:
            ebd_df[col] = yr_row[col]
        print("handled year_round data")
        return ebd_df

    # If not year_round, we need to match seasonal windows
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
            return pd.Series({
                "abundance_mean": np.nan,
                "total_pop_percent": np.nan,
                "season": "n/a"
            })

    # Apply seasonal matching row-by-row
    seasonal_info = ebd_df.apply(match_season, axis=1)
    print("applied seasonal matching")

    # Combine original EBD with matched seasonal info
    merged_df = pd.concat([ebd_df, seasonal_info], axis=1)
    print("combined EBD with seasonal info")

    return merged_df



import os
import matplotlib.pyplot as plt
import seaborn as sns

# def run_eda(df):
#     """Perform basic EDA and generate plots."""
#     print("Running EDA...")

#     # Print basic info
#     print(f"Data shape: {df.shape}")
#     print(f"Columns: {df.columns.tolist()}")

#     # Ensure output directory exists
#     os.makedirs("data/analyzed", exist_ok=True)

#     # Fill NA only in string columns to avoid dtype warnings
#     for col in df.columns:
#         if df[col].dtype == object:
#             df[col].fillna("n/a", inplace=True)

#     # Example 1: Observation counts by season
#     if "season" in df.columns:
#         print("Top 5 seasons:\n", df["season"].value_counts().head())

#     # Example 2: Histogram of abundance_mean
#     if "abundance_mean" in df.columns:
#         plt.figure(figsize=(8, 5))
#         sns.histplot(df["abundance_mean"].dropna(), bins=30, kde=True)
#         plt.title("Distribution of Abundance Mean")
#         plt.xlabel("Abundance Mean")
#         plt.ylabel("Frequency")
#         plt.tight_layout()
#         plt.savefig(f"data/analyzed/abundance_mean_hist_{df}.png")
#         plt.close()
#         print("Saved abundance_mean_hist.png")

def run_eda(df):
    print("Running EDA...")

    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")

    os.makedirs("data/analyzed", exist_ok=True)

    for col in df.columns:
        if df[col].dtype == object:
            df[col].fillna("n/a", inplace=True)

    if "season" in df.columns:
        print("Top 5 seasons:\n", df["season"].value_counts().head())

    if "abundance_mean" in df.columns:
        plt.figure(figsize=(8, 5))
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

        filename = f"data/analyzed/abundance_mean_hist_{species_name}.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved {filename}")