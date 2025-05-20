"""
Script to run the Bangladesh Energy Transition simulation with different scenarios.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bangladesh_energy.models.energy_system import EnergySystem, EnergySystemConfig
from bangladesh_energy.models.economic_model import EconomicModel, EconomicConfig
from bangladesh_energy.models.environmental_model import EnvironmentalModel, EnvironmentalConfig
from bangladesh_energy.config.simulation_config import SimulationConfig
from bangladesh_energy.utils.helpers import (
    format_currency,
    format_percentage,
    format_power,
    format_energy
)

class Scenario:
    """Base class for simulation scenarios."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.config = SimulationConfig()
    
    def modify_config(self):
        """Modify configuration for this scenario."""
        pass
    
    def run(self) -> pd.DataFrame:
        """Run the scenario simulation."""
        # Initialize models with modified config
        self.modify_config()
        energy_system = EnergySystem(EnergySystemConfig())
        economic_model = EconomicModel(EconomicConfig())
        environmental_model = EnvironmentalModel(EnvironmentalConfig())
        
        # Initialize results storage
        results = {
            'year': [],
            'renewable_share': [],
            'total_capacity': [],
            'total_generation': [],
            'emissions': [],
            'investment': [],
            'lcoe': [],
            'water_use': [],
            'land_use': [],
            'employment': []
        }
        
        # Run simulation for each year
        for year in range(self.config.START_YEAR, self.config.END_YEAR + 1):
            # Simulate energy system
            energy_system.simulate_generation(year)
            system_summary = energy_system.get_system_summary(year)
            
            # Calculate metrics
            renewable_share = energy_system.calculate_renewable_share(year)
            
            # Calculate economic metrics
            total_investment = 0
            total_lcoe = 0
            tech_count = 0
            
            for tech, capacity in system_summary['capacity_by_technology'].items():
                if capacity > 0:
                    generation = system_summary['generation_by_technology'].get(tech, 0)
                    investment = economic_model.analyze_investment(tech, capacity, generation, year)
                    total_investment += investment['capex']
                    total_lcoe += investment['lcoe']
                    tech_count += 1
            
            avg_lcoe = total_lcoe / tech_count if tech_count > 0 else 0
            
            # Calculate environmental impacts
            total_emissions = 0
            total_water_use = 0
            total_land_use = 0
            
            for tech, generation in system_summary['generation_by_technology'].items():
                capacity = system_summary['capacity_by_technology'].get(tech, 0)
                total_emissions += environmental_model.calculate_emissions(tech, generation)
                total_water_use += environmental_model.calculate_water_use(tech, generation)
                total_land_use += environmental_model.calculate_land_use(tech, capacity)
            
            # Calculate employment
            total_employment = 0
            for tech, capacity in system_summary['capacity_by_technology'].items():
                if capacity > 0:
                    total_employment += calculate_employment(
                        tech, capacity / 1000,  # Convert to MW
                        self.config.SOCIAL_PARAMS['employment_factors']
                    )
            
            # Store results
            results['year'].append(year)
            results['renewable_share'].append(renewable_share)
            results['total_capacity'].append(sum(system_summary['capacity_by_technology'].values()))
            results['total_generation'].append(sum(system_summary['generation_by_technology'].values()))
            results['emissions'].append(total_emissions)
            results['investment'].append(total_investment)
            results['lcoe'].append(avg_lcoe)
            results['water_use'].append(total_water_use)
            results['land_use'].append(total_land_use)
            results['employment'].append(total_employment)
        
        return pd.DataFrame(results)

class BaselineScenario(Scenario):
    """Baseline scenario with current policies and trends."""
    
    def __init__(self):
        super().__init__(
            name="Baseline",
            description="Current policies and trends continue"
        )
    
    def modify_config(self):
        """Modify configuration for baseline scenario."""
        # No modifications needed for baseline
        pass

class AcceleratedTransitionScenario(Scenario):
    """Scenario with accelerated renewable energy transition."""
    
    def __init__(self):
        super().__init__(
            name="Accelerated Transition",
            description="Accelerated deployment of renewable energy"
        )
    
    def modify_config(self):
        """Modify configuration for accelerated transition scenario."""
        # Increase renewable energy targets
        self.config.RENEWABLE_TARGETS = {
            2030: 0.25,  # 25% by 2030
            2041: 0.60,  # 60% by 2041
            2050: 1.00   # 100% by 2050
        }
        
        # Reduce renewable energy costs
        for tech in ['solar_pv', 'wind', 'biomass']:
            self.config.TECHNOLOGIES[tech]['capex'] *= 0.8  # 20% reduction
            self.config.TECHNOLOGIES[tech]['opex'] *= 0.8  # 20% reduction
        
        # Increase renewable incentives
        for tech in self.config.POLICY_PARAMS['renewable_incentives']:
            self.config.POLICY_PARAMS['renewable_incentives'][tech] *= 1.5  # 50% increase

class DelayedTransitionScenario(Scenario):
    """Scenario with delayed renewable energy transition."""
    
    def __init__(self):
        super().__init__(
            name="Delayed Transition",
            description="Slower deployment of renewable energy"
        )
    
    def modify_config(self):
        """Modify configuration for delayed transition scenario."""
        # Decrease renewable energy targets
        self.config.RENEWABLE_TARGETS = {
            2030: 0.10,  # 10% by 2030
            2041: 0.30,  # 30% by 2041
            2050: 0.80   # 80% by 2050
        }
        
        # Increase renewable energy costs
        for tech in ['solar_pv', 'wind', 'biomass']:
            self.config.TECHNOLOGIES[tech]['capex'] *= 1.2  # 20% increase
            self.config.TECHNOLOGIES[tech]['opex'] *= 1.2  # 20% increase
        
        # Decrease renewable incentives
        for tech in self.config.POLICY_PARAMS['renewable_incentives']:
            self.config.POLICY_PARAMS['renewable_incentives'][tech] *= 0.8  # 20% decrease

def run_scenarios():
    """Run all scenarios and compare results."""
    print("Running Bangladesh Energy Transition Scenarios...")
    
    # Define scenarios
    scenarios = [
        BaselineScenario(),
        AcceleratedTransitionScenario(),
        DelayedTransitionScenario()
    ]
    
    # Run each scenario
    results = {}
    for scenario in scenarios:
        print(f"\nRunning {scenario.name} scenario...")
        print(f"Description: {scenario.description}")
        results[scenario.name] = scenario.run()
    
    # Generate comparison plots
    generate_comparison_plots(results)
    
    # Generate comparison report
    generate_comparison_report(results)
    
    print("\nScenario analysis complete!")

def generate_comparison_plots(results: Dict[str, pd.DataFrame]):
    """Generate comparison plots for all scenarios."""
    # Set style
    plt.style.use('seaborn')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    fig.suptitle('Bangladesh Energy Transition Scenario Comparison')
    
    # Plot renewable share
    for scenario_name, df in results.items():
        axes[0, 0].plot(df['year'], df['renewable_share'] * 100, label=scenario_name)
    axes[0, 0].set_title('Renewable Energy Share')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Share (%)')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Plot emissions
    for scenario_name, df in results.items():
        axes[0, 1].plot(df['year'], df['emissions'] / 1e6, label=scenario_name)
    axes[0, 1].set_title('CO2 Emissions')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Emissions (Mt CO2)')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Plot investment
    for scenario_name, df in results.items():
        axes[1, 0].plot(df['year'], df['investment'] / 1e9, label=scenario_name)
    axes[1, 0].set_title('Annual Investment')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Investment (Billion USD)')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Plot LCOE
    for scenario_name, df in results.items():
        axes[1, 1].plot(df['year'], df['lcoe'], label=scenario_name)
    axes[1, 1].set_title('Levelized Cost of Electricity')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('LCOE (USD/kWh)')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    # Plot water use
    for scenario_name, df in results.items():
        axes[2, 0].plot(df['year'], df['water_use'] / 1e6, label=scenario_name)
    axes[2, 0].set_title('Water Use')
    axes[2, 0].set_xlabel('Year')
    axes[2, 0].set_ylabel('Water Use (Million m³)')
    axes[2, 0].legend()
    axes[2, 0].grid(True)
    
    # Plot employment
    for scenario_name, df in results.items():
        axes[2, 1].plot(df['year'], df['employment'] / 1e3, label=scenario_name)
    axes[2, 1].set_title('Direct Employment')
    axes[2, 1].set_xlabel('Year')
    axes[2, 1].set_ylabel('Jobs (thousands)')
    axes[2, 1].legend()
    axes[2, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('scenario_comparison.png')
    plt.close()
    
    print("Comparison plots saved to 'scenario_comparison.png'")

def generate_comparison_report(results: Dict[str, pd.DataFrame]):
    """Generate a comparison report for all scenarios."""
    report = []
    report.append("# Bangladesh Energy Transition Scenario Comparison")
    report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary statistics for each scenario
    for scenario_name, df in results.items():
        report.append(f"\n## {scenario_name} Scenario")
        
        # Renewable share
        final_share = df['renewable_share'].iloc[-1] * 100
        report.append(f"\n### Renewable Energy Share")
        report.append(f"- Final renewable share: {final_share:.1f}%")
        
        # Emissions
        initial_emissions = df['emissions'].iloc[0]
        final_emissions = df['emissions'].iloc[-1]
        emission_reduction = (initial_emissions - final_emissions) / 1e6
        report.append(f"\n### Emissions Reduction")
        report.append(f"- Initial emissions: {initial_emissions/1e6:.1f} Mt CO2")
        report.append(f"- Final emissions: {final_emissions/1e6:.1f} Mt CO2")
        report.append(f"- Total reduction: {emission_reduction:.1f} Mt CO2")
        
        # Investment
        total_investment = df['investment'].sum()
        report.append(f"\n### Investment Requirements")
        report.append(f"- Total investment needed: {format_currency(total_investment)}")
        report.append(f"- Average annual investment: {format_currency(total_investment / len(df))}")
        
        # LCOE
        final_lcoe = df['lcoe'].iloc[-1]
        report.append(f"\n### Cost of Electricity")
        report.append(f"- Final LCOE: {format_currency(final_lcoe)}/kWh")
        
        # Environmental impacts
        final_water_use = df['water_use'].iloc[-1]
        final_land_use = df['land_use'].iloc[-1]
        report.append(f"\n### Environmental Impacts")
        report.append(f"- Final water use: {final_water_use:,.0f} m³")
        report.append(f"- Final land use: {final_land_use:,.0f} m²")
        
        # Employment
        final_employment = df['employment'].iloc[-1]
        report.append(f"\n### Employment")
        report.append(f"- Final direct employment: {final_employment:,.0f} jobs")
    
    # Write report to file
    with open('scenario_comparison_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("Comparison report saved to 'scenario_comparison_report.md'")

if __name__ == '__main__':
    run_scenarios() 