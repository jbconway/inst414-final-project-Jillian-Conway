import os
import pandas as pd
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_model(y_true, y_pred, species_name="unknown_species"):
    """
    Evaluate regression model performance, print metrics, and save results to CSV.
    
    Parameters:
    - y_true: true target values
    - y_pred: predicted values from the model
    - species_name: optional string to identify the species or dataset
    """
    if y_true is None or y_pred is None:
        print(f"No predictions to evaluate for {species_name}.")
        return

    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"Evaluation results for {species_name}:")
    print(f"  Mean Squared Error (MSE): {mse:.4f}")
    print(f"  Mean Absolute Error (MAE): {mae:.4f}")
    print(f"  R-squared (R2): {r2:.4f}")

    # Prepare dataframe for saving
    results_df = pd.DataFrame({
        "species": [species_name],
        "MSE": [mse],
        "MAE": [mae],
        "R2": [r2],
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })

    # Ensure output folder exists
    output_dir = "data/analyzed"
    os.makedirs(output_dir, exist_ok=True)

    # Create filename safe species name
    safe_species = species_name.lower().replace(" ", "_")

    # Save or append results to CSV file
    output_file = os.path.join(output_dir, f"evaluation_results_{safe_species}.csv")

    if os.path.exists(output_file):
        results_df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        results_df.to_csv(output_file, index=False)

    print(f"Saved evaluation results to {output_file}")
