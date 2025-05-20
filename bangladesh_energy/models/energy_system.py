"""
Core energy system model for Bangladesh's renewable energy transition.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EnergySystemConfig:
    """Configuration for the energy system model."""
    start_year: int = 2024
    end_year: int = 2050
    time_resolution: str = '1H'  # 1-hour resolution
    regions: List[str] = None
    technologies: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.regions is None:
            self.regions = ['Dhaka', 'Chittagong', 'Khulna', 'Rajshahi', 'Sylhet', 'Barishal', 'Rangpur', 'Mymensingh']
        if self.technologies is None:
            self.technologies = {
                'solar_pv': {
                    'capacity_factor': 0.15,  # Average for Bangladesh
                    'cost_per_mw': 800000,  # USD
                    'lifetime': 25,  # years
                    'o&m_cost_percent': 0.01,  # 1% of capital cost
                },
                'wind': {
                    'capacity_factor': 0.25,  # Average for coastal areas
                    'cost_per_mw': 1200000,
                    'lifetime': 20,
                    'o&m_cost_percent': 0.015,
                },
                'biomass': {
                    'capacity_factor': 0.75,
                    'cost_per_mw': 2000000,
                    'lifetime': 20,
                    'o&m_cost_percent': 0.02,
                },
                'battery_storage': {
                    'cost_per_mwh': 200000,
                    'lifetime': 10,
                    'o&m_cost_percent': 0.02,
                    'efficiency': 0.9,
                }
            }

class EnergySystem:
    """Main energy system model class."""
    
    def __init__(self, config: EnergySystemConfig):
        self.config = config
        self.time_index = pd.date_range(
            start=f"{config.start_year}-01-01",
            end=f"{config.end_year}-12-31",
            freq=config.time_resolution
        )
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the energy system with baseline data."""
        # Initialize capacity and generation dataframes
        self.capacity = pd.DataFrame(
            index=self.time_index,
            columns=[f"{tech}_{region}" for tech in self.config.technologies.keys() 
                    for region in self.config.regions]
        )
        self.generation = pd.DataFrame(
            index=self.time_index,
            columns=[f"{tech}_{region}" for tech in self.config.technologies.keys() 
                    for region in self.config.regions]
        )
        self.demand = pd.DataFrame(
            index=self.time_index,
            columns=self.config.regions
        )
        
        # Set initial values
        self.set_initial_capacity()
        self.initialize_demand()
    
    def set_initial_capacity(self):
        """Set initial installed capacity based on 2024 data."""
        # Initial solar capacity (946 MW)
        solar_capacity = 946
        # Distribute across regions based on population and solar potential
        solar_distribution = {
            'Dhaka': 0.15,
            'Chittagong': 0.20,
            'Khulna': 0.15,
            'Rajshahi': 0.15,
            'Sylhet': 0.10,
            'Barishal': 0.10,
            'Rangpur': 0.10,
            'Mymensingh': 0.05
        }
        
        for region, share in solar_distribution.items():
            self.capacity[f"solar_pv_{region}"].iloc[0] = solar_capacity * share
    
    def initialize_demand(self):
        """Initialize electricity demand profiles."""
        # Base demand in MW for each region
        base_demand = {
            'Dhaka': 5000,
            'Chittagong': 2000,
            'Khulna': 1000,
            'Rajshahi': 800,
            'Sylhet': 600,
            'Barishal': 500,
            'Rangpur': 700,
            'Mymensingh': 400
        }
        n_hours = len(self.time_index)
        # Create daily pattern (24 hours)
        daily_pattern = np.sin(np.linspace(0, 2*np.pi, 24, endpoint=False)) * 0.3 + 1
        # Tile daily pattern to match the number of hours in the simulation
        tiled_daily_pattern = np.tile(daily_pattern, n_hours // 24 + 1)[:n_hours]
        # Create seasonal pattern (one value per hour in the year)
        seasonal_pattern = np.sin(np.linspace(0, 2*np.pi, n_hours)) * 0.2 + 1
        for region in self.config.regions:
            base = base_demand[region]
            demand = base * tiled_daily_pattern * seasonal_pattern
            self.demand[region] = demand
    
    def simulate_generation(self, year: int):
        """Simulate generation for a given year."""
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")
        year_mask = (self.time_index >= year_start) & (self.time_index <= year_end)
        
        for tech in self.config.technologies.keys():
            for region in self.config.regions:
                capacity = self.capacity[f"{tech}_{region}"].iloc[year_mask]
                cf = self.config.technologies[tech]['capacity_factor']
                
                # Add some variability to capacity factor
                cf_variation = np.random.normal(0, 0.05, len(capacity))
                effective_cf = np.clip(cf + cf_variation, 0, 1)
                
                self.generation.loc[year_mask, f"{tech}_{region}"] = capacity * effective_cf
    
    def calculate_renewable_share(self, year: int) -> float:
        """Calculate renewable energy share for a given year."""
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")
        year_mask = (self.time_index >= year_start) & (self.time_index <= year_end)
        
        renewable_generation = self.generation.loc[year_mask, 
            [col for col in self.generation.columns if any(tech in col 
             for tech in ['solar_pv', 'wind', 'biomass'])]].sum().sum()
        
        total_generation = self.generation.loc[year_mask].sum().sum()
        
        return renewable_generation / total_generation if total_generation > 0 else 0
    
    def add_capacity(self, technology: str, region: str, capacity_mw: float, year: int):
        """Add new capacity for a specific technology and region."""
        year_start = pd.Timestamp(f"{year}-01-01")
        year_mask = self.time_index >= year_start
        
        current_capacity = self.capacity[f"{technology}_{region}"].iloc[0]
        self.capacity.loc[year_mask, f"{technology}_{region}"] = current_capacity + capacity_mw
    
    def get_system_summary(self, year: int) -> Dict:
        """Get summary statistics for the energy system in a given year."""
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")
        year_mask = (self.time_index >= year_start) & (self.time_index <= year_end)
        # Group by technology using columns
        capacity_by_tech = self.capacity.loc[year_end]
        capacity_by_technology = capacity_by_tech.groupby(lambda x: x.split('_')[0]).sum().to_dict()
        generation_by_tech = self.generation.loc[year_mask].sum()
        generation_by_technology = generation_by_tech.groupby(lambda x: x.split('_')[0]).sum().to_dict()
        return {
            'total_capacity': self.capacity.loc[year_mask].sum().sum(),
            'total_generation': self.generation.loc[year_mask].sum().sum(),
            'total_demand': self.demand.loc[year_mask].sum().sum(),
            'renewable_share': self.calculate_renewable_share(year),
            'capacity_by_technology': capacity_by_technology,
            'generation_by_technology': generation_by_technology
        }

    def simulate(self):
        """Simulate the energy system for all years and return annual summaries."""
        results = {}
        for year in range(self.config.start_year, self.config.end_year + 1):
            self.simulate_generation(year)
            summary = self.get_system_summary(year)
            results[year] = summary
        return results 