"""
Probabilistic risk scoring for vector-borne disease surveillance.

Computes risk probabilities with uncertainty quantification.
"""

from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd


class ProbabilisticRiskScorer:
    """
    Probabilistic risk scoring system.
    
    Integrates ecological, epidemiological, and operational data to compute
    risk probabilities with uncertainty bands.
    """
    
    def __init__(self):
        """Initialize the risk scorer."""
        pass
    
    def compute_vector_presence_probability(
        self,
        habitat_suitability: pd.Series,
        recent_observations: Optional[int] = None,
        observation_confidence: float = 0.8
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute probability of vector presence with uncertainty.
        
        Args:
            habitat_suitability: Series with habitat suitability (0-1)
            recent_observations: Number of confirmed recent observations (optional)
            observation_confidence: Confidence level for observations (0-1)
        
        Returns:
            Tuple of (point_estimate, lower_ci, upper_ci)
        """
        # Base probability from habitat suitability
        point_prob = habitat_suitability.copy()
        
        # Add observational data if available
        if recent_observations is not None and recent_observations > 0:
            observation_signal = min(observation_confidence, 0.9)
            point_prob = 0.7 * point_prob + 0.3 * observation_signal
        
        # Uncertainty bands (wider for lower probabilities)
        uncertainty = 0.15 * (1 - point_prob)
        lower_ci = (point_prob - uncertainty).clip(0, 1)
        upper_ci = (point_prob + uncertainty).clip(0, 1)
        
        return point_prob, lower_ci, upper_ci
    
    def compute_transmission_risk(
        self,
        vector_probability: pd.Series,
        case_indicator: Optional[pd.Series] = None,
        pathogen_circulation: float = 0.5
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute probability of pathogen transmission given vector presence.
        
        Args:
            vector_probability: Probability of vector presence (0-1)
            case_indicator: Optional series indicating confirmed cases (0/1)
            pathogen_circulation: Prior probability of pathogen in vector population
        
        Returns:
            Tuple of (point_estimate, lower_ci, upper_ci)
        """
        # Transmission risk conditional on vector presence
        point_prob = vector_probability * pathogen_circulation
        
        # If cases are observed, increase signal
        if case_indicator is not None:
            confirmed_signal = case_indicator.astype(float) * 0.8
            point_prob = 0.6 * point_prob + 0.4 * confirmed_signal
        
        # Uncertainty
        uncertainty = 0.2 * (1 - point_prob)
        lower_ci = (point_prob - uncertainty).clip(0, 1)
        upper_ci = (point_prob + uncertainty).clip(0, 1)
        
        return point_prob, lower_ci, upper_ci
    
    def compute_human_exposure_risk(
        self,
        transmission_probability: pd.Series,
        land_use_exposure: Optional[pd.Series] = None,
        seasonal_activity: Optional[pd.Series] = None,
        baseline_human_exposure: float = 0.3
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute probability of human exposure to the vector.
        
        Args:
            transmission_probability: Transmission probability (0-1)
            land_use_exposure: Land use exposure factor (0-1)
            seasonal_activity: Seasonal activity factor (0-1)
            baseline_human_exposure: Baseline human-vector contact rate
        
        Returns:
            Tuple of (point_estimate, lower_ci, upper_ci)
        """
        point_prob = transmission_probability * baseline_human_exposure
        
        if land_use_exposure is not None:
            point_prob = point_prob * (1 + 0.5 * land_use_exposure)
        
        if seasonal_activity is not None:
            point_prob = point_prob * seasonal_activity
        
        point_prob = point_prob.clip(0, 1)
        
        # Uncertainty
        uncertainty = 0.25 * (1 - point_prob)
        lower_ci = (point_prob - uncertainty).clip(0, 1)
        upper_ci = (point_prob + uncertainty).clip(0, 1)
        
        return point_prob, lower_ci, upper_ci
    
    def compute_outbreak_risk(
        self,
        exposure_probability: pd.Series,
        case_count: Optional[pd.Series] = None,
        trend: Optional[str] = None,
        baseline_cases: float = 0.1
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute outbreak risk (elevated case probability above baseline).
        
        Args:
            exposure_probability: Human exposure probability (0-1)
            case_count: Recent case counts (optional)
            trend: Trend direction ('increasing', 'stable', 'decreasing')
            baseline_cases: Baseline case rate
        
        Returns:
            Tuple of (point_estimate, lower_ci, upper_ci)
        """
        point_prob = exposure_probability * 0.5 + baseline_cases * 0.5
        
        # Add case data signal
        if case_count is not None:
            case_signal = case_count / (case_count.max() + 1)  # Normalize
            point_prob = 0.7 * point_prob + 0.3 * case_signal
        
        # Trend adjustment
        if trend == 'increasing':
            point_prob = point_prob * 1.3
        elif trend == 'decreasing':
            point_prob = point_prob * 0.7
        
        point_prob = point_prob.clip(0, 1)
        
        # Uncertainty
        uncertainty = 0.25 * (1 - point_prob)
        lower_ci = (point_prob - uncertainty).clip(0, 1)
        upper_ci = (point_prob + uncertainty).clip(0, 1)
        
        return point_prob, lower_ci, upper_ci
    
    def categorize_risk(self, probability: pd.Series) -> pd.Series:
        """
        Categorize risk level from probability.
        
        Args:
            probability: Risk probability (0-1)
        
        Returns:
            Series with risk categories: LOW, MODERATE, HIGH
        """
        categories = pd.cut(
            probability,
            bins=[0, 0.3, 0.7, 1.0],
            labels=['LOW', 'MODERATE', 'HIGH'],
            include_lowest=True
        )
        return categories
    
    def compute_integrated_risk_score(
        self,
        vector_prob: pd.Series,
        transmission_prob: pd.Series,
        exposure_prob: pd.Series,
        outbreak_prob: pd.Series,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute integrated risk score from multiple components.
        
        Args:
            vector_prob: Vector presence probability
            transmission_prob: Pathogen transmission probability
            exposure_prob: Human exposure probability
            outbreak_prob: Outbreak risk probability
            weights: Optional component weights
        
        Returns:
            Tuple of (point_estimate, lower_ci, upper_ci)
        """
        if weights is None:
            weights = {
                'vector': 0.2,
                'transmission': 0.3,
                'exposure': 0.3,
                'outbreak': 0.2
            }
        
        point_score = (
            weights['vector'] * vector_prob +
            weights['transmission'] * transmission_prob +
            weights['exposure'] * exposure_prob +
            weights['outbreak'] * outbreak_prob
        )
        
        # Uncertainty bands (use max component uncertainty)
        component_uncertainties = pd.concat([
            (vector_prob * (1 - vector_prob)) ** 0.5,
            (transmission_prob * (1 - transmission_prob)) ** 0.5,
            (exposure_prob * (1 - exposure_prob)) ** 0.5,
            (outbreak_prob * (1 - outbreak_prob)) ** 0.5,
        ], axis=1)
        
        max_component_uncertainty = component_uncertainties.max(axis=1)
        overall_uncertainty = 0.3 * max_component_uncertainty
        
        lower_ci = (point_score - overall_uncertainty).clip(0, 1)
        upper_ci = (point_score + overall_uncertainty).clip(0, 1)
        
        return point_score.clip(0, 1), lower_ci, upper_ci
