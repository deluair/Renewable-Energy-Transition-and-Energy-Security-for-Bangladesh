"""
Demand response model for analyzing load flexibility and demand-side management.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DemandResponseType(Enum):
    """Types of demand response programs."""
    PRICE_RESPONSE = "price_response"
    INCENTIVE_BASED = "incentive_based"
    EMERGENCY = "emergency"
    DIRECT_LOAD_CONTROL = "direct_load_control"

@dataclass
class DemandResponseParameters:
    """Parameters for demand response programs."""
    program_type: DemandResponseType
    participation_rate: float  # Expected participation rate
    response_delay: float  # Response delay in minutes
    duration: float  # Expected duration in hours
    max_reduction: float  # Maximum load reduction in MW
    min_reduction: float  # Minimum load reduction in MW
    incentive_rate: float  # Incentive rate in USD/kWh
    notification_time: float  # Required notification time in hours

class DemandResponseModel:
    """Model for analyzing demand response programs."""
    
    def __init__(self, params: DemandResponseParameters):
        self.params = params
        self.active_events = []
    
    def calculate_load_reduction(self, 
                               base_load: pd.Series,
                               price: pd.Series,
                               temperature: pd.Series) -> pd.DataFrame:
        """Calculate potential load reduction from demand response."""
        results = []
        
        for timestamp in base_load.index:
            # Calculate price elasticity
            price_elasticity = self._calculate_price_elasticity(
                price[timestamp],
                price.mean()
            )
            
            # Calculate temperature sensitivity
            temp_sensitivity = self._calculate_temperature_sensitivity(
                temperature[timestamp]
            )
            
            # Calculate base reduction
            base_reduction = (
                self.params.max_reduction *
                self.params.participation_rate *
                price_elasticity *
                temp_sensitivity
            )
            
            # Apply constraints
            reduction = min(
                max(base_reduction, self.params.min_reduction),
                self.params.max_reduction
            )
            
            # Record results
            results.append({
                'timestamp': timestamp,
                'base_load': base_load[timestamp],
                'price': price[timestamp],
                'temperature': temperature[timestamp],
                'price_elasticity': price_elasticity,
                'temp_sensitivity': temp_sensitivity,
                'load_reduction': reduction,
                'reduced_load': base_load[timestamp] - reduction
            })
        
        return pd.DataFrame(results)
    
    def _calculate_price_elasticity(self, current_price: float,
                                  average_price: float) -> float:
        """Calculate price elasticity of demand."""
        # Simple price elasticity model
        # Higher prices lead to higher elasticity
        price_ratio = current_price / average_price
        elasticity = 0.5 * (price_ratio - 1)  # Base elasticity of 0.5
        return max(0.0, min(1.0, elasticity))
    
    def _calculate_temperature_sensitivity(self, temperature: float) -> float:
        """Calculate temperature sensitivity of demand response."""
        # Temperature sensitivity model
        # Higher sensitivity during extreme temperatures
        optimal_temp = 22.0  # Optimal temperature in Celsius
        temp_diff = abs(temperature - optimal_temp)
        sensitivity = 1.0 - (temp_diff / 20.0)  # Normalize to 0-1 range
        return max(0.0, min(1.0, sensitivity))
    
    def simulate_demand_response_event(self,
                                     load_profile: pd.Series,
                                     event_start: pd.Timestamp,
                                     event_duration: float) -> pd.DataFrame:
        """Simulate a demand response event."""
        # Calculate event end time
        event_end = event_start + pd.Timedelta(hours=event_duration)
        
        # Get load profile during event
        event_load = load_profile[event_start:event_end]
        
        # Calculate load reduction
        reduction = self.calculate_load_reduction(
            event_load,
            pd.Series(1.0, index=event_load.index),  # Placeholder price
            pd.Series(25.0, index=event_load.index)  # Placeholder temperature
        )
        
        # Record event
        self.active_events.append({
            'start_time': event_start,
            'end_time': event_end,
            'duration': event_duration,
            'avg_reduction': reduction['load_reduction'].mean(),
            'total_reduction': reduction['load_reduction'].sum()
        })
        
        return reduction
    
    def calculate_program_metrics(self, 
                                load_reductions: pd.DataFrame) -> Dict:
        """Calculate demand response program metrics."""
        # Calculate reliability
        reliability = np.mean(
            load_reductions['load_reduction'] >= self.params.min_reduction
        )
        
        # Calculate response time compliance
        response_compliance = np.mean(
            load_reductions['load_reduction'] > 0
        )
        
        # Calculate economic benefits
        total_reduction = load_reductions['load_reduction'].sum()
        incentive_cost = total_reduction * self.params.incentive_rate
        
        # Calculate program effectiveness
        effectiveness = (
            load_reductions['load_reduction'].mean() /
            self.params.max_reduction
        )
        
        return {
            'reliability': reliability,
            'response_compliance': response_compliance,
            'total_reduction': total_reduction,
            'incentive_cost': incentive_cost,
            'effectiveness': effectiveness,
            'event_count': len(self.active_events)
        }
    
    def analyze_participant_behavior(self,
                                   load_reductions: pd.DataFrame) -> Dict:
        """Analyze participant behavior in demand response programs."""
        # Calculate participation consistency
        participation_consistency = np.mean(
            load_reductions['load_reduction'] > 0
        )
        
        # Calculate response magnitude
        avg_response = load_reductions['load_reduction'].mean()
        max_response = load_reductions['load_reduction'].max()
        
        # Calculate price sensitivity
        price_sensitivity = np.corrcoef(
            load_reductions['price'],
            load_reductions['load_reduction']
        )[0, 1]
        
        # Calculate temperature sensitivity
        temp_sensitivity = np.corrcoef(
            load_reductions['temperature'],
            load_reductions['load_reduction']
        )[0, 1]
        
        return {
            'participation_consistency': participation_consistency,
            'avg_response': avg_response,
            'max_response': max_response,
            'price_sensitivity': price_sensitivity,
            'temp_sensitivity': temp_sensitivity
        } 