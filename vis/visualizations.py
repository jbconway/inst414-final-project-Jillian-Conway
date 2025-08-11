import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

logger = logging.getLogger(__name__)

def plot_bird_locations(df, species_name):
    """
    Plots bird sightings on a map of Maryland using latitude and longitude from the dataset.
    Only plots valid data points with latitude, longitude, abundance, and population percent.

    Parameters:
        df (DataFrame): Data containing bird sightings and location info.
        species_name (str): Common name of the bird species (used in the title and filename).
    """
    try:
        # Drop rows where any of the required spatial or abundance columns are missing
        df = df.dropna(subset=["latitude", "longitude", "abundance_mean", "total_pop_percent"])
        logger.info(f"Data cleaned for plotting bird locations for {species_name}.")

        # Load US state shapefile and filter for just Maryland
        states = gpd.read_file("data/shapefiles/cb_2022_us_state_20m.shp")
        maryland = states[states['NAME'] == 'Maryland']

        # Convert latitude and longitude into geometric points
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df.longitude, df.latitude), 
            crs="EPSG:4326"  # Set coordinate reference system to standard lat/lon
        )

        # Create a plot with Maryland as the background
        fig, ax = plt.subplots(figsize=(8, 10))
        maryland.plot(ax=ax, color='lightgray')  # Draw Maryland state
        gdf.plot(ax=ax, markersize=10, color='red', alpha=0.6)  # Plot bird sightings
        
        # Add title and axis labels
        plt.title(f"Bird Sightings in Maryland: {species_name}", fontsize=14)
        plt.xlabel("Longitude", fontsize=12)
        plt.ylabel("Latitude", fontsize=12)

        # Save plot to outputs directory
        output_path = f"data/outputs/map_{species_name.lower().replace(' ', '_')}.png"
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Saved bird locations map for {species_name} to {output_path}")

    except Exception as e:
        logger.error(f"Failed to plot bird locations for {species_name}: {e}", exc_info=True)




from sklearn.metrics import confusion_matrix
def plot_confusion_matrix(y_true, y_pred, species_name, class_names=None):
    """
    Plots and saves a confusion matrix heatmap for binary classification results.
    
    Parameters:
        y_true (array-like): True class labels
        y_pred (array-like): Predicted class labels
        species_name (str): Species name for plot title and filename
        class_names (list of str, optional): Names of the classes for axis labels (default ['Low', 'High'])
    """
    try:
        if class_names is None:
            class_names = ['Low', 'High']  # default binary classes

        cm = confusion_matrix(y_true, y_pred, labels=class_names)
        
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_names,
                    yticklabels=class_names)
        
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.title(f'Confusion Matrix for {species_name}')
        plt.tight_layout()

        os.makedirs("data/outputs", exist_ok=True)
        plot_path = f"data/outputs/confusion_matrix_{species_name.lower().replace(' ', '_')}.png"
        plt.savefig(plot_path)
        plt.close()
        
        logger.info(f"Saved confusion matrix plot for {species_name} to {plot_path}")

    except Exception as e:
        logger.error(f"Failed to plot confusion matrix for {species_name}: {e}", exc_info=True)