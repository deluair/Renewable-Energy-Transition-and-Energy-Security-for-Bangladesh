"""
Economic model for analyzing costs and investments in the energy transition.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EconomicConfig:
    """Configuration for the economic model."""
    discount_rate: float = 0.08  # 8% discount rate
    inflation_rate: float = 0.05  # 5% inflation rate
    exchange_rate: float = 110.0  # BDT/USD
    carbon_price: float = 50.0  # USD/ton CO2
    fuel_prices: Dict[str, float] = None
    opex_escalation: float = 0.02  # 2% annual escalation
    
    def __post_init__(self):
        if self.fuel_prices is None:
            self.fuel_prices = {
                'natural_gas': 8.0,  # USD/MMBtu
                'coal': 80.0,  # USD/ton
                'oil': 80.0,  # USD/bbl
            }

class EconomicModel:
    """Economic model for energy system analysis."""
    
    def __init__(self, config: EconomicConfig):
        self.config = config
        self.investments = pd.DataFrame()
        self.operational_costs = pd.DataFrame()
        self.revenues = pd.DataFrame()
        self.emissions = pd.DataFrame()
    
    def calculate_capex(self, technology: str, capacity_mw: float, year: int) -> float:
        """Calculate capital expenditure for new capacity."""
        # Base costs from technology database
        base_costs = {
            'solar_pv': 800000,  # USD/MW
            'wind': 1200000,
            'biomass': 2000000,
            'battery_storage': 200000,  # USD/MWh
            'transmission': 500000,  # USD/km
            'distribution': 200000,  # USD/km
        }
        
        # Apply learning curve for renewable technologies
        if technology in ['solar_pv', 'wind', 'battery_storage']:
            learning_rate = 0.2  # 20% cost reduction per doubling of capacity
            years_since_2020 = year - 2020
            cost_reduction = (1 - learning_rate) ** (years_since_2020 / 2)
            base_cost = base_costs[technology] * cost_reduction
        else:
            base_cost = base_costs[technology]
        
        # Apply inflation
        years_since_base = year - 2024
        inflated_cost = base_cost * (1 + self.config.inflation_rate) ** years_since_base
        
        return inflated_cost * capacity_mw
    
    def calculate_opex(self, technology: str, capacity_mw: float, year: int) -> float:
        """Calculate annual operational expenditure."""
        # O&M costs as percentage of capex
        opex_rates = {
            'solar_pv': 0.01,  # 1% of capex
            'wind': 0.015,  # 1.5% of capex
            'biomass': 0.02,  # 2% of capex
            'battery_storage': 0.02,  # 2% of capex
            'transmission': 0.01,
            'distribution': 0.015,
        }
        
        capex = self.calculate_capex(technology, capacity_mw, year)
        base_opex = capex * opex_rates[technology]
        
        # Apply escalation
        years_since_base = year - 2024
        escalated_opex = base_opex * (1 + self.config.opex_escalation) ** years_since_base
        
        return escalated_opex
    
    def calculate_fuel_cost(self, fuel_type: str, amount: float, year: int) -> float:
        """Calculate fuel costs for conventional generation."""
        base_price = self.config.fuel_prices[fuel_type]
        
        # Apply fuel price escalation
        years_since_base = year - 2024
        escalated_price = base_price * (1 + self.config.inflation_rate) ** years_since_base
        
        return escalated_price * amount
    
    def calculate_emissions_cost(self, emissions_tonnes: float) -> float:
        """Calculate carbon cost based on emissions."""
        return emissions_tonnes * self.config.carbon_price
    
    def calculate_lcoe(self, technology: str, capacity_mw: float, 
                      annual_generation_mwh: float, year: int) -> float:
        """Calculate Levelized Cost of Electricity (LCOE)."""
        # Get technology lifetime
        lifetimes = {
            'solar_pv': 25,
            'wind': 20,
            'biomass': 20,
            'battery_storage': 10,
        }
        lifetime = lifetimes[technology]
        
        # Calculate present value of costs
        capex = self.calculate_capex(technology, capacity_mw, year)
        annual_opex = self.calculate_opex(technology, capacity_mw, year)
        
        # Present value of opex
        pv_opex = sum(
            annual_opex / (1 + self.config.discount_rate) ** t
            for t in range(1, lifetime + 1)
        )
        
        # Present value of generation
        pv_generation = sum(
            annual_generation_mwh / (1 + self.config.discount_rate) ** t
            for t in range(1, lifetime + 1)
        )
        
        # Calculate LCOE
        lcoe = (capex + pv_opex) / pv_generation
        
        return lcoe
    
    def calculate_npv(self, cash_flows: List[float], year: int) -> float:
        """Calculate Net Present Value of a series of cash flows."""
        return sum(
            cf / (1 + self.config.discount_rate) ** (t - year)
            for t, cf in enumerate(cash_flows, start=year)
        )
    
    def calculate_irr(self, cash_flows: List[float]) -> float:
        """Calculate Internal Rate of Return."""
        def npv(rate):
            return sum(
                cf / (1 + rate) ** t
                for t, cf in enumerate(cash_flows)
            )
        
        # Use numerical methods to find IRR
        from scipy.optimize import newton
        try:
            return newton(npv, x0=0.1)
        except:
            return None
    
    def calculate_payback_period(self, initial_investment: float, 
                               annual_cash_flows: List[float]) -> float:
        """Calculate payback period in years."""
        cumulative_cash_flow = 0
        for year, cf in enumerate(annual_cash_flows, start=1):
            cumulative_cash_flow += cf
            if cumulative_cash_flow >= initial_investment:
                return year
        return float('inf')
    
    def analyze_investment(self, technology: str, capacity_mw: float, 
                         annual_generation_mwh: float, year: int) -> Dict:
        """Perform comprehensive investment analysis."""
        capex = self.calculate_capex(technology, capacity_mw, year)
        annual_opex = self.calculate_opex(technology, capacity_mw, year)
        lcoe = self.calculate_lcoe(technology, capacity_mw, annual_generation_mwh, year)
        
        # Assume electricity price of 0.12 USD/kWh
        annual_revenue = annual_generation_mwh * 1000 * 0.12
        annual_cash_flow = annual_revenue - annual_opex
        
        # Calculate financial metrics
        lifetimes = {
            'solar_pv': 25,
            'wind': 20,
            'biomass': 20,
            'battery_storage': 10,
        }
        lifetime = lifetimes[technology]
        
        cash_flows = [-capex] + [annual_cash_flow] * lifetime
        npv = self.calculate_npv(cash_flows, year)
        irr = self.calculate_irr(cash_flows)
        payback = self.calculate_payback_period(capex, [annual_cash_flow] * lifetime)
        
        return {
            'capex': capex,
            'annual_opex': annual_opex,
            'lcoe': lcoe,
            'npv': npv,
            'irr': irr,
            'payback_period': payback,
            'annual_revenue': annual_revenue,
            'annual_cash_flow': annual_cash_flow
        }
    
    def calculate_metrics(self, energy_results: Dict) -> Dict:
        """Calculate economic metrics based on energy system results."""
        results = {}
        for year, data in energy_results.items():
            # Calculate investment and operational costs for each technology
            annual_investments = {}
            annual_opex = {}
            annual_lcoe = {}
            for tech, capacity in data['capacity_by_technology'].items():
                # Skip if capacity is zero or tech not in cost database
                if capacity == 0 or tech not in self.config.fuel_prices:
                    continue
                annual_investments[tech] = self.calculate_capex(
                    tech, capacity, year
                )
                annual_opex[tech] = self.calculate_opex(
                    tech, capacity, year
                )
                annual_lcoe[tech] = self.calculate_lcoe(
                    tech, capacity, 
                    data['generation_by_technology'].get(tech, 0),
                    year
                )
            # Store results for the year
            results[year] = {
                'investments': annual_investments,
                'opex': annual_opex,
                'lcoe': annual_lcoe,
                # Add more metrics as needed
            }
        return results 