import etl.extract as extract
import etl.transform as transform
import etl.load as load
import analysis.evaluate as ananalysis
import vis.visualizations as vis
import pandas as pd


def main():
    species_files = [
        {
            "name": "cardinal",
            "status": "cornel_bird_data/trends_and_status_ds/norcar_regional_2023.csv",
            "ebd": "cornel_bird_data/ebd_ds/ebd_US-MD_norcar_201001_202401_smp_relJun-2025.txt"
        },
        {
            "name": "osprey",
            "status": "cornel_bird_data/trends_and_status_ds/osprey_regional_2023.csv",
            "ebd": "cornel_bird_data/ebd_ds/ebd_US-MD_osprey_201001_202401_smp_relJun-2025.txt"
        },
        {
            "name": "american_woodcock",
            "status": "cornel_bird_data/trends_and_status_ds/amewoo_regional_2023.csv",
            "ebd": "cornel_bird_data/ebd_ds/ebd_US-MD_amewoo_201001_202401_smp_relJun-2025.txt"
        }
    ]

    for bird in species_files:
        species = bird["name"]

        # Set paths to extracted files
        ebd_extracted_path = f"data/extracted/{species}_ebd_extracted.csv"
        status_extracted_path = f"data/extracted/{species}_status_extracted.csv"
        merge_df_path = f"data/processed/{species}_merged_data.csv"


        # Extract each bird's data
        extract.extract_data(bird["ebd"], ebd_extracted_path)
        print(f"Extracted EBD data for {species} and saved in {ebd_extracted_path}")
        extract.extract_data(bird["status"], status_extracted_path)
        print(f"Extracted Status data for {species} and saved in {status_extracted_path}")

        # Transform - clean and filter
        ebd_cleaned = transform.clean_ebd_data(ebd_extracted_path)
        print(f"Cleaned EBD data for {species}")
        status_cleaned = transform.clean_status_data(status_extracted_path)
        print(f"Cleaned Status data for {species}")

        # Transform - Merge
        merged_df = transform.merge_datasets(status_cleaned, ebd_cleaned)

        # Perform EDA on each of the merged datasets
        transform.run_eda(merged_df)
        
        load.save_processed_data(merged_df, merge_df_path)

        # Run descriptive stats (filtering inside function if needed)
        ananalysis.summarize_bird_data(merged_df)

        # Plot locations on Maryland map
        vis.plot_bird_locations(merged_df,species)


if __name__ == "__main__":
    main()  