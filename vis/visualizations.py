import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd

def plot_bird_locations(df, species_name):
    """Plots bird sightings on a map of Maryland."""
    df = df.dropna(subset=["latitude", "longitude", "abundance_mean", "total_pop_percent"])
    
    # Load Maryland shapefile or use built-in geopandas data if simplified
    states = gpd.read_file("data/shapefiles/cb_2022_us_state_20m.shp")
    maryland = states[states['NAME'] == 'Maryland']
    
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

    fig, ax = plt.subplots(figsize=(8, 10))
    maryland.plot(ax=ax, color='lightgray')
    gdf.plot(ax=ax, markersize=10, color='red', alpha=0.6)
    
    plt.title(f"Bird Sightings in Maryland: {species_name}")
    plt.savefig(f"data/outputs/map_{species_name.lower().replace(' ', '_')}.png")
    plt.close()
