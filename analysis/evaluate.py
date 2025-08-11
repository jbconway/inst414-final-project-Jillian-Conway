import logging
import pandas as pd
from datetime import datetime
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

logger = logging.getLogger(__name__)

def evaluate_classification_model(y_true, y_pred, species_name="unknown"):
    """
    Evaluate classification model, save metrics to CSV, and log results.
    """
    try:
        acc = accuracy_score(y_true, y_pred)
        cls_report = classification_report(y_true, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_true, y_pred)

        logger.info(f"Classification Accuracy for {species_name}: {acc:.3f}")
        logger.info(f"Classification Report for {species_name}:\n{classification_report(y_true, y_pred)}")
        logger.info(f"Confusion Matrix for {species_name}:\n{conf_matrix}")

        # Save summary metrics to CSV
        eval_results = pd.DataFrame([{
            "species": species_name,
            "accuracy": acc,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        os.makedirs("data/analyzed", exist_ok=True)
        eval_path = "data/analyzed/classification_evaluation_results.csv"

        if os.path.exists(eval_path):
            eval_results.to_csv(eval_path, mode='a', header=False, index=False)
        else:
            eval_results.to_csv(eval_path, index=False)

        # Optionally, save confusion matrix to a CSV too
        conf_df = pd.DataFrame(conf_matrix)
        conf_path = f"data/analyzed/confusion_matrix_{species_name.lower().replace(' ', '_')}.csv"
        conf_df.to_csv(conf_path, index=True)

        logger.info(f"Saved classification evaluation results for {species_name}.")

    except Exception as e:
        logger.error(f"Error during classification evaluation for {species_name}: {e}", exc_info=True)
        raise
