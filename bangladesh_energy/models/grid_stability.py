"""
Grid stability model for analyzing power system stability and reliability.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GridParameters:
    """Grid stability parameters."""
    base_load: float  # Base load in MW
    peak_load: float  # Peak load in MW
    voltage_levels: List[float]  # Voltage levels in kV
    transmission_loss: float  # Transmission loss factor
    spinning_reserve: float  # Spinning reserve requirement (%)
    frequency_band: Tuple[float, float]  # Acceptable frequency range (Hz)
    voltage_band: Tuple[float, float]  # Acceptable voltage range (p.u.)

class GridStabilityModel:
    """Model for analyzing grid stability and reliability."""
    
    def __init__(self, params: GridParameters):
        self.params = params
        self.frequency = 50.0  # Base frequency in Hz
        self.voltage = 1.0  # Base voltage in p.u.
    
    def calculate_power_flow(self, generation: Dict[str, float], 
                           load: float) -> Dict[str, float]:
        """Calculate power flow and system stability metrics."""
        # Calculate total generation
        total_gen = sum(generation.values())
        
        # Calculate power balance
        power_balance = total_gen - load
        
        # Calculate frequency deviation
        freq_deviation = self._calculate_frequency_deviation(power_balance)
        
        # Calculate voltage stability
        voltage_stability = self._calculate_voltage_stability(generation, load)
        
        # Calculate spinning reserve adequacy
        reserve_adequacy = self._calculate_reserve_adequacy(generation, load)
        
        return {
            'power_balance': power_balance,
            'frequency_deviation': freq_deviation,
            'voltage_stability': voltage_stability,
            'reserve_adequacy': reserve_adequacy
        }
    
    def _calculate_frequency_deviation(self, power_balance: float) -> float:
        """Calculate frequency deviation based on power balance."""
        # Simple frequency-power relationship
        # Assuming 1% frequency change per 1% power imbalance
        freq_deviation = (power_balance / self.params.base_load) * self.frequency
        return freq_deviation
    
    def _calculate_voltage_stability(self, generation: Dict[str, float],
                                   load: float) -> float:
        """Calculate voltage stability margin."""
        # Calculate voltage stability based on generation-load ratio
        gen_load_ratio = sum(generation.values()) / load
        
        # Simple voltage stability index
        # Higher value indicates better stability
        stability_index = 1.0 - abs(1.0 - gen_load_ratio)
        return max(0.0, stability_index)
    
    def _calculate_reserve_adequacy(self, generation: Dict[str, float],
                                  load: float) -> float:
        """Calculate spinning reserve adequacy."""
        # Calculate required spinning reserve
        required_reserve = load * self.params.spinning_reserve
        
        # Calculate available reserve (assuming 10% of generation capacity)
        available_reserve = sum(generation.values()) * 0.1
        
        # Calculate reserve adequacy ratio
        adequacy_ratio = available_reserve / required_reserve
        return min(1.0, adequacy_ratio)
    
    def analyze_stability(self, generation_profile: pd.DataFrame,
                         load_profile: pd.Series) -> pd.DataFrame:
        """Analyze grid stability over time."""
        stability_metrics = []
        
        for timestamp in generation_profile.index:
            # Get generation and load for current timestamp
            generation = generation_profile.loc[timestamp].to_dict()
            load = load_profile.loc[timestamp]
            
            # Calculate stability metrics
            metrics = self.calculate_power_flow(generation, load)
            metrics['timestamp'] = timestamp
            stability_metrics.append(metrics)
        
        return pd.DataFrame(stability_metrics)
    
    def calculate_reliability_metrics(self, stability_results: pd.DataFrame) -> Dict:
        """Calculate system reliability metrics."""
        # Calculate frequency stability
        freq_stable = np.mean(
            (stability_results['frequency_deviation'] >= self.params.frequency_band[0]) &
            (stability_results['frequency_deviation'] <= self.params.frequency_band[1])
        )
        
        # Calculate voltage stability
        volt_stable = np.mean(
            stability_results['voltage_stability'] >= 0.8  # 80% stability threshold
        )
        
        # Calculate reserve adequacy
        reserve_adequate = np.mean(
            stability_results['reserve_adequacy'] >= 0.9  # 90% adequacy threshold
        )
        
        # Calculate system reliability index
        reliability_index = (freq_stable + volt_stable + reserve_adequate) / 3
        
        return {
            'frequency_stability': freq_stable,
            'voltage_stability': volt_stable,
            'reserve_adequacy': reserve_adequate,
            'system_reliability': reliability_index
        } 