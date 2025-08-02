def summarize_bird_data(df):
    """Prints basic descriptive stats for bird observations."""
    print("Descriptive Summary:\n")
    print(f"Total records: {len(df)}")
    print("\nSpecies breakdown:")
    print(df["common_name"].value_counts())

    if "season" in df.columns:
        print("\nSeasonal breakdown:")
        print(df["season"].value_counts(dropna=False))

    if "abundance_mean" in df.columns:
        print("\nAbundance stats:")
        print(df["abundance_mean"].describe())
