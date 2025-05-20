"""
Test cases for the advanced analysis module.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import os

from analysis.advanced_analysis import AdvancedAnalysis

class TestAdvancedAnalysis(unittest.TestCase):
    """Test cases for the advanced analysis module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample data
        self.sample_data = pd.DataFrame({
            'year': range(2024, 2051),
            'renewable_share': np.linspace(0.1, 0.8, 27),
            'emissions': np.linspace(1000000, 200000, 27),
            'investment': np.linspace(1000000000, 2000000000, 27),
            'lcoe': np.linspace(0.15, 0.08, 27),
            'water_use': np.linspace(1000000, 200000, 27),
            'employment': np.linspace(10000, 50000, 27)
        })
        
        self.analysis = AdvancedAnalysis(self.sample_data)
    
    def test_calculate_metrics(self):
        """Test calculation of key metrics."""
        metrics = self.analysis.calculate_metrics()
        
        # Test metric calculations
        self.assertIn('renewable_share_growth', metrics)
        self.assertIn('emissions_reduction', metrics)
        self.assertIn('total_investment', metrics)
        self.assertIn('avg_lcoe', metrics)
        self.assertIn('water_use_reduction', metrics)
        self.assertIn('employment_growth', metrics)
        
        # Test metric values
        self.assertGreater(metrics['renewable_share_growth'], 0)
        self.assertGreater(metrics['emissions_reduction'], 0)
        self.assertGreater(metrics['total_investment'], 0)
        self.assertGreater(metrics['water_use_reduction'], 0)
        self.assertGreater(metrics['employment_growth'], 0)
    
    def test_create_heatmap(self):
        """Test creation of correlation heatmap."""
        self.analysis.create_heatmap()
        
        # Check if file was created
        self.assertTrue(os.path.exists('correlation_heatmap.png'))
        
        # Clean up
        os.remove('correlation_heatmap.png')
    
    def test_create_radar_chart(self):
        """Test creation of radar chart."""
        self.analysis.create_radar_chart()
        
        # Check if file was created
        self.assertTrue(os.path.exists('performance_radar_chart.html'))
        
        # Clean up
        os.remove('performance_radar_chart.html')
    
    def test_generate_advanced_report(self):
        """Test generation of advanced report."""
        self.analysis.generate_advanced_report()
        
        # Check if file was created
        self.assertTrue(os.path.exists('advanced_analysis_report.md'))
        
        # Check report content
        with open('advanced_analysis_report.md', 'r') as f:
            content = f.read()
            self.assertIn('Advanced Analysis Report', content)
            self.assertIn('Key Performance Metrics', content)
            self.assertIn('Trend Analysis', content)
        
        # Clean up
        os.remove('advanced_analysis_report.md')
    
    def test_create_interactive_dashboard(self):
        """Test creation of interactive dashboard."""
        self.analysis.create_interactive_dashboard()
        
        # Check if file was created
        self.assertTrue(os.path.exists('energy_transition_dashboard.html'))
        
        # Clean up
        os.remove('energy_transition_dashboard.html')

if __name__ == '__main__':
    unittest.main() 