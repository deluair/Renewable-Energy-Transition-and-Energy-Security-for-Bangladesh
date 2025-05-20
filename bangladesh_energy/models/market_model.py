"""
Market model for analyzing electricity market operations and pricing.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MarketType(Enum):
    """Types of electricity markets."""
    DAY_AHEAD = "day_ahead"
    REAL_TIME = "real_time"
    BALANCING = "balancing"
    CAPACITY = "capacity"

@dataclass
class Generator:
    """Parameters for a power generator."""
    name: str
    technology: str
    capacity: float  # Installed capacity in MW
    min_output: float  # Minimum output in MW
    ramp_rate: float  # Ramp rate in MW/hour
    variable_cost: float  # Variable cost in USD/MWh
    fixed_cost: float  # Fixed cost in USD/MW/year
    start_cost: float  # Start-up cost in USD
    min_uptime: float  # Minimum uptime in hours
    min_downtime: float  # Minimum downtime in hours

@dataclass
class MarketParameters:
    """Parameters for electricity market simulation."""
    market_type: MarketType
    price_cap: float  # Price cap in USD/MWh
    price_floor: float  # Price floor in USD/MWh
    demand_elasticity: float  # Price elasticity of demand
    market_clearing_interval: float  # Market clearing interval in hours
    reserve_margin: float  # Required reserve margin

class MarketModel:
    """Model for analyzing electricity market operations."""
    
    def __init__(self, params: MarketParameters):
        self.params = params
        self.generators = {}
        self.market_results = []
    
    def add_generator(self, generator: Generator):
        """Add a generator to the market."""
        self.generators[generator.name] = generator
    
    def clear_market(self, 
                     demand_annual_total: float, # Changed from demand_profile Series
                     renewable_generation_annual_total: float # Changed from renewable_generation Series
                    ) -> pd.DataFrame:
        """Clear the electricity market (simplified for annual data)."""
        # This is a simplified version. For accurate hourly market clearing,
        # energy_results should provide hourly demand and generation profiles.
        results = []
        # Simplified market clearing for annual totals
        # Assume a single clearing for the year
        # Calculate available conventional generation
        total_capacity = sum(gen.capacity for gen in self.generators)
        available_conventional = total_capacity - renewable_generation_annual_total
        # Calculate supply-demand balance
        balance = available_conventional - demand_annual_total
        # Simplified price calculation (e.g., based on scarcity)
        if balance >= 0:
            market_price = 50  # Default price if supply meets demand (USD/MWh)
        else:
            market_price = self.params.price_cap # Price cap if demand exceeds supply
        # Placeholder for other metrics
        results.append({
            'timestamp': 'Annual', # Representing annual market clearing
            'demand': demand_annual_total,
            'renewable_generation': renewable_generation_annual_total,
            'market_price': market_price,
            'balance': balance,
            # Add more detailed metrics if needed for an annual model
        })
        return pd.DataFrame(results)
    
    def _get_generator_bids(self, timestamp: pd.Timestamp) -> List[Dict]:
        """Get generator bids for market clearing."""
        bids = []
        
        for name, generator in self.generators.items():
            # Simple bid based on variable cost
            bid = {
                'generator': name,
                'price': generator.variable_cost,
                'quantity': generator.capacity
            }
            bids.append(bid)
        
        return bids
    
    def calculate_market_metrics(self, 
                               market_results: pd.DataFrame) -> Dict:
        """Calculate market performance metrics."""
        # Calculate price statistics
        price_stats = {
            'average_price': market_results['market_price'].mean(),
            'max_price': market_results['market_price'].max(),
            'min_price': market_results['market_price'].min(),
            'price_volatility': market_results['market_price'].std()
        }
        
        # Calculate market efficiency
        total_cost = 0
        for _, row in market_results.iterrows():
            for generator, dispatch in row['dispatch'].items():
                total_cost += (
                    dispatch * 
                    self.generators[generator].variable_cost
                )
        
        # Calculate consumer surplus
        consumer_surplus = (
            market_results['demand'] * 
            (self.params.price_cap - market_results['market_price'])
        ).sum()
        
        # Calculate producer surplus
        producer_surplus = 0
        for _, row in market_results.iterrows():
            for generator, dispatch in row['dispatch'].items():
                producer_surplus += (
                    dispatch * 
                    (row['market_price'] - 
                     self.generators[generator].variable_cost)
                )
        
        return {
            'price_statistics': price_stats,
            'total_cost': total_cost,
            'consumer_surplus': consumer_surplus,
            'producer_surplus': producer_surplus,
            'market_efficiency': (consumer_surplus + producer_surplus) / total_cost
        }
    
    def analyze_market_power(self, 
                           market_results: pd.DataFrame) -> Dict:
        """Analyze market power concentration."""
        # Calculate market shares
        market_shares = {}
        total_generation = 0
        
        for _, row in market_results.iterrows():
            for generator, dispatch in row['dispatch'].items():
                if generator not in market_shares:
                    market_shares[generator] = 0
                market_shares[generator] += dispatch
                total_generation += dispatch
        
        # Calculate HHI (Herfindahl-Hirschman Index)
        hhi = sum(
            (share / total_generation) ** 2 
            for share in market_shares.values()
        )
        
        # Calculate market concentration
        concentration = {
            'hhi': hhi,
            'market_shares': {
                gen: share / total_generation 
                for gen, share in market_shares.items()
            }
        }
        
        return concentration
    
    def optimize_generator_dispatch(self,
                                  demand: pd.Series,
                                  renewable_generation: pd.Series) -> pd.DataFrame:
        """Optimize generator dispatch to meet demand."""
        # Initialize results
        results = []
        
        for timestamp in demand.index:
            # Get demand and renewable generation
            current_demand = demand[timestamp]
            current_renewable = renewable_generation[timestamp]
            
            # Calculate residual demand
            residual_demand = current_demand - current_renewable
            
            # Optimize dispatch
            dispatch = self._optimize_dispatch(residual_demand)
            
            # Calculate costs
            total_cost = sum(
                dispatch[gen] * self.generators[gen].variable_cost
                for gen in dispatch
            )
            
            results.append({
                'timestamp': timestamp,
                'demand': current_demand,
                'renewable_generation': current_renewable,
                'residual_demand': residual_demand,
                'dispatch': dispatch,
                'total_cost': total_cost
            })
        
        return pd.DataFrame(results)
    
    def _optimize_dispatch(self, demand: float) -> Dict[str, float]:
        """Optimize generator dispatch for a given demand."""
        # Simple merit order dispatch
        sorted_generators = sorted(
            self.generators.items(),
            key=lambda x: x[1].variable_cost
        )
        
        dispatch = {}
        remaining_demand = demand
        
        for name, generator in sorted_generators:
            if remaining_demand <= 0:
                dispatch[name] = 0
                continue
            
            dispatch[name] = min(
                generator.capacity,
                remaining_demand
            )
            remaining_demand -= dispatch[name]
        
        return dispatch 