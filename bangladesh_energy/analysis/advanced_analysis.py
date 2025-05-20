"""
Advanced analysis tools for the Bangladesh Energy Transition simulation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class AdvancedAnalysis:
    """Class for advanced analysis and visualizations."""
    
    def __init__(self, results_df: pd.DataFrame):
        self.results = results_df
    
    def create_interactive_dashboard(self):
        """Create an interactive dashboard using Plotly."""
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Renewable Energy Share',
                'CO2 Emissions',
                'Investment Requirements',
                'LCOE Trends',
                'Environmental Impacts',
                'Employment Generation'
            )
        )
        
        # Add renewable share plot
        fig.add_trace(
            go.Scatter(
                x=self.results['year'],
                y=self.results['renewable_share'] * 100,
                name='Renewable Share'
            ),
            row=1, col=1
        )
        
        # Add emissions plot
        fig.add_trace(
            go.Scatter(
                x=self.results['year'],
                y=self.results['emissions'] / 1e6,
                name='Emissions'
            ),
            row=1, col=2
        )
        
        # Add investment plot
        fig.add_trace(
            go.Bar(
                x=self.results['year'],
                y=self.results['investment'] / 1e9,
                name='Investment'
            ),
            row=2, col=1
        )
        
        # Add LCOE plot
        fig.add_trace(
            go.Scatter(
                x=self.results['year'],
                y=self.results['lcoe'],
                name='LCOE'
            ),
            row=2, col=2
        )
        
        # Add environmental impacts plot
        fig.add_trace(
            go.Scatter(
                x=self.results['year'],
                y=self.results['water_use'] / 1e6,
                name='Water Use'
            ),
            row=3, col=1
        )
        
        # Add employment plot
        fig.add_trace(
            go.Scatter(
                x=self.results['year'],
                y=self.results['employment'] / 1e3,
                name='Employment'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1600,
            title_text="Bangladesh Energy Transition Dashboard",
            showlegend=True
        )
        
        # Save as HTML
        fig.write_html('energy_transition_dashboard.html')
    
    def calculate_metrics(self) -> Dict:
        """Calculate key performance metrics."""
        metrics = {}
        
        # Renewable energy metrics
        metrics['renewable_share_growth'] = (
            self.results['renewable_share'].iloc[-1] - 
            self.results['renewable_share'].iloc[0]
        ) * 100
        
        # Emissions metrics
        metrics['emissions_reduction'] = (
            self.results['emissions'].iloc[0] - 
            self.results['emissions'].iloc[-1]
        ) / 1e6
        
        # Economic metrics
        metrics['total_investment'] = self.results['investment'].sum() / 1e9
        metrics['avg_lcoe'] = self.results['lcoe'].mean()
        
        # Environmental metrics
        metrics['water_use_reduction'] = (
            self.results['water_use'].iloc[0] - 
            self.results['water_use'].iloc[-1]
        ) / 1e6
        
        # Social metrics
        metrics['employment_growth'] = (
            self.results['employment'].iloc[-1] - 
            self.results['employment'].iloc[0]
        ) / 1e3
        
        return metrics
    
    def create_heatmap(self):
        """Create a correlation heatmap of key metrics."""
        # Select metrics for correlation analysis
        metrics = [
            'renewable_share',
            'emissions',
            'investment',
            'lcoe',
            'water_use',
            'employment'
        ]
        
        # Calculate correlation matrix
        corr_matrix = self.results[metrics].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap='coolwarm',
            center=0,
            fmt='.2f'
        )
        plt.title('Correlation Matrix of Key Metrics')
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png')
        plt.close()
    
    def create_radar_chart(self):
        """Create a radar chart of key metrics."""
        # Calculate normalized metrics
        metrics = self.calculate_metrics()
        normalized_metrics = {
            'Renewable Share Growth': metrics['renewable_share_growth'] / 100,
            'Emissions Reduction': metrics['emissions_reduction'] / 50,  # Normalize to 50 Mt
            'Investment Efficiency': 1 - (metrics['avg_lcoe'] / 0.2),  # Normalize to 0.2 USD/kWh
            'Water Use Reduction': metrics['water_use_reduction'] / 100,  # Normalize to 100 million m³
            'Employment Growth': metrics['employment_growth'] / 100  # Normalize to 100k jobs
        }
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(normalized_metrics.values()),
            theta=list(normalized_metrics.keys()),
            fill='toself',
            name='Performance Metrics'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            title='Performance Metrics Radar Chart'
        )
        
        fig.write_html('performance_radar_chart.html')
    
    def generate_advanced_report(self):
        """Generate an advanced analysis report."""
        report = []
        report.append("# Advanced Analysis Report")
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Add metrics to report
        report.append("\n## Key Performance Metrics")
        report.append(f"- Renewable Share Growth: {metrics['renewable_share_growth']:.1f}%")
        report.append(f"- Emissions Reduction: {metrics['emissions_reduction']:.1f} Mt CO2")
        report.append(f"- Total Investment: ${metrics['total_investment']:.1f} billion")
        report.append(f"- Average LCOE: ${metrics['avg_lcoe']:.3f}/kWh")
        report.append(f"- Water Use Reduction: {metrics['water_use_reduction']:.1f} million m³")
        report.append(f"- Employment Growth: {metrics['employment_growth']:.1f}k jobs")
        
        # Add trend analysis
        report.append("\n## Trend Analysis")
        for column in ['renewable_share', 'emissions', 'investment', 'lcoe']:
            trend = np.polyfit(range(len(self.results)), self.results[column], 1)[0]
            report.append(f"- {column.replace('_', ' ').title()} Trend: {trend:.2e} per year")
        
        # Write report to file
        with open('advanced_analysis_report.md', 'w') as f:
            f.write('\n'.join(report)) 