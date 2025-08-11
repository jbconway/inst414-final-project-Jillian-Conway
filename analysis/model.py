
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


def train_classification_model(df, target_col='abundance_class'):
    """
    Train a Random Forest classification model to predict abundance_class.
    Properly handles numeric and categorical features with preprocessing,
    and avoids data leakage.
    Assumes df is preprocessed and target_col exists.
    """
    try:
        # Columns to exclude from features to avoid leakage
        leak_cols = [target_col, 'abundance_mean']  # Add others if needed

        # Select feature columns excluding target and leakage columns
        feature_cols = [col for col in df.columns if col not in leak_cols]

        # Drop rows with missing target or feature values
        df = df.dropna(subset=[target_col] + feature_cols)

        X = df[feature_cols]
        y = df[target_col]

        logger.info(f"Classes: {y.unique().tolist()}")

        # Split data (stratify by target)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)

        # Separate numeric and categorical columns
        numeric_features = X.select_dtypes(include=['number']).columns.tolist()
        categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

        # Create preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

        # Full pipeline: preprocessing + classifier
        clf = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        # Train model
        clf.fit(X_train, y_train)
        logger.info("Random Forest classification model trained successfully.")

        # Predict on test set
        y_pred = clf.predict(X_test)

        return clf, y_test, y_pred

    except Exception as e:
        logger.error(f"Error during classification model training: {e}", exc_info=True)
        raise