import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

def clean_ebd_data(filepath):
    """Reads and cleans only the EBD data file."""
    df = pd.read_csv(filepath, sep=None, engine='python')
    # debugging output
    # print("ebd df before")
    # print(df.head())
    logger.debug(f"Read EBD data from {filepath}, shape: {df.shape}")

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
    logger.debug(f"EBD data after cleaning, columns: {list(df.columns)}")

    return df


def clean_status_data(filepath):
    """Reads and cleans only the Status and Trends data file."""
    df = pd.read_csv(filepath)
    # debugging output
    # print("status df before")
    # print(df.head())
    logger.debug(f"Read Status data from {filepath}, shape: {df.shape}")

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
    logger.debug(f"Status data after cleaning, columns: {list(df.columns)}")

    return df


def merge_datasets(status_df, ebd_df):
    """
    Merge cleaned EBD and Status & Trends datasets.

    Rules:
    - Normalize codes and filter to Maryland (us-md).
    - If a status row has season == 'year_round' for a species, apply that species-level
      abundance_mean and total_pop_percent to all matching EBD rows for the same species.
    - Otherwise, match observation_date by month/day to seasonal start/end windows (ignore year).
      Matches are attempted per-species when possible.
    - Returns ebd_df with added columns: abundance_mean, total_pop_percent, season
    """
    logger.debug("Starting merge_datasets")

    # --- Defensive pre-checks ---
    for col in ["state_code"]:
        if col not in ebd_df.columns:
            logger.error(f"ebd_df missing expected column: {col}")
            raise KeyError(f"ebd_df missing expected column: {col}")

    # Choose species key for matching (common_name > scientific_name > species_code)
    def choose_species_col(a, b):
        for c in ["common_name", "scientific_name", "species_code", "species"]:
            if c in a.columns and c in b.columns:
                return c
        return None

    species_col = choose_species_col(status_df, ebd_df)
    logger.debug(f"Species column chosen for merge: {species_col}")

    ebd_df = ebd_df.copy()
    status_df = status_df.copy()

    ebd_df["state_code"] = ebd_df["state_code"].fillna("").astype(str).str.lower()
    status_df["region_code"] = status_df.get("region_code", "").fillna("").astype(str).str.lower().str.replace("usa-", "us-")
    status_df["season"] = status_df.get("season", "").fillna("").astype(str).str.lower()

    ebd_df = ebd_df[ebd_df["state_code"] == "us-md"].copy()
    status_df = status_df[status_df["region_code"] == "us-md"].copy()

    ebd_df["observation_date"] = pd.to_datetime(ebd_df.get("observation_date"), errors="coerce")
    status_df["start_date"] = pd.to_datetime(status_df.get("start_date"), errors="coerce")
    status_df["end_date"] = pd.to_datetime(status_df.get("end_date"), errors="coerce")

    if "season" not in status_df.columns:
        status_df["season"] = ""

    year_round = status_df[status_df["season"] == "year_round"].copy()
    seasonal = status_df[status_df["season"] != "year_round"].copy()

    ebd_df["abundance_mean"] = np.nan
    ebd_df["total_pop_percent"] = np.nan
    ebd_df["season"] = "n/a"

    if not year_round.empty:
        if species_col is not None:
            for _, yr in year_round.iterrows():
                sp = yr.get(species_col)
                if pd.isna(sp) or str(sp).strip() == "":
                    continue
                mask = ebd_df[species_col].fillna("").astype(str) == str(sp)
                if mask.any():
                    ebd_df.loc[mask, "abundance_mean"] = yr.get("abundance_mean")
                    ebd_df.loc[mask, "total_pop_percent"] = yr.get("total_pop_percent")
                    ebd_df.loc[mask, "season"] = yr.get("season")
            logger.info("Applied year_round data per species")
        else:
            yr_row = year_round.iloc[0]
            ebd_df["abundance_mean"] = yr_row.get("abundance_mean")
            ebd_df["total_pop_percent"] = yr_row.get("total_pop_percent")
            ebd_df["season"] = yr_row.get("season")
            logger.info("Applied single year_round row to all observations (no species key found).")
            return ebd_df

    if seasonal.empty:
        logger.info("No seasonal rows found in status_df; returning EBD with any year_round assignments (if any).")
        return ebd_df

    def md_in_range(obs_date, start_date, end_date):
        if pd.isna(obs_date) or pd.isna(start_date) or pd.isna(end_date):
            return False
        obs_md = (int(obs_date.month), int(obs_date.day))
        start_md = (int(start_date.month), int(start_date.day))
        end_md = (int(end_date.month), int(end_date.day))
        if start_md <= end_md:
            return start_md <= obs_md <= end_md
        else:
            return obs_md >= start_md or obs_md <= end_md

    def match_season_for_row(row):
        obs_date = row["observation_date"]
        if pd.isna(obs_date):
            return pd.Series({"abundance_mean": np.nan, "total_pop_percent": np.nan, "season": "n/a"})

        if species_col:
            sp_val = row.get(species_col)
            seasonal_subset = seasonal[seasonal[species_col].fillna("").astype(str) == str(sp_val)]
            if seasonal_subset.empty:
                seasonal_subset = seasonal
        else:
            seasonal_subset = seasonal

        for _, srow in seasonal_subset.iterrows():
            sd = srow.get("start_date")
            ed = srow.get("end_date")
            if md_in_range(obs_date, sd, ed):
                return pd.Series({
                    "abundance_mean": srow.get("abundance_mean"),
                    "total_pop_percent": srow.get("total_pop_percent"),
                    "season": srow.get("season") or "n/a"
                })
        return pd.Series({"abundance_mean": np.nan, "total_pop_percent": np.nan, "season": "n/a"})

    needs_match_mask = ebd_df["season"].isin(["n/a", "", None])
    if needs_match_mask.any():
        seasonal_info = ebd_df[needs_match_mask].apply(match_season_for_row, axis=1)
        ebd_df.loc[needs_match_mask, ["abundance_mean", "total_pop_percent", "season"]] = seasonal_info.values
        logger.info("Applied seasonal matching to EBD data")

    return ebd_df


def categorize_abundance_binary(df):
    # Choose a cutoff — e.g., median or domain-specific threshold
    cutoff = df['abundance_mean'].median()
    df['abundance_class'] = df['abundance_mean'].apply(lambda x: 'Low' if x <= cutoff else 'High')
    df = df.dropna(subset=['abundance_class'])
    return df


def run_eda(df):
    """Run exploratory data analysis on the merged DataFrame."""
    # print("Running EDA...")
    logger.info("Running EDA...")
    # Print the number of rows and columns in the dataset
    # print(f"Data shape: {df.shape}")
    logger.info(f"Data shape: {df.shape}")
    # Print a list of all column names in the dataset
    # print(f"Columns: {df.columns.tolist()}")
    logger.info(f"Columns: {df.columns.tolist()}")
    # make a folder to save output to
    os.makedirs("data/analyzed", exist_ok=True)
    # Fill missing values in string (object) columns with "n/a"
    for col in df.columns:
        if df[col].dtype == object:
            df[col].fillna("n/a", inplace=True)

    # If the column "season" exists, show the top 5 most common values
    if "season" in df.columns:
        # print("Top 5 seasons:\n", df["season"].value_counts().head())
        logger.info(f"Top 5 seasons:\n{df['season'].value_counts().head()}")

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
        # print(f"Saved {filename}")
        logger.info(f"Saved histogram plot to {filename}")
