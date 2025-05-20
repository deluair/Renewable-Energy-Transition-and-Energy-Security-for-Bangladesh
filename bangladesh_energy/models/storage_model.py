"""
Energy storage model for analyzing different storage technologies and their integration.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class StorageTechnology(Enum):
    """Types of energy storage technologies."""
    LITHIUM_ION = "lithium_ion"
    PUMPED_HYDRO = "pumped_hydro"
    FLOW_BATTERY = "flow_battery"
    THERMAL = "thermal"
    HYDROGEN = "hydrogen"

@dataclass
class StorageParameters:
    """Parameters for energy storage systems."""
    technology: StorageTechnology
    capacity: float  # Storage capacity in MWh
    power: float  # Power rating in MW
    efficiency: float  # Round-trip efficiency
    lifetime: int  # Expected lifetime in years
    capex: float  # Capital cost in USD/kWh
    opex: float  # Operational cost in USD/kWh/year
    degradation: float  # Annual capacity degradation rate
    response_time: float  # Response time in seconds

class StorageModel:
    """Model for analyzing energy storage systems."""
    
    def __init__(self, params: StorageParameters):
        self.params = params
        self.current_capacity = params.capacity
        self.cycles = 0
    
    def calculate_storage_operation(self, 
                                  generation: pd.Series,
                                  load: pd.Series,
                                  price: pd.Series) -> pd.DataFrame:
        """Calculate storage operation over time."""
        results = []
        current_energy = 0.0
        
        for timestamp in generation.index:
            # Calculate net power
            net_power = generation[timestamp] - load[timestamp]
            
            # Determine storage action
            if net_power > 0:  # Excess generation
                # Charge if price is low
                if price[timestamp] < price.mean():
                    charge_power = min(net_power, 
                                    self.params.power,
                                    (self.current_capacity - current_energy) / 
                                    self.params.efficiency)
                    current_energy += charge_power * self.params.efficiency
                    self.cycles += 1
                else:
                    charge_power = 0
            else:  # Generation deficit
                # Discharge if price is high
                if price[timestamp] > price.mean():
                    discharge_power = min(abs(net_power),
                                       self.params.power,
                                       current_energy)
                    current_energy -= discharge_power
                    self.cycles += 1
                else:
                    discharge_power = 0
            
            # Record results
            results.append({
                'timestamp': timestamp,
                'net_power': net_power,
                'charge_power': charge_power if net_power > 0 else 0,
                'discharge_power': discharge_power if net_power < 0 else 0,
                'stored_energy': current_energy,
                'price': price[timestamp]
            })
        
        return pd.DataFrame(results)
    
    def calculate_economics(self, operation_results: pd.DataFrame) -> Dict:
        """Calculate economic metrics for storage operation."""
        # Calculate total energy throughput
        total_throughput = (
            operation_results['charge_power'].sum() +
            operation_results['discharge_power'].sum()
        )
        
        # Calculate revenue from price arbitrage
        revenue = (
            operation_results['discharge_power'] * 
            operation_results['price']
        ).sum()
        
        # Calculate costs
        capex = self.params.capacity * self.params.capex
        opex = self.params.capacity * self.params.opex * self.params.lifetime
        
        # Calculate degradation cost
        degradation_cost = (
            self.params.capacity * 
            self.params.capex * 
            (1 - (1 - self.params.degradation) ** self.params.lifetime)
        )
        
        # Calculate total cost
        total_cost = capex + opex + degradation_cost
        
        # Calculate net present value (simplified)
        npv = revenue - total_cost
        
        return {
            'total_throughput': total_throughput,
            'revenue': revenue,
            'capex': capex,
            'opex': opex,
            'degradation_cost': degradation_cost,
            'total_cost': total_cost,
            'npv': npv,
            'cycles': self.cycles
        }
    
    def calculate_performance_metrics(self, 
                                    operation_results: pd.DataFrame) -> Dict:
        """Calculate performance metrics for storage operation."""
        # Calculate capacity factor
        capacity_factor = (
            operation_results['discharge_power'].sum() /
            (self.params.power * len(operation_results))
        )
        
        # Calculate utilization rate
        utilization_rate = (
            operation_results['stored_energy'].mean() /
            self.current_capacity
        )
        
        # Calculate round-trip efficiency
        actual_efficiency = (
            operation_results['discharge_power'].sum() /
            operation_results['charge_power'].sum()
            if operation_results['charge_power'].sum() > 0
            else 0
        )
        
        # Calculate response time compliance
        response_compliance = np.mean(
            operation_results['discharge_power'] > 0
        )
        
        return {
            'capacity_factor': capacity_factor,
            'utilization_rate': utilization_rate,
            'actual_efficiency': actual_efficiency,
            'response_compliance': response_compliance,
            'cycles_per_day': self.cycles / (len(operation_results) / 24)
        }
    
    def update_capacity(self):
        """Update storage capacity based on degradation."""
        self.current_capacity *= (1 - self.params.degradation) 