"""
LSTM model for stock price prediction
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, List
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks
from sklearn.preprocessing import MinMaxScaler
import joblib
from pathlib import Path

from backend.utils.logger import logger


class LSTMPredictor:
    """LSTM model for price prediction"""
    
    def __init__(self,
                 lookback_days: int = 60,
                 lstm_units: List[int] = [128, 64, 32],
                 dropout: float = 0.2,
                 learning_rate: float = 0.001):
        """
        Initialize LSTM predictor
        
        Args:
            lookback_days: Number of historical days to use
            lstm_units: List of LSTM layer units
            dropout: Dropout rate
            learning_rate: Learning rate for Adam optimizer
        """
        self.lookback_days = lookback_days
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        
        self.model_dir = Path("models/saved_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_data(self,
                     data: pd.DataFrame,
                     target_col: str = 'Close',
                     feature_cols: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM training
        
        Args:
            data: DataFrame with price and features
            target_col: Target column name
            feature_cols: List of feature column names (optional)
        
        Returns:
            Tuple of (X, y) arrays
        """
        # Use only target if no features specified
        if feature_cols is None:
            feature_cols = [target_col]
        
        # Extract target
        target_data = data[target_col].values.reshape(-1, 1)
        self.scaler.fit(target_data)
        scaled_target = self.scaler.transform(target_data)
        
        # Extract and scale features
        feature_data = data[feature_cols].values
        self.feature_scaler.fit(feature_data)
        scaled_features = self.feature_scaler.transform(feature_data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.lookback_days, len(scaled_features)):
            X.append(scaled_features[i-self.lookback_days:i])
            y.append(scaled_target[i])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Prepared data: X shape {X.shape}, y shape {y.shape}")
        
        return X, y
    
    def build_model(self, n_features: int):
        """
        Build LSTM model architecture
        
        Args:
            n_features: Number of input features
        """
        model = keras.Sequential()
        
        # First LSTM layer
        model.add(layers.LSTM(
            units=self.lstm_units[0],
            return_sequences=True if len(self.lstm_units) > 1 else False,
            input_shape=(self.lookback_days, n_features)
        ))
        model.add(layers.Dropout(self.dropout))
        
        # Additional LSTM layers
        for i, units in enumerate(self.lstm_units[1:], 1):
            return_seq = i < len(self.lstm_units) - 1
            model.add(layers.LSTM(units=units, return_sequences=return_seq))
            model.add(layers.Dropout(self.dropout))
        
        # Output layer
        model.add(layers.Dense(1))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        self.model = model
        
        logger.info(f"Built LSTM model with {self.model.count_params()} parameters")
        
        return model
    
    def train(self,
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None,
              epochs: int = 100,
              batch_size: int = 32,
              verbose: int = 1):
        """
        Train LSTM model
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            epochs: Number of training epochs
            batch_size: Batch size
            verbose: Verbosity level
        
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model(n_features=X_train.shape[2])
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        )
        
        model_checkpoint = callbacks.ModelCheckpoint(
            filepath=str(self.model_dir / 'lstm_checkpoint.h5'),
            monitor='val_loss' if X_val is not None else 'loss',
            save_best_only=True
        )
        
        callback_list = [early_stop, reduce_lr, model_checkpoint]
        
        # Train
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=verbose
        )
        
        logger.info(f"Training complete. Final loss: {history.history['loss'][-1]:.6f}")
        
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features
        
        Returns:
            Predictions (unscaled)
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Predict (scaled)
        predictions_scaled = self.model.predict(X, verbose=0)
        
        # Inverse transform to original scale
        predictions = self.scaler.inverse_transform(predictions_scaled)
        
        return predictions
    
    def predict_next(self, recent_data: pd.DataFrame,
                    feature_cols: Optional[List[str]] = None) -> float:
        """
        Predict next day's price
        
        Args:
            recent_data: Recent data (at least lookback_days rows)
            feature_cols: Feature columns to use
        
        Returns:
            Predicted price
        """
        if len(recent_data) < self.lookback_days:
            raise ValueError(f"Need at least {self.lookback_days} days of data")
        
        # Take last lookback_days
        data = recent_data.tail(self.lookback_days)
        
        # Prepare features
        if feature_cols is None:
            feature_cols = [data.columns[0]]
        
        features = data[feature_cols].values
        scaled_features = self.feature_scaler.transform(features)
        
        # Reshape for model
        X = scaled_features.reshape(1, self.lookback_days, len(feature_cols))
        
        # Predict
        prediction = self.predict(X)[0, 0]
        
        return prediction
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test targets
        
        Returns:
            Dictionary with metrics
        """
        # Get predictions
        predictions_scaled = self.model.predict(X_test, verbose=0)
        predictions = self.scaler.inverse_transform(predictions_scaled)
        y_true = self.scaler.inverse_transform(y_test)
        
        # Calculate metrics
        mse = np.mean((predictions - y_true) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - y_true))
        mape = np.mean(np.abs((y_true - predictions) / y_true)) * 100
        
        # Directional accuracy
        y_true_direction = np.diff(y_true.flatten()) > 0
        pred_direction = np.diff(predictions.flatten()) > 0
        directional_accuracy = np.mean(y_true_direction == pred_direction)
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'directional_accuracy': directional_accuracy
        }
        
        logger.info(f"Evaluation metrics: RMSE={rmse:.4f}, MAE={mae:.4f}, "
                   f"MAPE={mape:.2f}%, Dir_Acc={directional_accuracy:.2%}")
        
        return metrics
    
    def save(self, name: str = "lstm_model"):
        """
        Save model and scalers
        
        Args:
            name: Model name
        """
        # Save model
        model_path = self.model_dir / f"{name}.h5"
        self.model.save(model_path)
        
        # Save scalers
        scaler_path = self.model_dir / f"{name}_scaler.pkl"
        feature_scaler_path = self.model_dir / f"{name}_feature_scaler.pkl"
        
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.feature_scaler, feature_scaler_path)
        
        logger.info(f"Model saved to {model_path}")
    
    def load(self, name: str = "lstm_model"):
        """
        Load model and scalers
        
        Args:
            name: Model name
        """
        # Load model
        model_path = self.model_dir / f"{name}.h5"
        self.model = keras.models.load_model(model_path)
        
        # Load scalers
        scaler_path = self.model_dir / f"{name}_scaler.pkl"
        feature_scaler_path = self.model_dir / f"{name}_feature_scaler.pkl"
        
        self.scaler = joblib.load(scaler_path)
        self.feature_scaler = joblib.load(feature_scaler_path)
        
        logger.info(f"Model loaded from {model_path}")


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download sample data
    data = yf.download('ICLN', start='2019-01-01', end='2024-12-31')
    
    # Initialize predictor
    predictor = LSTMPredictor(lookback_days=60, lstm_units=[128, 64, 32])
    
    # Prepare data
    X, y = predictor.prepare_data(data, target_col='Close')
    
    # Split train/test
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Train
    history = predictor.train(X_train, y_train, X_test, y_test, epochs=50)
    
    # Evaluate
    metrics = predictor.evaluate(X_test, y_test)
    print(metrics)
    
    # Save
    predictor.save()
