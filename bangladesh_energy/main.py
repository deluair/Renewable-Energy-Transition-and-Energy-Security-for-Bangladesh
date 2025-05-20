"""
Main simulation script for Bangladesh's renewable energy transition.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns

from models.energy_system import EnergySystem, EnergySystemConfig
from models.economic_model import EconomicModel, EconomicConfig
from models.environmental_model import EnvironmentalModel, EnvironmentalConfig

class BangladeshEnergyTransition:
    """Main simulation class for Bangladesh's energy transition."""
    
    def __init__(self):
        # Initialize configurations
        self.energy_config = EnergySystemConfig()
        self.economic_config = EconomicConfig()
        self.environmental_config = EnvironmentalConfig()
        
        # Initialize models
        self.energy_system = EnergySystem(self.energy_config)
        self.economic_model = EconomicModel(self.economic_config)
        self.environmental_model = EnvironmentalModel(self.environmental_config)
        
        # Initialize results storage
        self.results = {
            'renewable_share': [],
            'emissions': [],
            'costs': [],
            'investments': [],
            'environmental_impacts': []
        }
    
    def run_simulation(self, years: List[int]):
        """Run the simulation for specified years."""
        for year in years:
            print(f"\nSimulating year {year}...")
            
            # Simulate energy system
            self.energy_system.simulate_generation(year)
            renewable_share = self.energy_system.calculate_renewable_share(year)
            self.results['renewable_share'].append({
                'year': year,
                'share': renewable_share
            })
            
            # Calculate economic metrics
            system_summary = self.energy_system.get_system_summary(year)
            for tech, capacity in system_summary['capacity_by_technology'].items():
                if capacity > 0:
                    investment = self.economic_model.analyze_investment(
                        tech, capacity, 
                        system_summary['generation_by_technology'].get(tech, 0),
                        year
                    )
                    self.results['investments'].append({
                        'year': year,
                        'technology': tech,
                        **investment
                    })
            
            # Calculate environmental impacts
            total_emissions = 0
            for tech, generation in system_summary['generation_by_technology'].items():
                emissions = self.environmental_model.calculate_emissions(tech, generation)
                total_emissions += emissions
                
                # Calculate other environmental impacts
                water_use = self.environmental_model.calculate_water_use(tech, generation)
                land_use = self.environmental_model.calculate_land_use(tech, capacity)
                air_pollutants = self.environmental_model.calculate_air_pollutants(tech, generation)
                
                self.results['environmental_impacts'].append({
                    'year': year,
                    'technology': tech,
                    'emissions': emissions,
                    'water_use': water_use,
                    'land_use': land_use,
                    'air_pollutants': air_pollutants
                })
            
            self.results['emissions'].append({
                'year': year,
                'total_emissions': total_emissions
            })
    
    def plot_results(self):
        """Plot key simulation results."""
        # Set style
        plt.style.use('seaborn')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Bangladesh Energy Transition Simulation Results')
        
        # Plot renewable share
        renewable_data = pd.DataFrame(self.results['renewable_share'])
        axes[0, 0].plot(renewable_data['year'], renewable_data['share'] * 100)
        axes[0, 0].set_title('Renewable Energy Share')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Share (%)')
        axes[0, 0].grid(True)
        
        # Plot emissions
        emissions_data = pd.DataFrame(self.results['emissions'])
        axes[0, 1].plot(emissions_data['year'], emissions_data['total_emissions'] / 1e6)
        axes[0, 1].set_title('Total CO2 Emissions')
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Emissions (Mt CO2)')
        axes[0, 1].grid(True)
        
        # Plot investments
        investments_data = pd.DataFrame(self.results['investments'])
        investments_by_year = investments_data.groupby('year')['capex'].sum()
        axes[1, 0].bar(investments_by_year.index, investments_by_year / 1e9)
        axes[1, 0].set_title('Annual Investment')
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Investment (Billion USD)')
        axes[1, 0].grid(True)
        
        # Plot environmental impacts
        env_data = pd.DataFrame(self.results['environmental_impacts'])
        env_by_year = env_data.groupby('year')['emissions'].sum()
        axes[1, 1].plot(env_by_year.index, env_by_year / 1e6)
        axes[1, 1].set_title('Environmental Impact Score')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Impact Score')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('simulation_results.png')
        plt.close()
    
    def generate_report(self):
        """Generate a comprehensive report of simulation results."""
        report = []
        report.append("# Bangladesh Energy Transition Simulation Report")
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary statistics
        report.append("\n## Key Findings")
        
        # Renewable share
        renewable_data = pd.DataFrame(self.results['renewable_share'])
        final_share = renewable_data['share'].iloc[-1] * 100
        report.append(f"\n### Renewable Energy Share")
        report.append(f"- Final renewable share: {final_share:.1f}%")
        
        # Emissions
        emissions_data = pd.DataFrame(self.results['emissions'])
        emission_reduction = (emissions_data['total_emissions'].iloc[0] - 
                            emissions_data['total_emissions'].iloc[-1]) / 1e6
        report.append(f"\n### Emissions Reduction")
        report.append(f"- Total emission reduction: {emission_reduction:.1f} Mt CO2")
        
        # Investments
        investments_data = pd.DataFrame(self.results['investments'])
        total_investment = investments_data['capex'].sum() / 1e9
        report.append(f"\n### Investment Requirements")
        report.append(f"- Total investment needed: ${total_investment:.1f} billion")
        
        # Environmental impacts
        env_data = pd.DataFrame(self.results['environmental_impacts'])
        report.append(f"\n### Environmental Impacts")
        report.append(f"- Total land use: {env_data['land_use'].sum():.1f} m²")
        report.append(f"- Total water use: {env_data['water_use'].sum():.1f} m³")
        
        # Write report to file
        with open('simulation_report.md', 'w') as f:
            f.write('\n'.join(report))

def main():
    """Main function to run the simulation."""
    # Create simulation instance
    simulation = BangladeshEnergyTransition()
    
    # Run simulation for 2024-2050
    years = list(range(2024, 2051))
    simulation.run_simulation(years)
    
    # Generate visualizations and report
    simulation.plot_results()
    simulation.generate_report()
    
    print("\nSimulation completed. Results saved to 'simulation_results.png' and 'simulation_report.md'")

if __name__ == "__main__":
    main() 