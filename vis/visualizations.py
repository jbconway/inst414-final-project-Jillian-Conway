## may add more types of visualizations later, like histograms or bar charts
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd

def plot_bird_locations(df, species_name):
    """
    Plots bird sightings on a map of Maryland using latitude and longitude from the dataset.
    Only plots valid data points with latitude, longitude, abundance, and population percent.

    Parameters:
        df (DataFrame): Data containing bird sightings and location info.
        species_name (str): Common name of the bird species (used in the title and filename).
    """
    
    # Drop rows where any of the required spatial or abundance columns are missing
    df = df.dropna(subset=["latitude", "longitude", "abundance_mean", "total_pop_percent"])
    
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
