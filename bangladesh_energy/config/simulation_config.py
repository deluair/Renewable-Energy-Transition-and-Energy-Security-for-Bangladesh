"""
Configuration parameters for the Bangladesh Energy Transition simulation.
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SimulationConfig:
    """Main configuration class for the simulation."""
    
    # Simulation period
    START_YEAR: int = 2024
    END_YEAR: int = 2050
    
    # Renewable energy targets
    RENEWABLE_TARGETS: Dict[int, float] = {
        2030: 0.15,  # 15% by 2030
        2041: 0.40,  # 40% by 2041
        2050: 1.00   # 100% by 2050
    }
    
    # Technology parameters
    TECHNOLOGIES: Dict[str, Dict] = {
        'solar_pv': {
            'capacity_factor': 0.18,
            'capex': 800,  # USD/kW
            'opex': 15,    # USD/kW/year
            'lifetime': 25,
            'land_use': 2.5,  # m²/kW
            'water_use': 0.0,  # m³/MWh
            'emission_factor': 0.0  # tCO2/MWh
        },
        'wind': {
            'capacity_factor': 0.25,
            'capex': 1200,  # USD/kW
            'opex': 30,     # USD/kW/year
            'lifetime': 20,
            'land_use': 0.5,  # m²/kW
            'water_use': 0.0,  # m³/MWh
            'emission_factor': 0.0  # tCO2/MWh
        },
        'biomass': {
            'capacity_factor': 0.70,
            'capex': 2500,  # USD/kW
            'opex': 100,    # USD/kW/year
            'lifetime': 20,
            'land_use': 0.1,  # m²/kW
            'water_use': 1.5,  # m³/MWh
            'emission_factor': 0.0  # tCO2/MWh
        },
        'natural_gas': {
            'capacity_factor': 0.85,
            'capex': 1000,  # USD/kW
            'opex': 50,     # USD/kW/year
            'lifetime': 25,
            'land_use': 0.05,  # m²/kW
            'water_use': 1.0,  # m³/MWh
            'emission_factor': 0.4  # tCO2/MWh
        },
        'coal': {
            'capacity_factor': 0.80,
            'capex': 2000,  # USD/kW
            'opex': 80,     # USD/kW/year
            'lifetime': 30,
            'land_use': 0.1,  # m²/kW
            'water_use': 2.0,  # m³/MWh
            'emission_factor': 0.8  # tCO2/MWh
        }
    }
    
    # Economic parameters
    ECONOMIC_PARAMS: Dict = {
        'discount_rate': 0.08,  # 8%
        'inflation_rate': 0.05,  # 5%
        'exchange_rate': 110.0,  # BDT/USD
        'carbon_price': 50.0,    # USD/ton CO2
        'fuel_prices': {
            'natural_gas': 5.0,  # USD/MMBtu
            'coal': 60.0,        # USD/ton
            'oil': 80.0          # USD/bbl
        },
        'opex_escalation': 0.02  # 2% annual escalation
    }
    
    # Environmental parameters
    ENVIRONMENTAL_PARAMS: Dict = {
        'emission_factors': {
            'natural_gas': 0.4,  # tCO2/MWh
            'coal': 0.8,         # tCO2/MWh
            'oil': 0.6,          # tCO2/MWh
            'biomass': 0.0,      # tCO2/MWh (carbon neutral)
            'solar_pv': 0.0,     # tCO2/MWh
            'wind': 0.0          # tCO2/MWh
        },
        'water_factors': {
            'natural_gas': 1.0,  # m³/MWh
            'coal': 2.0,         # m³/MWh
            'oil': 1.5,          # m³/MWh
            'biomass': 1.5,      # m³/MWh
            'solar_pv': 0.0,     # m³/MWh
            'wind': 0.0          # m³/MWh
        },
        'land_use_factors': {
            'natural_gas': 0.05,  # m²/kW
            'coal': 0.1,          # m²/kW
            'oil': 0.08,          # m²/kW
            'biomass': 0.1,       # m²/kW
            'solar_pv': 2.5,      # m²/kW
            'wind': 0.5           # m²/kW
        }
    }
    
    # Grid parameters
    GRID_PARAMS: Dict = {
        'transmission_loss': 0.05,  # 5% transmission loss
        'distribution_loss': 0.08,  # 8% distribution loss
        'grid_capacity_factor': 0.85,
        'grid_capex': 500,  # USD/kW
        'grid_opex': 20,    # USD/kW/year
        'grid_lifetime': 40
    }
    
    # Storage parameters
    STORAGE_PARAMS: Dict = {
        'battery': {
            'capacity_factor': 0.90,
            'capex': 300,  # USD/kWh
            'opex': 10,    # USD/kWh/year
            'lifetime': 10,
            'efficiency': 0.85
        },
        'pumped_hydro': {
            'capacity_factor': 0.85,
            'capex': 2000,  # USD/kW
            'opex': 30,     # USD/kW/year
            'lifetime': 50,
            'efficiency': 0.80
        }
    }
    
    # Demand parameters
    DEMAND_PARAMS: Dict = {
        'base_load': 12000,  # MW
        'peak_load': 18000,  # MW
        'annual_growth': 0.06,  # 6% annual growth
        'daily_variation': 0.2,  # 20% daily variation
        'seasonal_variation': 0.15  # 15% seasonal variation
    }
    
    # Policy parameters
    POLICY_PARAMS: Dict = {
        'renewable_incentives': {
            'solar_pv': 0.10,  # 10% subsidy
            'wind': 0.15,      # 15% subsidy
            'biomass': 0.20    # 20% subsidy
        },
        'carbon_tax': {
            'start_year': 2025,
            'initial_rate': 20.0,  # USD/ton CO2
            'annual_increase': 0.05  # 5% annual increase
        },
        'grid_connection_fee': 1000,  # USD/kW
        'feed_in_tariff': {
            'solar_pv': 0.12,  # USD/kWh
            'wind': 0.10,      # USD/kWh
            'biomass': 0.08    # USD/kWh
        }
    }
    
    # Social parameters
    SOCIAL_PARAMS: Dict = {
        'employment_factors': {
            'solar_pv': 0.5,    # jobs/MW
            'wind': 0.3,        # jobs/MW
            'biomass': 1.0,     # jobs/MW
            'natural_gas': 0.2,  # jobs/MW
            'coal': 0.4         # jobs/MW
        },
        'community_benefits': {
            'solar_pv': 0.02,  # 2% of revenue
            'wind': 0.02,      # 2% of revenue
            'biomass': 0.05    # 5% of revenue
        }
    } 