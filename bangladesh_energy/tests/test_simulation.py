"""
Test cases for the Bangladesh Energy Transition simulation.
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime

from models.energy_system import EnergySystem, EnergySystemConfig
from models.economic_model import EconomicModel, EconomicConfig
from models.environmental_model import EnvironmentalModel, EnvironmentalConfig
from utils.helpers import (
    calculate_hourly_demand,
    calculate_capacity_factor,
    calculate_emissions,
    calculate_water_use,
    calculate_land_use,
    calculate_lcoe,
    calculate_employment,
    calculate_community_benefits
)

class TestEnergySystem(unittest.TestCase):
    """Test cases for the energy system model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = EnergySystemConfig()
        self.energy_system = EnergySystem(self.config)
    
    def test_initial_capacity(self):
        """Test initial capacity setup."""
        self.assertGreater(len(self.energy_system.capacity), 0)
        self.assertGreater(sum(self.energy_system.capacity.values()), 0)
    
    def test_generation_simulation(self):
        """Test generation simulation."""
        year = 2024
        self.energy_system.simulate_generation(year)
        self.assertGreater(len(self.energy_system.generation), 0)
        self.assertGreater(sum(self.energy_system.generation.values()), 0)
    
    def test_renewable_share(self):
        """Test renewable share calculation."""
        year = 2024
        share = self.energy_system.calculate_renewable_share(year)
        self.assertGreaterEqual(share, 0)
        self.assertLessEqual(share, 1)

class TestEconomicModel(unittest.TestCase):
    """Test cases for the economic model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = EconomicConfig()
        self.economic_model = EconomicModel(self.config)
    
    def test_capex_calculation(self):
        """Test capital expenditure calculation."""
        tech = 'solar_pv'
        capacity = 1000  # kW
        capex = self.economic_model.calculate_capex(tech, capacity)
        self.assertGreater(capex, 0)
    
    def test_opex_calculation(self):
        """Test operational expenditure calculation."""
        tech = 'solar_pv'
        capacity = 1000  # kW
        opex = self.economic_model.calculate_opex(tech, capacity)
        self.assertGreater(opex, 0)
    
    def test_lcoe_calculation(self):
        """Test LCOE calculation."""
        tech = 'solar_pv'
        capacity = 1000  # kW
        generation = 1500  # MWh
        year = 2024
        lcoe = self.economic_model.calculate_lcoe(tech, capacity, generation, year)
        self.assertGreater(lcoe, 0)

class TestEnvironmentalModel(unittest.TestCase):
    """Test cases for the environmental model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = EnvironmentalConfig()
        self.environmental_model = EnvironmentalModel(self.config)
    
    def test_emissions_calculation(self):
        """Test emissions calculation."""
        tech = 'natural_gas'
        generation = 1000  # MWh
        emissions = self.environmental_model.calculate_emissions(tech, generation)
        self.assertGreater(emissions, 0)
    
    def test_water_use_calculation(self):
        """Test water use calculation."""
        tech = 'coal'
        generation = 1000  # MWh
        water_use = self.environmental_model.calculate_water_use(tech, generation)
        self.assertGreater(water_use, 0)
    
    def test_land_use_calculation(self):
        """Test land use calculation."""
        tech = 'solar_pv'
        capacity = 1000  # kW
        land_use = self.environmental_model.calculate_land_use(tech, capacity)
        self.assertGreater(land_use, 0)

class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""
    
    def test_hourly_demand(self):
        """Test hourly demand calculation."""
        base_load = 1000  # MW
        peak_load = 1500  # MW
        daily_variation = 0.2
        seasonal_variation = 0.15
        year = 2024
        
        demand = calculate_hourly_demand(
            base_load, peak_load, daily_variation, seasonal_variation, year
        )
        
        self.assertEqual(len(demand), 8760)  # Hours in a year
        self.assertTrue(np.all(demand >= 0))
        self.assertTrue(np.all(demand <= peak_load * (1 + 0.06) ** (year - 2024)))
    
    def test_capacity_factor(self):
        """Test capacity factor calculation."""
        tech = 'solar_pv'
        location = 'Dhaka'
        month = 6
        hour = 12
        
        cf = calculate_capacity_factor(tech, location, month, hour)
        self.assertGreaterEqual(cf, 0)
        self.assertLessEqual(cf, 1)
    
    def test_emissions_calculation(self):
        """Test emissions calculation."""
        tech = 'coal'
        generation = 1000  # MWh
        emission_factors = {'coal': 0.8}  # tCO2/MWh
        
        emissions = calculate_emissions(tech, generation, emission_factors)
        self.assertEqual(emissions, 800)  # 1000 MWh * 0.8 tCO2/MWh
    
    def test_water_use_calculation(self):
        """Test water use calculation."""
        tech = 'coal'
        generation = 1000  # MWh
        water_factors = {'coal': 2.0}  # m³/MWh
        
        water_use = calculate_water_use(tech, generation, water_factors)
        self.assertEqual(water_use, 2000)  # 1000 MWh * 2.0 m³/MWh
    
    def test_land_use_calculation(self):
        """Test land use calculation."""
        tech = 'solar_pv'
        capacity = 1000  # kW
        land_use_factors = {'solar_pv': 2.5}  # m²/kW
        
        land_use = calculate_land_use(tech, capacity, land_use_factors)
        self.assertEqual(land_use, 2500)  # 1000 kW * 2.5 m²/kW
    
    def test_lcoe_calculation(self):
        """Test LCOE calculation."""
        capex = 1000  # USD/kW
        opex = 20  # USD/kW/year
        capacity_factor = 0.2
        lifetime = 25
        discount_rate = 0.08
        
        lcoe = calculate_lcoe(capex, opex, capacity_factor, lifetime, discount_rate)
        self.assertGreater(lcoe, 0)
    
    def test_employment_calculation(self):
        """Test employment calculation."""
        tech = 'solar_pv'
        capacity = 100  # MW
        employment_factors = {'solar_pv': 0.5}  # jobs/MW
        
        jobs = calculate_employment(tech, capacity, employment_factors)
        self.assertEqual(jobs, 50)  # 100 MW * 0.5 jobs/MW
    
    def test_community_benefits_calculation(self):
        """Test community benefits calculation."""
        tech = 'solar_pv'
        revenue = 1000000  # USD
        community_benefits = {'solar_pv': 0.02}  # 2% of revenue
        
        benefits = calculate_community_benefits(tech, revenue, community_benefits)
        self.assertEqual(benefits, 20000)  # 1000000 USD * 0.02

if __name__ == '__main__':
    unittest.main() 