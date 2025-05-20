"""
Script to run sensitivity analysis on key parameters of the Bangladesh Energy Transition simulation.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple

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

class SensitivityAnalysis:
    """Class for running sensitivity analysis on simulation parameters."""
    
    def __init__(self):
        self.config = SimulationConfig()
        self.base_results = None
    
    def run_base_case(self) -> pd.DataFrame:
        """Run the base case simulation."""
        print("Running base case simulation...")
        
        # Initialize models
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
        
        self.base_results = pd.DataFrame(results)
        return self.base_results
    
    def run_sensitivity_analysis(
        self,
        parameter: str,
        values: List[float],
        target_year: int = 2050
    ) -> pd.DataFrame:
        """
        Run sensitivity analysis for a specific parameter.
        
        Args:
            parameter: Parameter to analyze
            values: List of values to test
            target_year: Year to analyze results for
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        print(f"\nRunning sensitivity analysis for {parameter}...")
        
        # Initialize results storage
        results = {
            'value': [],
            'renewable_share': [],
            'emissions': [],
            'investment': [],
            'lcoe': [],
            'water_use': [],
            'land_use': [],
            'employment': []
        }
        
        # Run simulation for each value
        for value in values:
            print(f"Testing value: {value}")
            
            # Modify parameter
            self._modify_parameter(parameter, value)
            
            # Run simulation
            df = self.run_base_case()
            
            # Get results for target year
            year_results = df[df['year'] == target_year].iloc[0]
            
            # Store results
            results['value'].append(value)
            results['renewable_share'].append(year_results['renewable_share'])
            results['emissions'].append(year_results['emissions'])
            results['investment'].append(year_results['investment'])
            results['lcoe'].append(year_results['lcoe'])
            results['water_use'].append(year_results['water_use'])
            results['land_use'].append(year_results['land_use'])
            results['employment'].append(year_results['employment'])
        
        return pd.DataFrame(results)
    
    def _modify_parameter(self, parameter: str, value: float):
        """Modify a specific parameter in the configuration."""
        if parameter == 'discount_rate':
            self.config.ECONOMIC_PARAMS['discount_rate'] = value
        elif parameter == 'inflation_rate':
            self.config.ECONOMIC_PARAMS['inflation_rate'] = value
        elif parameter == 'carbon_price':
            self.config.ECONOMIC_PARAMS['carbon_price'] = value
        elif parameter == 'solar_capex':
            self.config.TECHNOLOGIES['solar_pv']['capex'] = value
        elif parameter == 'wind_capex':
            self.config.TECHNOLOGIES['wind']['capex'] = value
        elif parameter == 'biomass_capex':
            self.config.TECHNOLOGIES['biomass']['capex'] = value
        elif parameter == 'solar_capacity_factor':
            self.config.TECHNOLOGIES['solar_pv']['capacity_factor'] = value
        elif parameter == 'wind_capacity_factor':
            self.config.TECHNOLOGIES['wind']['capacity_factor'] = value
        elif parameter == 'biomass_capacity_factor':
            self.config.TECHNOLOGIES['biomass']['capacity_factor'] = value
        else:
            raise ValueError(f"Unknown parameter: {parameter}")

def run_sensitivity_analysis():
    """Run sensitivity analysis on key parameters."""
    print("Starting Bangladesh Energy Transition Sensitivity Analysis...")
    
    # Initialize sensitivity analysis
    sa = SensitivityAnalysis()
    
    # Run base case
    base_results = sa.run_base_case()
    
    # Define parameters to analyze
    parameters = {
        'discount_rate': [0.05, 0.08, 0.12],  # 5%, 8%, 12%
        'carbon_price': [20, 50, 100],        # USD/ton CO2
        'solar_capex': [600, 800, 1000],      # USD/kW
        'wind_capex': [900, 1200, 1500],      # USD/kW
        'solar_capacity_factor': [0.15, 0.18, 0.21],  # 15%, 18%, 21%
        'wind_capacity_factor': [0.20, 0.25, 0.30]    # 20%, 25%, 30%
    }
    
    # Run sensitivity analysis for each parameter
    results = {}
    for parameter, values in parameters.items():
        results[parameter] = sa.run_sensitivity_analysis(parameter, values)
    
    # Generate sensitivity plots
    generate_sensitivity_plots(results)
    
    # Generate sensitivity report
    generate_sensitivity_report(results)
    
    print("\nSensitivity analysis complete!")

def generate_sensitivity_plots(results: Dict[str, pd.DataFrame]):
    """Generate sensitivity analysis plots."""
    # Set style
    plt.style.use('seaborn')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    fig.suptitle('Bangladesh Energy Transition Sensitivity Analysis')
    
    # Plot renewable share sensitivity
    for parameter, df in results.items():
        axes[0, 0].plot(df['value'], df['renewable_share'] * 100, label=parameter)
    axes[0, 0].set_title('Renewable Energy Share Sensitivity')
    axes[0, 0].set_xlabel('Parameter Value')
    axes[0, 0].set_ylabel('Share (%)')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Plot emissions sensitivity
    for parameter, df in results.items():
        axes[0, 1].plot(df['value'], df['emissions'] / 1e6, label=parameter)
    axes[0, 1].set_title('CO2 Emissions Sensitivity')
    axes[0, 1].set_xlabel('Parameter Value')
    axes[0, 1].set_ylabel('Emissions (Mt CO2)')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Plot investment sensitivity
    for parameter, df in results.items():
        axes[1, 0].plot(df['value'], df['investment'] / 1e9, label=parameter)
    axes[1, 0].set_title('Investment Sensitivity')
    axes[1, 0].set_xlabel('Parameter Value')
    axes[1, 0].set_ylabel('Investment (Billion USD)')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Plot LCOE sensitivity
    for parameter, df in results.items():
        axes[1, 1].plot(df['value'], df['lcoe'], label=parameter)
    axes[1, 1].set_title('LCOE Sensitivity')
    axes[1, 1].set_xlabel('Parameter Value')
    axes[1, 1].set_ylabel('LCOE (USD/kWh)')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    # Plot water use sensitivity
    for parameter, df in results.items():
        axes[2, 0].plot(df['value'], df['water_use'] / 1e6, label=parameter)
    axes[2, 0].set_title('Water Use Sensitivity')
    axes[2, 0].set_xlabel('Parameter Value')
    axes[2, 0].set_ylabel('Water Use (Million m³)')
    axes[2, 0].legend()
    axes[2, 0].grid(True)
    
    # Plot employment sensitivity
    for parameter, df in results.items():
        axes[2, 1].plot(df['value'], df['employment'] / 1e3, label=parameter)
    axes[2, 1].set_title('Employment Sensitivity')
    axes[2, 1].set_xlabel('Parameter Value')
    axes[2, 1].set_ylabel('Jobs (thousands)')
    axes[2, 1].legend()
    axes[2, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png')
    plt.close()
    
    print("Sensitivity plots saved to 'sensitivity_analysis.png'")

def generate_sensitivity_report(results: Dict[str, pd.DataFrame]):
    """Generate a sensitivity analysis report."""
    report = []
    report.append("# Bangladesh Energy Transition Sensitivity Analysis")
    report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary statistics for each parameter
    for parameter, df in results.items():
        report.append(f"\n## {parameter.replace('_', ' ').title()}")
        
        # Calculate sensitivity metrics
        for metric in ['renewable_share', 'emissions', 'investment', 'lcoe', 'water_use', 'employment']:
            values = df[metric]
            min_val = values.min()
            max_val = values.max()
            range_val = max_val - min_val
            mean_val = values.mean()
            
            report.append(f"\n### {metric.replace('_', ' ').title()}")
            report.append(f"- Minimum: {min_val:,.2f}")
            report.append(f"- Maximum: {max_val:,.2f}")
            report.append(f"- Range: {range_val:,.2f}")
            report.append(f"- Mean: {mean_val:,.2f}")
            
            # Calculate sensitivity coefficient
            param_values = df['value']
            sensitivity = np.corrcoef(param_values, values)[0, 1]
            report.append(f"- Sensitivity coefficient: {sensitivity:.2f}")
    
    # Write report to file
    with open('sensitivity_analysis_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("Sensitivity report saved to 'sensitivity_analysis_report.md'")

if __name__ == '__main__':
    run_sensitivity_analysis() 