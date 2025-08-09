import logging
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

logger = logging.getLogger(__name__)

def train_model(df):
    """
    Train a linear regression model to predict bird abundance_mean.
    """
    try:
        target_column = 'abundance_mean'

        # Select numeric columns only (excluding target)
        feature_columns = df.select_dtypes(include=['number']).columns.tolist()
        if target_column in feature_columns:
            feature_columns.remove(target_column)

        # Drop rows with missing values in target or features
        df = df.dropna(subset=[target_column] + feature_columns)

        y = df[target_column]
        X = df[feature_columns]

        logger.info(f"Target variable sample values for training: {y.head().tolist()}")

        # Split data without stratify because target is continuous
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train linear regression model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        logger.info("Linear regression model trained successfully.")

        # Predict on test data
        y_pred = model.predict(X_test_scaled)

        return model, y_test, y_pred
    
    except Exception as e:
        logger.error(f"Error during model training: {e}", exc_info=True)
        raise
