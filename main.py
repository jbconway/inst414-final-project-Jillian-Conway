import etl.extract as extract
import etl.transform as transform
import etl.load as load
import analysis.evaluate as ananalysis
import vis.visualizations as vis
import pandas as pd
import analysis.model as model
import analysis.evaluate as evaluate

"""
Main script to run the ETL process, analyze bird data, and visualize results.
"""
def main():
    # speciies files to process
    # Each dictionary contains the species name, path to status data, and path to eBird data.
    # The data has been downloaded from the Cornell Lab of Ornithology's datasets.
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
    # for each species, extract, transform, load, analyze and visualize data
    for bird in species_files:
        species = bird["name"]

        # Set paths to extracted files to output the data to
        ebd_extracted_path = f"data/extracted/{species}_ebd_extracted.csv"
        status_extracted_path = f"data/extracted/{species}_status_extracted.csv"
        merge_df_path = f"data/processed/{species}_merged_data.csv"


        # EXTRACT each bird's data
        extract.extract_data(bird["ebd"], ebd_extracted_path)
        print(f"Extracted EBD data for {species} and saved in {ebd_extracted_path}")
        extract.extract_data(bird["status"], status_extracted_path)
        print(f"Extracted Status data for {species} and saved in {status_extracted_path}")

        # TRANSFORM - clean and filter
        ebd_cleaned = transform.clean_ebd_data(ebd_extracted_path)
        print(f"Cleaned EBD data for {species}")
        status_cleaned = transform.clean_status_data(status_extracted_path)
        print(f"Cleaned Status data for {species}")

        # TRANSFORM - Merge status and trends with ebd datasets for each species
        print(f"Merging datasets for {species}")
        merged_df = transform.merge_datasets(status_cleaned, ebd_cleaned)

        # Perform EDA on each of the merged datasets
        print(f"Running EDA for {species}")
        transform.run_eda(merged_df)
        
        # LOAD - Save the merged DataFrame
        print(f"Saving merged data for {species} to {merge_df_path}")
        load.save_processed_data(merged_df, merge_df_path)

        # Train model and evaluate
        print(f"Training model for {species}")
        trained_model, y_test, y_pred = model.train_model(merged_df)
        print(f"Evaluating model for {species}")
        evaluate.evaluate_model(y_test, y_pred, species_name=species)


        # Plot locations on Maryland map
        print(f"Plotting bird locations for {species}")
        vis.plot_bird_locations(merged_df,species)
        print(f"Plotting prediction distribution for {species}")
        vis.plot_regression_results(y_test, y_pred, species)

if __name__ == "__main__":
    main()  