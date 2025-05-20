"""
Utility functions for the Bangladesh Energy Transition simulation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

def calculate_hourly_demand(
    base_load: float,
    peak_load: float,
    daily_variation: float,
    seasonal_variation: float,
    year: int,
    start_year: int = 2024
) -> np.ndarray:
    """
    Calculate hourly electricity demand for a given year.
    
    Args:
        base_load: Base load in MW
        peak_load: Peak load in MW
        daily_variation: Daily load variation factor
        seasonal_variation: Seasonal load variation factor
        year: Year to calculate demand for
        start_year: Base year for growth calculations
    
    Returns:
        Array of hourly demand values for the year
    """
    # Calculate annual growth
    years_growth = year - start_year
    annual_growth_factor = (1 + 0.06) ** years_growth  # 6% annual growth
    
    # Generate hourly timestamps for the year
    hours = pd.date_range(
        start=f'{year}-01-01',
        end=f'{year}-12-31 23:00:00',
        freq='H'
    )
    
    # Calculate base demand with growth
    base_demand = base_load * annual_growth_factor
    
    # Calculate daily pattern (higher during day, lower at night)
    daily_pattern = np.sin(np.pi * hours.hour / 12) * daily_variation + 1
    
    # Calculate seasonal pattern (higher in summer, lower in winter)
    seasonal_pattern = np.sin(2 * np.pi * (hours.dayofyear - 182) / 365) * seasonal_variation + 1
    
    # Combine patterns
    demand = base_demand * daily_pattern * seasonal_pattern
    
    # Ensure demand doesn't exceed peak load
    peak_demand = peak_load * annual_growth_factor
    demand = np.minimum(demand, peak_demand)
    
    return demand

def calculate_capacity_factor(
    technology: str,
    location: str,
    month: int,
    hour: int
) -> float:
    """
    Calculate capacity factor for a technology at a specific location and time.
    
    Args:
        technology: Energy technology type
        location: Geographic location
        month: Month of the year (1-12)
        hour: Hour of the day (0-23)
    
    Returns:
        Capacity factor (0-1)
    """
    # Base capacity factors from configuration
    base_factors = {
        'solar_pv': 0.18,
        'wind': 0.25,
        'biomass': 0.70,
        'natural_gas': 0.85,
        'coal': 0.80
    }
    
    base_factor = base_factors.get(technology, 0.0)
    
    # Apply time-based variations
    if technology == 'solar_pv':
        # Solar variation based on time of day and month
        solar_angle = np.pi * (hour - 12) / 12
        monthly_factor = np.sin(np.pi * (month - 6) / 6) * 0.2 + 0.8
        return base_factor * np.cos(solar_angle) ** 2 * monthly_factor
    
    elif technology == 'wind':
        # Wind variation based on month (higher in monsoon)
        monsoon_factor = np.sin(np.pi * (month - 6) / 6) * 0.3 + 0.7
        return base_factor * monsoon_factor
    
    else:
        # Other technologies have constant capacity factors
        return base_factor

def calculate_emissions(
    technology: str,
    generation: float,
    emission_factors: Dict[str, float]
) -> float:
    """
    Calculate CO2 emissions for electricity generation.
    
    Args:
        technology: Energy technology type
        generation: Electricity generation in MWh
        emission_factors: Dictionary of emission factors by technology
    
    Returns:
        CO2 emissions in tons
    """
    return generation * emission_factors.get(technology, 0.0)

def calculate_water_use(
    technology: str,
    generation: float,
    water_factors: Dict[str, float]
) -> float:
    """
    Calculate water use for electricity generation.
    
    Args:
        technology: Energy technology type
        generation: Electricity generation in MWh
        water_factors: Dictionary of water use factors by technology
    
    Returns:
        Water use in cubic meters
    """
    return generation * water_factors.get(technology, 0.0)

def calculate_land_use(
    technology: str,
    capacity: float,
    land_use_factors: Dict[str, float]
) -> float:
    """
    Calculate land use for energy infrastructure.
    
    Args:
        technology: Energy technology type
        capacity: Installed capacity in kW
        land_use_factors: Dictionary of land use factors by technology
    
    Returns:
        Land use in square meters
    """
    return capacity * land_use_factors.get(technology, 0.0)

def calculate_lcoe(
    capex: float,
    opex: float,
    capacity_factor: float,
    lifetime: int,
    discount_rate: float
) -> float:
    """
    Calculate Levelized Cost of Electricity (LCOE).
    
    Args:
        capex: Capital expenditure in USD/kW
        opex: Annual operational expenditure in USD/kW
        capacity_factor: Annual capacity factor
        lifetime: Project lifetime in years
        discount_rate: Annual discount rate
    
    Returns:
        LCOE in USD/kWh
    """
    # Annual generation
    annual_generation = 8760 * capacity_factor  # kWh/kW
    
    # Present value of capital costs
    pv_capex = capex
    
    # Present value of operational costs
    pv_opex = opex * (1 - (1 + discount_rate) ** -lifetime) / discount_rate
    
    # Total present value of costs
    total_pv_cost = pv_capex + pv_opex
    
    # Total present value of generation
    total_pv_generation = annual_generation * (1 - (1 + discount_rate) ** -lifetime) / discount_rate
    
    # LCOE
    return total_pv_cost / total_pv_generation

def calculate_employment(
    technology: str,
    capacity: float,
    employment_factors: Dict[str, float]
) -> float:
    """
    Calculate direct employment from energy projects.
    
    Args:
        technology: Energy technology type
        capacity: Installed capacity in MW
        employment_factors: Dictionary of employment factors by technology
    
    Returns:
        Number of jobs created
    """
    return capacity * employment_factors.get(technology, 0.0)

def calculate_community_benefits(
    technology: str,
    revenue: float,
    community_benefits: Dict[str, float]
) -> float:
    """
    Calculate community benefits from energy projects.
    
    Args:
        technology: Energy technology type
        revenue: Annual revenue in USD
        community_benefits: Dictionary of community benefit factors by technology
    
    Returns:
        Community benefits in USD
    """
    return revenue * community_benefits.get(technology, 0.0)

def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return f"{value * 100:.1f}%"

def format_power(value: float) -> str:
    """Format a number as power capacity."""
    if value >= 1e6:
        return f"{value/1e6:.1f} GW"
    elif value >= 1e3:
        return f"{value/1e3:.1f} MW"
    else:
        return f"{value:.1f} kW"

def format_energy(value: float) -> str:
    """Format a number as energy."""
    if value >= 1e9:
        return f"{value/1e9:.1f} TWh"
    elif value >= 1e6:
        return f"{value/1e6:.1f} GWh"
    elif value >= 1e3:
        return f"{value/1e3:.1f} MWh"
    else:
        return f"{value:.1f} kWh" 