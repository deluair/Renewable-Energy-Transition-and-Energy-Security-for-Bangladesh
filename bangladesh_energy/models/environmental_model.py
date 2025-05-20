"""
Environmental model for tracking emissions and environmental impacts.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EnvironmentalConfig:
    """Configuration for the environmental model."""
    # Emission factors (kg CO2e per unit)
    emission_factors: Dict[str, float] = None
    # Water consumption factors (m3 per MWh)
    water_factors: Dict[str, float] = None
    # Land use factors (m2 per MW)
    land_use_factors: Dict[str, float] = None
    
    def __post_init__(self):
        if self.emission_factors is None:
            self.emission_factors = {
                'natural_gas': 0.5,  # kg CO2e/kWh
                'coal': 1.0,
                'oil': 0.8,
                'biomass': 0.1,  # Assuming sustainable biomass
                'solar_pv': 0.05,  # Lifecycle emissions
                'wind': 0.02,
                'battery_storage': 0.1,
            }
        
        if self.water_factors is None:
            self.water_factors = {
                'natural_gas': 0.5,  # m3/MWh
                'coal': 1.5,
                'oil': 0.8,
                'biomass': 0.3,
                'solar_pv': 0.1,
                'wind': 0.0,
                'battery_storage': 0.0,
            }
        
        if self.land_use_factors is None:
            self.land_use_factors = {
                'solar_pv': 2000,  # m2/MW
                'wind': 5000,
                'biomass': 1000,
                'battery_storage': 100,
            }

class EnvironmentalModel:
    """Environmental impact assessment model."""
    
    def __init__(self, config: EnvironmentalConfig):
        self.config = config
        self.emissions = pd.DataFrame()
        self.water_use = pd.DataFrame()
        self.land_use = pd.DataFrame()
    
    def calculate_emissions(self, technology: str, generation_mwh: float) -> float:
        """Calculate CO2 emissions for electricity generation."""
        if technology in self.config.emission_factors:
            return generation_mwh * 1000 * self.config.emission_factors[technology]
        return 0.0
    
    def calculate_water_use(self, technology: str, generation_mwh: float) -> float:
        """Calculate water consumption for electricity generation."""
        if technology in self.config.water_factors:
            return generation_mwh * self.config.water_factors[technology]
        return 0.0
    
    def calculate_land_use(self, technology: str, capacity_mw: float) -> float:
        """Calculate land use for power generation capacity."""
        if technology in self.config.land_use_factors:
            return capacity_mw * self.config.land_use_factors[technology]
        return 0.0
    
    def calculate_air_pollutants(self, technology: str, generation_mwh: float) -> Dict[str, float]:
        """Calculate air pollutant emissions."""
        # Emission factors for air pollutants (kg/MWh)
        pollutant_factors = {
            'natural_gas': {
                'SO2': 0.001,
                'NOx': 0.5,
                'PM2.5': 0.01,
            },
            'coal': {
                'SO2': 2.0,
                'NOx': 1.5,
                'PM2.5': 0.5,
            },
            'oil': {
                'SO2': 1.0,
                'NOx': 1.0,
                'PM2.5': 0.1,
            },
            'biomass': {
                'SO2': 0.1,
                'NOx': 0.8,
                'PM2.5': 0.2,
            }
        }
        
        if technology in pollutant_factors:
            return {
                pollutant: generation_mwh * factor
                for pollutant, factor in pollutant_factors[technology].items()
            }
        return {'SO2': 0.0, 'NOx': 0.0, 'PM2.5': 0.0}
    
    def calculate_health_impacts(self, air_pollutants: Dict[str, float]) -> Dict[str, float]:
        """Calculate health impacts from air pollution."""
        # Health impact factors (premature deaths per ton of pollutant)
        health_factors = {
            'PM2.5': 0.1,  # deaths per ton
            'SO2': 0.05,
            'NOx': 0.03,
        }
        
        return {
            pollutant: emissions * factor
            for pollutant, emissions in air_pollutants.items()
            if pollutant in health_factors
        }
    
    def calculate_biodiversity_impact(self, land_use: float, 
                                    land_type: str) -> Dict[str, float]:
        """Calculate biodiversity impact of land use change."""
        # Biodiversity impact factors (species affected per hectare)
        impact_factors = {
            'forest': 10.0,
            'agriculture': 5.0,
            'grassland': 7.0,
            'wetland': 15.0,
            'urban': 2.0,
        }
        
        if land_type in impact_factors:
            return {
                'species_affected': land_use * impact_factors[land_type] / 10000,  # Convert m2 to ha
                'habitat_loss': land_use / 10000,  # hectares
            }
        return {'species_affected': 0.0, 'habitat_loss': 0.0}
    
    def calculate_water_quality_impact(self, technology: str, 
                                     water_use: float) -> Dict[str, float]:
        """Calculate water quality impacts."""
        # Water quality impact factors
        quality_factors = {
            'natural_gas': {
                'thermal_pollution': 0.3,
                'chemical_pollution': 0.1,
            },
            'coal': {
                'thermal_pollution': 0.5,
                'chemical_pollution': 0.8,
            },
            'oil': {
                'thermal_pollution': 0.4,
                'chemical_pollution': 0.6,
            },
            'biomass': {
                'thermal_pollution': 0.2,
                'chemical_pollution': 0.3,
            }
        }
        
        if technology in quality_factors:
            return {
                impact_type: water_use * factor
                for impact_type, factor in quality_factors[technology].items()
            }
        return {'thermal_pollution': 0.0, 'chemical_pollution': 0.0}
    
    def calculate_waste_generation(self, technology: str, 
                                 capacity_mw: float) -> Dict[str, float]:
        """Calculate waste generation from power plants."""
        # Waste generation factors (tons per MW per year)
        waste_factors = {
            'coal': {
                'ash': 100,
                'sludge': 10,
                'hazardous': 1,
            },
            'biomass': {
                'ash': 50,
                'sludge': 5,
                'hazardous': 0.5,
            },
            'solar_pv': {
                'electronic_waste': 0.1,
                'hazardous': 0.01,
            },
            'battery_storage': {
                'electronic_waste': 0.2,
                'hazardous': 0.05,
            }
        }
        
        if technology in waste_factors:
            return {
                waste_type: capacity_mw * amount
                for waste_type, amount in waste_factors[technology].items()
            }
        return {}
    
    def calculate_circular_economy_potential(self, technology: str, 
                                          capacity_mw: float) -> Dict[str, float]:
        """Calculate potential for circular economy practices."""
        # Circular economy potential factors
        circular_factors = {
            'solar_pv': {
                'recyclable_materials': 0.85,  # % of materials
                'reusable_components': 0.60,
                'energy_recovery': 0.10,
            },
            'wind': {
                'recyclable_materials': 0.90,
                'reusable_components': 0.70,
                'energy_recovery': 0.05,
            },
            'battery_storage': {
                'recyclable_materials': 0.70,
                'reusable_components': 0.50,
                'energy_recovery': 0.20,
            }
        }
        
        if technology in circular_factors:
            return {
                metric: capacity_mw * factor
                for metric, factor in circular_factors[technology].items()
            }
        return {}
    
    def calculate_environmental_benefits(self, renewable_generation_mwh: float) -> Dict[str, float]:
        """Calculate environmental benefits of renewable energy."""
        # Assume displacement of natural gas generation
        displaced_emissions = self.calculate_emissions('natural_gas', renewable_generation_mwh)
        displaced_water = self.calculate_water_use('natural_gas', renewable_generation_mwh)
        displaced_air_pollutants = self.calculate_air_pollutants('natural_gas', renewable_generation_mwh)
        
        return {
            'emissions_avoided': displaced_emissions,
            'water_saved': displaced_water,
            'air_pollution_avoided': displaced_air_pollutants,
            'health_benefits': self.calculate_health_impacts(displaced_air_pollutants)
        }
    
    def calculate_environmental_impact_score(self, impacts: Dict[str, float]) -> float:
        """Calculate overall environmental impact score."""
        # Weight factors for different impacts
        weights = {
            'emissions': 0.4,
            'water_use': 0.2,
            'land_use': 0.2,
            'air_pollution': 0.1,
            'waste': 0.1,
        }
        
        # Normalize and weight impacts
        normalized_impacts = {
            'emissions': impacts.get('emissions', 0) / 1000,  # Normalize to tons
            'water_use': impacts.get('water_use', 0) / 1000,  # Normalize to 1000 m3
            'land_use': impacts.get('land_use', 0) / 10000,  # Normalize to hectares
            'air_pollution': sum(impacts.get('air_pollutants', {}).values()) / 1000,
            'waste': sum(impacts.get('waste', {}).values()) / 1000,
        }
        
        # Calculate weighted score
        score = sum(
            normalized_impacts[impact] * weight
            for impact, weight in weights.items()
        )
        
        return score 