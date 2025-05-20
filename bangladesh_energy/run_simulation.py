"""
Main simulation runner for Bangladesh Energy Transition Simulation.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from bangladesh_energy.models.energy_system import EnergySystem, EnergySystemConfig
from bangladesh_energy.models.economic_model import EconomicModel
from bangladesh_energy.models.environmental_model import EnvironmentalModel, EnvironmentalConfig
from bangladesh_energy.models.grid_stability import GridStabilityModel, GridParameters
from bangladesh_energy.models.storage_model import StorageModel, StorageParameters, StorageTechnology
from bangladesh_energy.models.demand_response import DemandResponseModel, DemandResponseParameters
from bangladesh_energy.models.transmission_network import TransmissionNetworkModel, TransmissionLine, Substation
from bangladesh_energy.models.distribution_network import DistributionNetworkModel, DistributionLine, DistributionTransformer, DistributedGenerator
from bangladesh_energy.models.market_model import MarketModel, MarketParameters, Generator, MarketType
from bangladesh_energy.models.weather_model import WeatherModel, WeatherParameters, SolarParameters, WindParameters
from bangladesh_energy.config.simulation_config import SimulationConfig

class SimulationRunner:
    """Main simulation runner class."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.results = {}
        
        # Initialize models
        self.energy_model = EnergySystem(EnergySystemConfig(
            start_year=config.START_YEAR,
            end_year=config.END_YEAR,
            technologies=config.TECHNOLOGIES
        ))
        self.economic_model = EconomicModel(config.ECONOMIC_PARAMS)
        self.environmental_model = EnvironmentalModel(EnvironmentalConfig(**config.ENVIRONMENTAL_PARAMS))
        
        # Initialize grid stability model
        self.grid_model = GridStabilityModel(GridParameters(
            base_load=config.DEMAND_PARAMS['base_load'],
            peak_load=config.DEMAND_PARAMS['peak_load'],
            voltage_levels=[132, 230, 400],  # kV
            transmission_loss=config.GRID_PARAMS['transmission_loss'],
            spinning_reserve=0.1,  # 10% spinning reserve
            frequency_band=(49.5, 50.5),  # Hz
            voltage_band=(0.95, 1.05)  # p.u.
        ))
        
        # Initialize storage model
        self.storage_model = StorageModel(StorageParameters(
            technology=StorageTechnology.LITHIUM_ION,
            capacity=1000,  # MWh
            power=500,  # MW
            efficiency=0.9,
            lifetime=15,  # years
            capex=300,  # USD/kWh
            opex=5,  # USD/kWh/year
            degradation=0.02,  # 2% per year
            response_time=0.1  # seconds
        ))
        
        # Initialize demand response model
        self.dr_model = DemandResponseModel(DemandResponseParameters(
            program_type=None,  # Set appropriate DemandResponseType if needed
            participation_rate=0.2,  # 20% participation
            response_delay=15,  # minutes
            duration=4,  # hours
            max_reduction=3000,  # MW (example value)
            min_reduction=500,  # MW (example value)
            incentive_rate=0.05,  # USD/kWh (example value)
            notification_time=24  # hours
        ))
        
        # Initialize transmission network model
        self.transmission_model = TransmissionNetworkModel()
        
        # Initialize distribution network model
        self.distribution_model = DistributionNetworkModel()
        
        # Initialize market model
        self.market_model = MarketModel(MarketParameters(
            market_type=MarketType.DAY_AHEAD,
            price_cap=1000,  # USD/MWh
            price_floor=0,  # USD/MWh
            demand_elasticity=-0.1,
            market_clearing_interval=1,  # hour
            reserve_margin=0.15  # 15% reserve margin
        ))
        
        # Initialize weather model
        self.weather_model = WeatherModel(WeatherParameters(
            location=(23.6850, 90.3563),  # Dhaka coordinates
            elevation=4,  # meters
            timezone='Asia/Dhaka',
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 12, 31),
            resolution='1H'
        ))
    
    def run_simulation(self) -> Dict:
        """Run the complete simulation."""
        # Generate weather data
        weather_data = self.weather_model.generate_weather_data()
        
        # Calculate renewable resources
        solar_data = self.weather_model.calculate_solar_resource(SolarParameters(
            tilt_angle=23.685,  # Latitude tilt
            azimuth=180,  # South-facing
            albedo=0.2,
            tracking=False,
            degradation=0.005  # 0.5% per year
        ))
        
        wind_data = self.weather_model.calculate_wind_resource(WindParameters(
            hub_height=100,  # meters
            roughness_length=0.1,
            wind_shear=0.2,
            turbulence=0.1
        ))
        
        # Run energy system simulation
        energy_results = self.energy_model.simulate()
        
        # Calculate economic metrics
        economic_results = self.economic_model.calculate_metrics(energy_results)
        
        # Calculate environmental impacts
        environmental_results = self.environmental_model.calculate_impacts(energy_results)
        
        # Analyze grid stability
        grid_results_list = []
        for year, data in energy_results.items():
            grid_results_list.append(self.grid_model.analyze_stability(
                pd.DataFrame(data['generation_by_technology'], index=[0]), # Create DataFrame from dict
                pd.Series(data['total_demand']) # Create Series from scalar
            ))
        grid_results = pd.concat(grid_results_list) # Concatenate results from all years
        
        # Analyze storage operation
        storage_results_list = []
        for year, data in energy_results.items():
            # Assuming economic_results is also a dict with year as key
            # and electricity_price is available per year.
            # This might need further adjustment based on how economic_results is structured.
            electricity_price_for_year = economic_results.get(year, {}).get('electricity_price', pd.Series(dtype=float)) 
            storage_results_list.append(self.storage_model.calculate_storage_operation(
                pd.Series(data['generation_by_technology']), # Create Series from dict
                pd.Series(data['total_demand']), # Create Series from scalar
                electricity_price_for_year
            ))
        storage_results = pd.concat(storage_results_list) # Concatenate results
        
        # Analyze demand response
        dr_results_list = []
        for year, data in energy_results.items():
            # Similar assumptions as above for electricity_price
            electricity_price_for_year = economic_results.get(year, {}).get('electricity_price', pd.Series(dtype=float))
            # Define event_start and event_duration for annual simulation
            event_start_for_year = pd.Timestamp(f"{year}-01-01") # Example: start of the year
            event_duration_for_year = self.dr_model.params.duration # Use duration from DR params
            dr_results_list.append(self.dr_model.simulate_demand_response_event(
                data['total_demand'], # Pass as scalar
                event_start_for_year, # Add event_start
                event_duration_for_year, # Add event_duration
            ))
        dr_results = pd.concat(dr_results_list) # Concatenate results
        
        # Analyze transmission network
        transmission_results_list = []
        for year, data in energy_results.items():
            transmission_results_list.append(self.transmission_model.calculate_power_flow(
                data['generation_by_technology'],
                data['total_demand']
            ))
        transmission_results = pd.concat(transmission_results_list) if transmission_results_list else pd.DataFrame()
        
        # Analyze distribution network
        distribution_results_list = []
        for year, data in energy_results.items():
             # Ensure network and distributed_generators are initialized correctly for this to work
            nodes_load = {node: data['total_demand'] for node in getattr(self.distribution_model, 'network', {})} 
            generators_generation = {gen: data['generation_by_technology'] for gen in getattr(self.distribution_model, 'distributed_generators', {})}
            distribution_results_list.append(self.distribution_model.calculate_power_flow(
                nodes_load,
                generators_generation
            ))
        distribution_results = pd.concat(distribution_results_list) if distribution_results_list else pd.DataFrame()
        
        # Analyze market operations
        market_results_list = []
        for year, data in energy_results.items():
            market_results_list.append(self.market_model.clear_market(
                data['total_demand'], # Pass as scalar
                pd.Series(data['generation_by_technology']).sum() # Pass total renewable generation as scalar
            ))
        market_results = pd.concat(market_results_list) if market_results_list else pd.DataFrame()
        
        # Combine all results
        self.results = {
            'energy': energy_results,
            'economic': economic_results,
            'environmental': environmental_results,
            'grid': grid_results,
            'storage': storage_results,
            'demand_response': dr_results,
            'transmission': transmission_results,
            'distribution': distribution_results,
            'market': market_results,
            'weather': {
                'data': weather_data,
                'solar': solar_data,
                'wind': wind_data
            }
        }
        
        return self.results
    
    def save_results(self, output_dir: str = 'results'):
        """Save simulation results to files."""
        os.makedirs(output_dir, exist_ok=True)
        # Save main results for each category (energy, economic, etc.)
        for category, yearly_data in self.results.items():
            if category == 'weather': # Weather data is handled separately
                continue
            if isinstance(yearly_data, dict):
                # If yearly_data is a dict of dicts (e.g., {year: {metrics...}} )
                all_years_df_list = []
                for year, data_for_year in yearly_data.items():
                    if isinstance(data_for_year, dict):
                        # Convert each year's dict to a DataFrame and add a year column
                        df = pd.DataFrame(list(data_for_year.items()), columns=['Metric', 'Value'])
                        df['Year'] = year
                        all_years_df_list.append(df)
                    elif isinstance(data_for_year, pd.DataFrame):
                        # If already a DataFrame (e.g. grid_results from concat)
                        data_for_year['Year'] = year # Add year if not present, though concat might handle it
                        all_years_df_list.append(data_for_year)
                if all_years_df_list:
                    final_df = pd.concat(all_years_df_list)
                    final_df.to_csv(f'{output_dir}/{category}_results.csv', index=False)
            elif isinstance(yearly_data, pd.DataFrame):
                # If the category itself is a DataFrame (e.g. grid_results after concat)
                yearly_data.to_csv(f'{output_dir}/{category}_results.csv', index=False)
        # Save weather data
        if 'weather' in self.results and isinstance(self.results['weather'], dict):
            if 'data' in self.results['weather'] and isinstance(self.results['weather']['data'], pd.DataFrame):
                self.results['weather']['data'].to_csv(f'{output_dir}/weather_data.csv', index=False)
            if 'solar' in self.results['weather'] and isinstance(self.results['weather']['solar'], pd.DataFrame):
                self.results['weather']['solar'].to_csv(f'{output_dir}/solar_data.csv', index=False)
            if 'wind' in self.results['weather'] and isinstance(self.results['weather']['wind'], pd.DataFrame):
                self.results['weather']['wind'].to_csv(f'{output_dir}/wind_data.csv', index=False)
        # Generate summary report
        # self._generate_summary_report(output_dir) # Commented out for now
    
    def _generate_summary_report(self, output_dir: str):
        """Generate a summary report of the simulation results."""
        report = []
        report.append("# Bangladesh Energy Transition Simulation Results\n")
        
        # Energy System Summary
        report.append("## Energy System")
        report.append(f"- Total Generation: {self.results['energy']['total_generation']:.2f} TWh")
        report.append(f"- Renewable Share: {self.results['energy']['renewable_share']:.1f}%")
        report.append(f"- Peak Demand: {self.results['energy']['peak_demand']:.2f} GW")
        
        # Economic Summary
        report.append("\n## Economic Metrics")
        report.append(f"- Total Investment: ${self.results['economic']['total_investment']:.2f} billion")
        report.append(f"- Average LCOE: ${self.results['economic']['average_lcoe']:.2f}/MWh")
        report.append(f"- Total Cost: ${self.results['economic']['total_cost']:.2f} billion")
        
        # Environmental Summary
        report.append("\n## Environmental Impacts")
        report.append(f"- CO2 Emissions: {self.results['environmental']['co2_emissions']:.2f} Mt")
        report.append(f"- Water Use: {self.results['environmental']['water_use']:.2f} million m³")
        report.append(f"- Land Use: {self.results['environmental']['land_use']:.2f} km²")
        
        # Grid Stability Summary
        report.append("\n## Grid Stability")
        report.append(f"- Frequency Deviation: {self.results['grid']['frequency_deviation']:.2f} Hz")
        report.append(f"- Voltage Stability: {self.results['grid']['voltage_stability']:.2f} p.u.")
        report.append(f"- Reserve Adequacy: {self.results['grid']['reserve_adequacy']:.1f}%")
        
        # Storage Summary
        report.append("\n## Energy Storage")
        report.append(f"- Storage Utilization: {self.results['storage']['utilization_rate']:.1f}%")
        report.append(f"- Storage Revenue: ${self.results['storage']['revenue']:.2f} million")
        report.append(f"- Storage Cost: ${self.results['storage']['cost']:.2f} million")
        
        # Demand Response Summary
        report.append("\n## Demand Response")
        report.append(f"- Load Reduction: {self.results['demand_response']['load_reduction']:.1f}%")
        report.append(f"- Program Cost: ${self.results['demand_response']['program_cost']:.2f} million")
        report.append(f"- Participant Savings: ${self.results['demand_response']['participant_savings']:.2f} million")
        
        # Transmission Summary
        report.append("\n## Transmission Network")
        report.append(f"- Network Losses: {self.results['transmission']['losses'].sum():.2f} MWh")
        report.append(f"- Average Utilization: {self.results['transmission']['utilization'].mean():.1f}%")
        report.append(f"- Network Efficiency: {self.results['transmission']['efficiency']:.1f}%")
        
        # Distribution Summary
        report.append("\n## Distribution Network")
        report.append(f"- Distribution Losses: {self.results['distribution']['losses'].sum():.2f} MWh")
        report.append(f"- Transformer Loading: {self.results['distribution']['transformer_loading'].mean():.1f}%")
        report.append(f"- Voltage Profile: {self.results['distribution']['voltage_profile']['avg_voltage']:.2f} p.u.")
        
        # Market Summary
        report.append("\n## Market Operations")
        report.append(f"- Average Price: ${self.results['market']['market_price'].mean():.2f}/MWh")
        report.append(f"- Market Efficiency: {self.results['market']['market_efficiency']:.1f}%")
        report.append(f"- Consumer Surplus: ${self.results['market']['consumer_surplus']:.2f} million")
        
        # Write report
        with open(f'{output_dir}/simulation_summary.md', 'w') as f:
            f.write('\n'.join(report))

def main():
    """Main function to run the simulation."""
    # Load configuration
    config = SimulationConfig()
    
    # Create simulation runner
    runner = SimulationRunner(config)
    
    # Run simulation
    results = runner.run_simulation()
    
    # Save results
    runner.save_results()
    
    print("Simulation completed successfully!")
    print("Results saved in the 'results' directory.")

if __name__ == '__main__':
    main() 