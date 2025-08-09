import logging
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def evaluate_model(y_true, y_pred, species_name="unknown"):
    """
    Evaluate the regression model and save evaluation metrics.
    """
    try:
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        logger.info(f"Evaluation for {species_name}: MSE={mse:.3f}, MAE={mae:.3f}, R²={r2:.3f}")

        eval_results = pd.DataFrame([{
            "species": species_name,
            "MSE": mse,
            "MAE": mae,
            "R2": r2,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        os.makedirs("data/analyzed", exist_ok=True)
        eval_path = "data/analyzed/evaluation_results.csv"

        if os.path.exists(eval_path):
            eval_results.to_csv(eval_path, mode='a', header=False, index=False)
        else:
            eval_results.to_csv(eval_path, index=False)

        logger.info(f"Saved evaluation results to {eval_path}")

    except Exception as e:
        logger.error(f"Error during evaluation for {species_name}: {e}", exc_info=True)
