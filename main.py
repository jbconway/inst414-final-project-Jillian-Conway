import etl.extract as extract
import etl.transform as transform
import etl.load as load
import analysis.evaluate as ananalysis
import vis.visualizations as vis
import pandas as pd
import analysis.model as model
import analysis.evaluate as evaluate
import logging

"""
Main script to run the ETL process, analyze bird data, and visualize results.
"""
def main():
    # Setup logging
    logging.basicConfig(
        filename='etl_pipeline.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'  # overwrite log file each run; change to 'a' to append
    )
    logger = logging.getLogger()
    
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
    
    logger.info("Pipeline started.")
    
    for bird in species_files:
        species = bird["name"]
        logger.info(f"Processing species: {species}")

        ebd_extracted_path = f"data/extracted/{species}_ebd_extracted.csv"
        status_extracted_path = f"data/extracted/{species}_status_extracted.csv"
        merge_df_path = f"data/processed/{species}_merged_data.csv"

        try:
            extract.extract_data(bird["ebd"], ebd_extracted_path)
            logger.info(f"Extracted EBD data for {species} and saved to {ebd_extracted_path}")
        except Exception as e:
            logger.error(f"Error extracting EBD data for {species}: {e}", exc_info=True)
            continue  # Skip this species and continue with the next

        try:
            extract.extract_data(bird["status"], status_extracted_path)
            logger.info(f"Extracted Status data for {species} and saved to {status_extracted_path}")
        except Exception as e:
            logger.error(f"Error extracting Status data for {species}: {e}", exc_info=True)
            continue

        try:
            ebd_cleaned = transform.clean_ebd_data(ebd_extracted_path)
            logger.info(f"Cleaned EBD data for {species}")
        except Exception as e:
            logger.error(f"Error cleaning EBD data for {species}: {e}", exc_info=True)
            continue

        try:
            status_cleaned = transform.clean_status_data(status_extracted_path)
            logger.info(f"Cleaned Status data for {species}")
        except Exception as e:
            logger.error(f"Error cleaning Status data for {species}: {e}", exc_info=True)
            continue

        try:
            logger.info(f"Merging datasets for {species}")
            merged_df = transform.merge_datasets(status_cleaned, ebd_cleaned)
        except Exception as e:
            logger.error(f"Error merging datasets for {species}: {e}", exc_info=True)
            continue
        try:
            merged_df = transform.categorize_abundance_binary(merged_df)
            logger.info(f"Categorized abundance for {species}")
        except Exception as e:
            logger.error(f"Error categorizing abundance for {species}: {e}", exc_info=True)
            continue

        try:
            logger.info(f"Running EDA for {species}")
            transform.run_eda(merged_df)
        except Exception as e:
            logger.error(f"Error during EDA for {species}: {e}", exc_info=True)
            # Continue because EDA is optional for pipeline success

        try:
            logger.info(f"Saving merged data for {species} to {merge_df_path}")
            load.save_processed_data(merged_df, merge_df_path)
        except Exception as e:
            logger.error(f"Error saving merged data for {species}: {e}", exc_info=True)
            continue

        try:
            logger.info(f"Training model for {species}")
            # trained_model, y_test, y_pred = model.train_model(merged_df)
            trained_model, y_test, y_pred = model.train_classification_model(merged_df, target_col='abundance_class')
        except Exception as e:
            logger.error(f"Error training model for {species}: {e}", exc_info=True)
            continue

        try:
            logger.info(f"Evaluating model for {species}")
            # evaluate.evaluate_model(y_test, y_pred, species_name=species)
            evaluate.evaluate_classification_model(y_test, y_pred, species_name=species)

        except Exception as e:
            logger.error(f"Error evaluating model for {species}: {e}", exc_info=True)

        try:
            logger.info(f"Plotting bird locations for {species}")
            vis.plot_bird_locations(merged_df, species)
        except Exception as e:
            logger.error(f"Error plotting bird locations for {species}: {e}", exc_info=True)

        try:
            logger.info(f"Creating confusion matrix for {species}")
            vis.plot_confusion_matrix(y_test, y_pred, species, class_names=['Low', 'Medium', 'High'])
            # vis.plot_regression_results(y_test, y_pred, species)
        except Exception as e:
            logger.error(f"Error creating confusion matrix for {species}: {e}", exc_info=True)

    logger.info("Pipeline finished.")


if __name__ == "__main__":
    main()  