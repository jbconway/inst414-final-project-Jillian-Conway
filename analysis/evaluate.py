import os
def summarize_bird_data(df, species_name="summary"):
    """Prints and saves basic descriptive stats for bird observations."""

    summary_path = f"data/analyzed/descriptive_summary_{species_name.lower().replace(' ', '_')}.txt"
    os.makedirs("data/analyzed", exist_ok=True)

    with open(summary_path, "w") as f:
        f.write("Descriptive Summary:\n\n")
        f.write(f"Total records: {len(df)}\n\n")

        f.write("Species breakdown:\n")
        f.write(df["common_name"].value_counts().to_string())
        f.write("\n\n")

        if "season" in df.columns:
            f.write("Seasonal breakdown:\n")
            f.write(df["season"].value_counts(dropna=False).to_string())
            f.write("\n\n")

        if "abundance_mean" in df.columns:
            f.write("Abundance stats:\n")
            f.write(df["abundance_mean"].describe().to_string())

    print(f"Saved descriptive summary to {summary_path}")

