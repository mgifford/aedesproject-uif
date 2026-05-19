"""
Multi-layer validation for vector-borne disease models.

Implements ecological, entomological, epidemiological, and operational validation
with rolling backtesting, baseline comparison, and uncertainty quantification.
"""

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd


class MultiLayerValidator:
    """
    Multi-layer validation framework.
    
    Validates models across:
    - Ecological (vector habitat predictions vs. known distribution)
    - Entomological (vector pool data vs. predictions)
    - Epidemiological (case predictions vs. observed cases)
    - Operational (lead time, false alerts, resource efficiency)
    """
    
    def __init__(self):
        """Initialize the validator."""
        self.results: Dict = {}
    
    def validate_ecological_accuracy(
        self,
        predicted_habitat: pd.Series,
        observed_presence: pd.Series,
        presence_threshold: float = 0.5
    ) -> Dict:
        """
        Validate ecological habitat predictions against known vector presence.
        
        Args:
            predicted_habitat: Predicted habitat suitability (0-1)
            observed_presence: Observed vector presence (0/1)
            presence_threshold: Threshold for converting probability to binary
        
        Returns:
            Dict with accuracy metrics
        """
        binary_predicted = (predicted_habitat > presence_threshold).astype(int)
        
        tp = ((binary_predicted == 1) & (observed_presence == 1)).sum()
        tn = ((binary_predicted == 0) & (observed_presence == 0)).sum()
        fp = ((binary_predicted == 1) & (observed_presence == 0)).sum()
        fn = ((binary_predicted == 0) & (observed_presence == 1)).sum()
        
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        results = {
            'accuracy': accuracy,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'tp': tp,
            'tn': tn,
            'fp': fp,
            'fn': fn,
        }
        
        self.results['ecological'] = results
        return results
    
    def validate_entomological_correlation(
        self,
        predicted_vector_activity: pd.Series,
        observed_pools_or_counts: pd.Series
    ) -> Dict:
        """
        Validate vector activity predictions against pool/trap data.
        
        Args:
            predicted_vector_activity: Predicted vector activity (0-1)
            observed_pools_or_counts: Observed mosquito pool counts or trap counts
        
        Returns:
            Dict with correlation metrics
        """
        # Normalize observed counts to 0-1
        if observed_pools_or_counts.max() > 0:
            normalized_observed = observed_pools_or_counts / observed_pools_or_counts.max()
        else:
            normalized_observed = pd.Series(0, index=observed_pools_or_counts.index)
        
        # Correlation
        correlation = predicted_vector_activity.corr(normalized_observed)
        
        results = {
            'correlation': correlation,
            'spearman_corr': predicted_vector_activity.corr(normalized_observed, method='spearman'),
        }
        
        self.results['entomological'] = results
        return results
    
    def validate_epidemiological_accuracy(
        self,
        predicted_risk: pd.Series,
        observed_cases: pd.Series,
        lead_time_days: int = 14
    ) -> Dict:
        """
        Validate outbreak predictions against observed cases.
        
        Measures lead time, sensitivity to severe outbreaks, false alert rate.
        
        Args:
            predicted_risk: Predicted risk probability (0-1)
            observed_cases: Observed weekly/daily case counts
            lead_time_days: Expected lead time for outbreak prediction
        
        Returns:
            Dict with epidemiological metrics
        """
        # Binary high-risk threshold
        risk_threshold = 0.7
        high_risk_predicted = (predicted_risk > risk_threshold).astype(int)
        
        # Binary outbreak threshold (cases above median + 1 SD)
        case_mean = observed_cases.mean()
        case_std = observed_cases.std()
        outbreak_threshold = case_mean + case_std
        outbreak_observed = (observed_cases > outbreak_threshold).astype(int)
        
        # Lead time analysis
        # Look for predictions that precede observed outbreaks by lead_time_days
        lead_window = lead_time_days // 7  # Convert to weeks if weekly data
        
        # Simple lead-time detection
        lead_times = []
        for i, outbreak_idx in enumerate(outbreak_observed[outbreak_observed == 1].index):
            if isinstance(outbreak_idx, int):
                days_before = outbreak_idx - lead_time_days
                if days_before >= 0 and high_risk_predicted.iloc[days_before] == 1:
                    lead_times.append(lead_time_days)
        
        lead_time_pct = len(lead_times) / max(outbreak_observed.sum(), 1)
        
        # Metrics
        tp = ((high_risk_predicted == 1) & (outbreak_observed == 1)).sum()
        tn = ((high_risk_predicted == 0) & (outbreak_observed == 0)).sum()
        fp = ((high_risk_predicted == 1) & (outbreak_observed == 0)).sum()
        fn = ((high_risk_predicted == 0) & (outbreak_observed == 1)).sum()
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        false_alert_rate = fp / (fp + tp) if (fp + tp) > 0 else 0
        
        results = {
            'lead_time_fraction': lead_time_pct,
            'sensitivity_to_outbreaks': sensitivity,
            'false_alert_rate': false_alert_rate,
            'outbreak_detection_tp': tp,
            'outbreak_detection_fp': fp,
            'outbreak_detection_fn': fn,
        }
        
        self.results['epidemiological'] = results
        return results
    
    def compare_to_baselines(
        self,
        predicted_cases: pd.Series,
        observed_cases: pd.Series,
        historical_data: Optional[pd.Series] = None
    ) -> Dict:
        """
        Compare model predictions against naive baselines.
        
        Args:
            predicted_cases: Model predictions
            observed_cases: Observed cases
            historical_data: Historical cases for baseline (optional)
        
        Returns:
            Dict with baseline comparisons (MAE, RMSE vs. baselines)
        """
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        
        model_mae = mean_absolute_error(observed_cases, predicted_cases)
        model_rmse = mean_squared_error(observed_cases, predicted_cases) ** 0.5
        
        baselines = {}
        
        # Seasonal average baseline
        if historical_data is not None and len(historical_data) > 0:
            seasonal_baseline = pd.Series([historical_data.mean()] * len(predicted_cases), index=predicted_cases.index)
            baselines['seasonal_avg_mae'] = mean_absolute_error(observed_cases, seasonal_baseline)
            baselines['seasonal_avg_rmse'] = mean_squared_error(observed_cases, seasonal_baseline) ** 0.5
        
        # Persistence baseline (previous value)
        persistence_baseline = observed_cases.shift(1).fillna(observed_cases.mean())
        baselines['persistence_mae'] = mean_absolute_error(observed_cases, persistence_baseline)
        baselines['persistence_rmse'] = mean_squared_error(observed_cases, persistence_baseline) ** 0.5
        
        results = {
            'model_mae': model_mae,
            'model_rmse': model_rmse,
            'baselines': baselines,
            'mae_improvement_vs_persistence': (baselines.get('persistence_mae', model_mae) - model_mae) / baselines.get('persistence_mae', 1),
        }
        
        self.results['baseline_comparison'] = results
        return results
    
    def validate_geographic_generalization(
        self,
        model_predictions: Dict[str, pd.Series],
        observed_cases: Dict[str, pd.Series],
        geography_types: Dict[str, str]  # e.g., {'urban': ['Denver'], 'rural': ['County1']}
    ) -> Dict:
        """
        Validate model performance across different geographic strata.
        
        Args:
            model_predictions: Dict of predictions by geography
            observed_cases: Dict of observed cases by geography
            geography_types: Dict mapping geographies to types (urban/rural/elevation)
        
        Returns:
            Dict with geographic performance stratification
        """
        results = {}
        
        for geo, pred in model_predictions.items():
            if geo not in observed_cases:
                continue
            
            obs = observed_cases[geo]
            geog_type = geography_types.get(geo, 'unknown')
            
            mae = abs(pred - obs).mean()
            corr = pred.corr(obs)
            
            if geog_type not in results:
                results[geog_type] = []
            
            results[geog_type].append({'geography': geo, 'mae': mae, 'correlation': corr})
        
        # Aggregate by type
        aggregated = {}
        for geog_type, metrics_list in results.items():
            maes = [m['mae'] for m in metrics_list]
            corrs = [m['correlation'] for m in metrics_list]
            aggregated[geog_type] = {
                'mean_mae': np.mean(maes),
                'std_mae': np.std(maes),
                'mean_correlation': np.mean(corrs),
            }
        
        self.results['geographic_generalization'] = aggregated
        return aggregated
    
    def validate_drift_testing(
        self,
        predictions_pre_event: pd.Series,
        observations_pre_event: pd.Series,
        predictions_post_event: pd.Series,
        observations_post_event: pd.Series,
        event_name: str = "climate_shift"
    ) -> Dict:
        """
        Test for model drift before/after significant events.
        
        Args:
            predictions_pre_event: Predictions before event
            observations_pre_event: Observations before event
            predictions_post_event: Predictions after event
            observations_post_event: Observations after event
            event_name: Description of event (e.g., 'drought', 'pandemic')
        
        Returns:
            Dict with drift metrics
        """
        from sklearn.metrics import mean_absolute_error
        
        pre_mae = mean_absolute_error(observations_pre_event, predictions_pre_event)
        post_mae = mean_absolute_error(observations_post_event, predictions_post_event)
        
        drift_pct = ((post_mae - pre_mae) / pre_mae * 100) if pre_mae > 0 else 0
        
        results = {
            'event': event_name,
            'pre_event_mae': pre_mae,
            'post_event_mae': post_mae,
            'drift_percent': drift_pct,
            'model_degradation': 'yes' if drift_pct > 10 else 'no',
        }
        
        self.results['drift_testing'] = results
        return results
    
    def get_validation_report(self) -> Dict:
        """Return full validation report."""
        return self.results
