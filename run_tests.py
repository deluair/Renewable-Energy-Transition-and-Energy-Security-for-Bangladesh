"""
Script to run the test suite for the Bangladesh Energy Transition simulation.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests in the test suite."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('bangladesh_energy/tests', pattern='test_*.py')
    
    # Run tests with verbosity
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 