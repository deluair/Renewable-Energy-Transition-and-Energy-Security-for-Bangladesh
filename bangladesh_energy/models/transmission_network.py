"""
Transmission network model for analyzing power flow and network constraints.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class TransmissionLine:
    """Parameters for a transmission line."""
    from_node: str
    to_node: str
    capacity: float  # Line capacity in MW
    reactance: float  # Line reactance in p.u.
    resistance: float  # Line resistance in p.u.
    length: float  # Line length in km
    voltage: float  # Line voltage in kV

@dataclass
class Substation:
    """Parameters for a substation."""
    name: str
    location: Tuple[float, float]  # (latitude, longitude)
    voltage_levels: List[float]  # Voltage levels in kV
    capacity: float  # Substation capacity in MVA
    load_served: float  # Load served in MW

class TransmissionNetworkModel:
    """Model for analyzing transmission network operations."""
    
    def __init__(self):
        self.network = nx.Graph()
        self.substations = {}
        self.lines = {}
    
    def add_substation(self, substation: Substation):
        """Add a substation to the network."""
        self.substations[substation.name] = substation
        self.network.add_node(
            substation.name,
            pos=substation.location,
            capacity=substation.capacity,
            load=substation.load_served
        )
    
    def add_transmission_line(self, line: TransmissionLine):
        """Add a transmission line to the network."""
        self.lines[(line.from_node, line.to_node)] = line
        self.network.add_edge(
            line.from_node,
            line.to_node,
            capacity=line.capacity,
            reactance=line.reactance,
            resistance=line.resistance,
            length=line.length,
            voltage=line.voltage
        )
    
    def calculate_power_flow(self, 
                           generation: Dict[str, float],
                           load: Dict[str, float]) -> pd.DataFrame:
        """Calculate power flow in the network using DC power flow."""
        results = []
        
        # Initialize node power injections
        power_injections = {}
        for node in self.network.nodes():
            power_injections[node] = (
                generation.get(node, 0) - load.get(node, 0)
            )
        
        # Calculate power flow using DC power flow
        for edge in self.network.edges():
            from_node, to_node = edge
            line = self.lines[(from_node, to_node)]
            
            # Calculate power flow (simplified DC power flow)
            angle_diff = 0.1  # Placeholder for angle difference
            power_flow = (angle_diff / line.reactance) * line.voltage
            
            # Check line capacity constraint
            if abs(power_flow) > line.capacity:
                power_flow = np.sign(power_flow) * line.capacity
            
            # Calculate losses
            losses = (power_flow ** 2) * line.resistance
            
            results.append({
                'from_node': from_node,
                'to_node': to_node,
                'power_flow': power_flow,
                'losses': losses,
                'utilization': abs(power_flow) / line.capacity
            })
        
        return pd.DataFrame(results)
    
    def analyze_network_reliability(self) -> Dict:
        """Analyze network reliability metrics."""
        # Calculate network metrics
        avg_degree = np.mean([d for n, d in self.network.degree()])
        clustering = nx.average_clustering(self.network)
        diameter = nx.diameter(self.network)
        
        # Calculate line utilization
        utilizations = []
        for edge in self.network.edges():
            line = self.lines[edge]
            utilizations.append(line.capacity)
        
        avg_utilization = np.mean(utilizations)
        
        # Calculate N-1 security
        n1_security = self._calculate_n1_security()
        
        return {
            'average_degree': avg_degree,
            'clustering_coefficient': clustering,
            'network_diameter': diameter,
            'average_utilization': avg_utilization,
            'n1_security': n1_security
        }
    
    def _calculate_n1_security(self) -> float:
        """Calculate N-1 security metric."""
        # Check network connectivity after removing each line
        n1_scores = []
        
        for edge in self.network.edges():
            # Create a copy of the network
            test_network = self.network.copy()
            
            # Remove the edge
            test_network.remove_edge(*edge)
            
            # Check if network remains connected
            if nx.is_connected(test_network):
                n1_scores.append(1.0)
            else:
                n1_scores.append(0.0)
        
        return np.mean(n1_scores)
    
    def identify_bottlenecks(self, power_flows: pd.DataFrame) -> List[Dict]:
        """Identify network bottlenecks."""
        bottlenecks = []
        
        # Find highly utilized lines
        high_utilization = power_flows[power_flows['utilization'] > 0.8]
        
        for _, line in high_utilization.iterrows():
            bottlenecks.append({
                'from_node': line['from_node'],
                'to_node': line['to_node'],
                'utilization': line['utilization'],
                'power_flow': line['power_flow'],
                'capacity': self.lines[(line['from_node'], line['to_node'])].capacity
            })
        
        return bottlenecks
    
    def calculate_network_losses(self, power_flows: pd.DataFrame) -> Dict:
        """Calculate network losses and efficiency metrics."""
        total_losses = power_flows['losses'].sum()
        total_flow = power_flows['power_flow'].abs().sum()
        
        # Calculate loss factor
        loss_factor = total_losses / total_flow if total_flow > 0 else 0
        
        # Calculate network efficiency
        efficiency = 1 - loss_factor
        
        return {
            'total_losses': total_losses,
            'total_flow': total_flow,
            'loss_factor': loss_factor,
            'network_efficiency': efficiency
        }
    
    def optimize_network_expansion(self, 
                                 future_load: Dict[str, float],
                                 max_investment: float) -> List[Dict]:
        """Optimize network expansion to meet future load."""
        expansion_plans = []
        
        # Calculate load growth
        for node, load in future_load.items():
            current_load = self.substations[node].load_served
            load_growth = load - current_load
            
            if load_growth > 0:
                # Check if existing lines can handle the growth
                connected_lines = self.network.edges(node)
                total_capacity = sum(
                    self.lines[edge].capacity for edge in connected_lines
                )
                
                if total_capacity < load_growth:
                    # Propose new line
                    new_capacity = load_growth - total_capacity
                    cost = new_capacity * 1000  # Simplified cost model
                    
                    if cost <= max_investment:
                        expansion_plans.append({
                            'node': node,
                            'new_capacity': new_capacity,
                            'cost': cost,
                            'load_growth': load_growth
                        })
        
        return expansion_plans 