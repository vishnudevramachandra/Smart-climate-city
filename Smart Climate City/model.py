"""
Traffic Prediction Model for Project EcoFlow
Uses Facebook Prophet for time series forecasting of traffic patterns
"""

import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from prophet import Prophet
from config import MODEL_PATH, MODEL_TR1_PATH, MODEL_TR2_PATH, TRAINING_DATA_MONTHS


class TrafficPredictor:
    """
    Traffic prediction model using Prophet for time series forecasting.
    Predicts future traffic volume based on historical patterns.
    """

    def __init__(self):
        self.model = None
        self.model_tr1 = None  # Separate model for direction 1
        self.model_tr2 = None  # Separate model for direction 2
        self.trained = False
        self.device_imei = None
        self.use_directions = False  # Whether to use direction-specific models

    def train(self, traffic_data_path, train_directions=True):
        """
        Train the Prophet model on historical traffic data.
        Can train separate models for each direction (TR1 and TR2).

        Parameters:
        - traffic_data_path: Path to CSV file with traffic data (from data_extraction.py)
        - train_directions: If True, train separate models for TR1 and TR2 in addition to total

        Returns:
        - True if training successful, False otherwise
        """
        try:
            print("\n" + "=" * 70)
            print("🧠 TRAINING TRAFFIC PREDICTION MODEL")
            print("=" * 70)

            # Load data
            print(f"\n📂 Loading data from: {traffic_data_path}")
            df = pd.read_csv(traffic_data_path)
            print(f"✅ Loaded {len(df):,} records")

            # Prepare data for Prophet
            # Prophet requires columns named 'ds' (datetime) and 'y' (target value)
            # We'll aggregate to 15-minute intervals for better short-term predictions
            print("\n🔧 Preparing data for Prophet (15-minute intervals)...")

            # Convert timestamp and aggregate to 15-minute intervals
            df['ds'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
            df['ds_15min'] = df['ds'].dt.floor('15T')  # Round down to nearest 15 minutes

            # Aggregate to 15-minute intervals (sum traffic per 15-minute period)
            df_15min = df.groupby('ds_15min').agg({
                'total_traffic': 'sum',
                'tr1': 'sum',
                'tr2': 'sum'
            }).reset_index()

            # Prepare total traffic model (15-minute intervals)
            prophet_df_total = pd.DataFrame({
                'ds': df_15min['ds_15min'],
                'y': df_15min['total_traffic']  # Total traffic per 15-minute period
            }).dropna()

            print(f"✅ Prepared {len(prophet_df_total):,} training samples for total traffic (15-min intervals)")
            print(f"   Date range: {prophet_df_total['ds'].min()} to {prophet_df_total['ds'].max()}")
            print(f"   Average total traffic per 15min: {prophet_df_total['y'].mean():.1f} vehicles")
            print(f"   (Original: {len(df):,} 1-minute samples aggregated to {len(prophet_df_total):,} 15-minute intervals)")

            # Initialize and train total traffic Prophet model
            print("\n🔮 Training Total Traffic Model...")
            print("   - Daily seasonality: ON")
            print("   - Weekly seasonality: ON")
            print("   - Yearly seasonality: AUTO")

            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality='auto',
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05
            )

            # Fit the total model
            self.model.fit(prophet_df_total)
            self.trained = True
            self.device_imei = df['imei'].iloc[0] if 'imei' in df.columns else 'unknown'

            print("✅ Total traffic model training complete!")

            # Train direction-specific models if requested
            if train_directions and 'tr1' in df.columns and 'tr2' in df.columns:
                print("\n" + "=" * 70)
                print("🧠 TRAINING DIRECTION-SPECIFIC MODELS")
                print("=" * 70)

                # Prepare TR1 data (15-minute intervals)
                prophet_df_tr1 = pd.DataFrame({
                    'ds': df_15min['ds_15min'],
                    'y': df_15min['tr1']  # TR1 traffic per 15-minute period
                }).dropna()

                # Prepare TR2 data (15-minute intervals)
                prophet_df_tr2 = pd.DataFrame({
                    'ds': df_15min['ds_15min'],
                    'y': df_15min['tr2']  # TR2 traffic per 15-minute period
                }).dropna()

                print(f"\n📊 Direction Statistics (15-minute intervals):")
                print(f"   TR1: {len(prophet_df_tr1):,} samples, avg: {prophet_df_tr1['y'].mean():.1f} vehicles/15min")
                print(f"   TR2: {len(prophet_df_tr2):,} samples, avg: {prophet_df_tr2['y'].mean():.1f} vehicles/15min")

                # Train TR1 model
                print("\n🔮 Training TR1 (Direction 1) Model...")
                self.model_tr1 = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality='auto',
                    seasonality_mode='multiplicative',
                    changepoint_prior_scale=0.05
                )
                self.model_tr1.fit(prophet_df_tr1)
                print("✅ TR1 model training complete!")

                # Train TR2 model
                print("\n🔮 Training TR2 (Direction 2) Model...")
                self.model_tr2 = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality='auto',
                    seasonality_mode='multiplicative',
                    changepoint_prior_scale=0.05
                )
                self.model_tr2.fit(prophet_df_tr2)
                print("✅ TR2 model training complete!")

                self.use_directions = True
                print("\n✅ All direction-specific models trained!")

            # Save the models
            self.save_model()

            return True

        except Exception as e:
            print(f"❌ Error training model: {e}")
            import traceback
            traceback.print_exc()
            return False

    def predict(self, hours_ahead=24):
        """
        Predict traffic volume for the next N hours.

        Parameters:
        - hours_ahead: Number of hours to forecast (default 24)

        Returns:
        - pandas DataFrame with predictions (ds, yhat, yhat_lower, yhat_upper)
        """
        if not self.trained or self.model is None:
            print("❌ Model not trained! Call train() first or load a saved model.")
            return None

        try:
            print(f"\n🔮 Generating {hours_ahead}-hour traffic forecast...")

            # Create future dataframe (15-minute intervals)
            # Convert hours to 15-minute periods (4 periods per hour)
            periods_15min = hours_ahead * 4
            future = self.model.make_future_dataframe(
                periods=periods_15min,
                freq='15T'
            )

            # Make predictions
            forecast = self.model.predict(future)

            # Get only future predictions (not historical)
            # Return the last N hours worth of 15-minute predictions
            future_only = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods_15min)

            print(f"✅ Forecast generated for next {hours_ahead} hours")
            print(f"   Start: {future_only['ds'].iloc[0]}")
            print(f"   End: {future_only['ds'].iloc[-1]}")
            print(f"   Predicted avg traffic: {future_only['yhat'].mean():.1f} vehicles")
            print(f"   Predicted max traffic: {future_only['yhat'].max():.1f} vehicles")

            return future_only

        except Exception as e:
            print(f"❌ Error making predictions: {e}")
            return None

    def get_current_prediction(self, include_directions=False, minutes_ahead=15):
        """
        Get prediction for the next N minutes (default 15 minutes for better response time).
        Calculates how many periods ahead from training data end to get current time prediction.

        Parameters:
        - include_directions: If True, also predict TR1 and TR2 separately (requires direction models)
        - minutes_ahead: Number of minutes to predict ahead (default 15 minutes)

        Returns:
        - Dictionary with prediction details
        """
        if not self.trained or self.model is None:
            print("❌ Model not trained! Call train() first or load a saved model.")
            return None

        try:
            from datetime import datetime
            import pandas as pd

            # Get current time
            now = datetime.now()

            # Round to nearest minute for prediction target
            target_time = now + timedelta(minutes=minutes_ahead)
            target_time = target_time.replace(second=0, microsecond=0)

            # Get the last training data point from the model's history
            # Prophet stores training data in model.history
            if hasattr(self.model, 'history') and len(self.model.history) > 0:
                last_training_time = pd.to_datetime(self.model.history['ds'].max())
            else:
                # Fallback: use make_future_dataframe with 0 periods to get last point
                future = self.model.make_future_dataframe(periods=0, freq='15T')
                if len(future) > 0:
                    last_training_time = pd.to_datetime(future['ds'].max())
                else:
                    last_training_time = now - timedelta(days=180)  # Fallback to 6 months ago

            # Calculate minutes from last training point to target time
            minutes_since_training = int((target_time - last_training_time).total_seconds() / 60)

            # Convert to 15-minute periods for Prophet (which now works in 15-minute intervals)
            periods_15min = int(minutes_since_training / 15)
            periods_ahead = max(1, periods_15min + 1)

            # Create future dataframe extending to the target time (15-minute intervals)
            future = self.model.make_future_dataframe(periods=periods_ahead, freq='15T')

            # Make prediction
            forecast = self.model.predict(future)

            # Get the prediction for the target time
            # Since Prophet works in hourly intervals, we use the hour that contains our target time
            if len(forecast) > 0:
                # Find the row closest to our target time
                forecast_times = pd.to_datetime(forecast['ds'])
                time_diffs = abs(forecast_times - target_time)
                closest_idx = time_diffs.idxmin()
                row = forecast.iloc[closest_idx]

                # The prediction is in vehicles per 15-minute period (based on training data)
                # Training data is aggregated to 15-minute intervals
                # To convert to vehicles per minute: divide by 15
                # To convert to vehicles per hour: multiply by 4

                predicted_per_15min = round(row['yhat'], 1)
                predicted_per_min = predicted_per_15min / 15.0  # Convert to per-minute for consistency

                # Cap predictions at reasonable maximum
                # Max reasonable per 15min: ~1125 vehicles (75 vehicles/min * 15 min)
                MAX_REASONABLE_15MIN = 1125.0
                if predicted_per_15min > MAX_REASONABLE_15MIN:
                    print(f"⚠️  Prediction {predicted_per_15min} vehicles/15min capped at {MAX_REASONABLE_15MIN}")
                    predicted_per_15min = MAX_REASONABLE_15MIN
                    predicted_per_min = predicted_per_15min / 15.0

                # Ensure minimum is reasonable (can't be negative)
                predicted_per_15min = max(0, predicted_per_15min)
                predicted_per_min = predicted_per_15min / 15.0

                # Cap bounds as well (convert to per-minute for consistency)
                lower_bound_15min = max(0, round(row['yhat_lower'], 1))
                upper_bound_15min = min(MAX_REASONABLE_15MIN, round(row['yhat_upper'], 1))
                lower_bound = lower_bound_15min / 15.0
                upper_bound = upper_bound_15min / 15.0

                # Get the timestamp for the prediction (closest hour to target)
                pred_timestamp = row['ds']

                result = {
                    'timestamp': pred_timestamp,
                    'predicted_traffic': predicted_per_min,  # Vehicles per minute (for consistency)
                    'predicted_traffic_15min': predicted_per_15min,  # Vehicles per 15-minute period
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'confidence_range': round(upper_bound - lower_bound, 1),
                    'target_minutes_ahead': minutes_ahead  # Store the actual target time we're predicting for
                }

                # If we have direction models, add direction-specific predictions
                if (include_directions or self.use_directions) and self.model_tr1 is not None and self.model_tr2 is not None:
                    # Create future dataframes for direction models (same periods, 15-minute intervals)
                    future_tr1 = self.model_tr1.make_future_dataframe(periods=periods_ahead, freq='15T')
                    future_tr2 = self.model_tr2.make_future_dataframe(periods=periods_ahead, freq='15T')

                    # Predict for each direction
                    forecast_tr1 = self.model_tr1.predict(future_tr1)
                    forecast_tr2 = self.model_tr2.predict(future_tr2)

                    if len(forecast_tr1) > 0 and len(forecast_tr2) > 0:
                        # Find closest time for direction predictions too
                        forecast_tr1_times = pd.to_datetime(forecast_tr1['ds'])
                        forecast_tr2_times = pd.to_datetime(forecast_tr2['ds'])
                        closest_idx_tr1 = abs(forecast_tr1_times - target_time).idxmin()
                        closest_idx_tr2 = abs(forecast_tr2_times - target_time).idxmin()
                        row_tr1 = forecast_tr1.iloc[closest_idx_tr1]
                        row_tr2 = forecast_tr2.iloc[closest_idx_tr2]

                        # Direction predictions are also in vehicles per 15-minute period
                        tr1_pred_15min = max(0, min(MAX_REASONABLE_15MIN, round(row_tr1['yhat'], 1)))
                        tr2_pred_15min = max(0, min(MAX_REASONABLE_15MIN, round(row_tr2['yhat'], 1)))

                        # Convert to per-minute for consistency
                        tr1_pred = tr1_pred_15min / 15.0
                        tr2_pred = tr2_pred_15min / 15.0

                        result['direction_1'] = tr1_pred
                        result['direction_2'] = tr2_pred
                        result['direction_1_15min'] = tr1_pred_15min
                        result['direction_2_15min'] = tr2_pred_15min
                        result['direction_1_lower'] = max(0, round(row_tr1['yhat_lower'], 1)) / 15.0
                        result['direction_1_upper'] = min(MAX_REASONABLE_15MIN, round(row_tr1['yhat_upper'], 1)) / 15.0
                        result['direction_2_lower'] = max(0, round(row_tr2['yhat_lower'], 1)) / 15.0
                        result['direction_2_upper'] = min(MAX_REASONABLE_15MIN, round(row_tr2['yhat_upper'], 1)) / 15.0

                return result
            return None

        except Exception as e:
            print(f"❌ Error getting current prediction: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_model(self, path=MODEL_PATH):
        """
        Save the trained model(s) to disk.
        Saves total model and direction-specific models if available.

        Parameters:
        - path: File path to save the main model
        """
        if not self.trained or self.model is None:
            print("❌ No trained model to save!")
            return False

        try:
            # Save main (total) model
            with open(path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'device_imei': self.device_imei,
                    'training_date': datetime.now(),
                    'use_directions': self.use_directions
                }, f)
            print(f"💾 Total traffic model saved to: {path}")

            # Save direction-specific models if available
            if self.use_directions and self.model_tr1 is not None and self.model_tr2 is not None:
                with open(MODEL_TR1_PATH, 'wb') as f:
                    pickle.dump({
                        'model': self.model_tr1,
                        'device_imei': self.device_imei,
                        'training_date': datetime.now(),
                        'direction': 'TR1'
                    }, f)
                print(f"💾 TR1 model saved to: {MODEL_TR1_PATH}")

                with open(MODEL_TR2_PATH, 'wb') as f:
                    pickle.dump({
                        'model': self.model_tr2,
                        'device_imei': self.device_imei,
                        'training_date': datetime.now(),
                        'direction': 'TR2'
                    }, f)
                print(f"💾 TR2 model saved to: {MODEL_TR2_PATH}")

            return True
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False

    def load_model(self, path=MODEL_PATH):
        """
        Load trained model(s) from disk.
        Loads total model and direction-specific models if available.

        Parameters:
        - path: File path to load the main model from
        """
        if not os.path.exists(path):
            print(f"❌ Model file not found: {path}")
            return False

        try:
            # Load main (total) model
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.device_imei = data.get('device_imei', 'unknown')
                self.trained = True
                self.use_directions = data.get('use_directions', False)

            training_date = data.get('training_date', 'Unknown')
            print(f"✅ Total traffic model loaded from: {path}")
            print(f"   Device: {self.device_imei}")
            print(f"   Trained: {training_date}")
            print(f"   Direction models: {'Yes' if self.use_directions else 'No'}")

            # Try to load direction-specific models if they exist
            if os.path.exists(MODEL_TR1_PATH) and os.path.exists(MODEL_TR2_PATH):
                try:
                    with open(MODEL_TR1_PATH, 'rb') as f:
                        data_tr1 = pickle.load(f)
                        self.model_tr1 = data_tr1['model']
                    print(f"✅ TR1 model loaded from: {MODEL_TR1_PATH}")

                    with open(MODEL_TR2_PATH, 'rb') as f:
                        data_tr2 = pickle.load(f)
                        self.model_tr2 = data_tr2['model']
                    print(f"✅ TR2 model loaded from: {MODEL_TR2_PATH}")

                    self.use_directions = True
                except Exception as e:
                    print(f"⚠️  Could not load direction models: {e}")
                    self.use_directions = False

            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False


def simulate_predictions_for_demo():
    """
    Generate simulated predictions for demo purposes (if real data isn't available).
    Returns sample predictions that vary by time of day.
    """
    import numpy as np

    current_hour = datetime.now().hour

    # Simulate rush hour patterns
    if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
        # Morning/evening rush hour
        base_traffic = 150
        variation = 30
    elif 10 <= current_hour <= 16:
        # Midday moderate traffic
        base_traffic = 80
        variation = 20
    else:
        # Night/early morning low traffic
        base_traffic = 30
        variation = 10

    # Add some randomness
    predicted = base_traffic + np.random.randint(-variation, variation)

    return {
        'timestamp': datetime.now(),
        'predicted_traffic': max(0, predicted),
        'lower_bound': max(0, predicted - 20),
        'upper_bound': predicted + 20,
        'confidence_range': 40
    }


if __name__ == "__main__":
    """
    Main execution: Train the model with extracted data
    Trains separate models for total traffic, TR1, and TR2
    """
    print("=" * 70)
    print("🧠 PROJECT ECOFLOW - MODEL TRAINING")
    print("=" * 70)

    # Path to training data (from data_extraction.py)
    data_path = f'data_cache/german_traffic_{TRAINING_DATA_MONTHS}m.csv'

    # Check if data exists
    if not os.path.exists(data_path):
        print(f"\n❌ Training data not found: {data_path}")
        print("⚠️  Run data_extraction.py first to extract the training data")
        exit(1)

    # Initialize and train (with direction-specific models)
    predictor = TrafficPredictor()
    print(f"\n📊 Training on {TRAINING_DATA_MONTHS} months of data with direction-specific models...")
    success = predictor.train(data_path, train_directions=True)

    if success:
        print("\n" + "=" * 70)
        print("🎯 TESTING PREDICTIONS")
        print("=" * 70)

        # Test with 24-hour forecast
        forecast = predictor.predict(hours_ahead=24)

        if forecast is not None:
            print("\n📊 Sample predictions:")
            print(forecast.head(10).to_string(index=False))

            # Get current hour prediction
            current = predictor.get_current_prediction()
            if current:
                print(f"\n🔮 Current hour prediction:")
                print(f"   Time: {current['timestamp']}")
                print(f"   Predicted traffic: {current['predicted_traffic']} vehicles")
                print(f"   Range: {current['lower_bound']} - {current['upper_bound']}")

        print("\n" + "=" * 70)
        print("✅ MODEL TRAINING & TESTING COMPLETE!")
        print("=" * 70)
        print(f"\n💾 Model saved to: {MODEL_PATH}")
        print(f"🎯 Next step: Run the dashboard with: streamlit run app.py")
    else:
        print("\n❌ Model training failed!")
        exit(1)
