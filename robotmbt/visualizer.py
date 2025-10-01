import networkx as nx
import plotly.graph_objects as go
from plotly.offline import plot
from robotmbt.suitedata import Suite, Scenario, Step

class ModelVisualizer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.executed_path_ids = []

    def build_graph_from_suite(self, suite: Suite):
        """Builds a graph from a RobotMBT suite with scenarios as nodes"""
        # Clear existing graph
        self.graph = nx.DiGraph()
        
        # Add all scenarios as nodes
        for scenario in suite.scenarios:
            if scenario.src_id is not None:
                node_id = f"S{scenario.src_id}"
                self.graph.add_node(node_id, 
                                   label=scenario.name,
                                   repetitions=0)  # Track how many times scenario appears

        # Create edges based on execution order (simplified for prototype)
        # In real implementation, this would use the actual model transitions
        scenario_ids = [f"S{scenario.src_id}" for scenario in suite.scenarios 
                       if scenario.src_id is not None]
        
        for i in range(len(scenario_ids) - 1):
            self.graph.add_edge(scenario_ids[i], scenario_ids[i + 1])

    def set_executed_path(self, path_scenario_ids: list):
        """Marks which scenarios were executed in the current run"""
        self.executed_path_ids = [f"S{id}" for id in path_scenario_ids]
        
        # Update repetition counts
        for node_id in self.executed_path_ids:
            if node_id in self.graph.nodes:
                current_reps = self.graph.nodes[node_id].get('repetitions', 0)
                self.graph.nodes[node_id]['repetitions'] = current_reps + 1

    def generate_plotly_html(self, output_file="mbt_dependency_graph.html"):
        """Generates an interactive Plotly graph as standalone HTML"""
        if not self.graph.nodes:
            print("No graph data available")
            return

        # Use spring layout for node positioning
        pos = nx.spring_layout(self.graph, seed=42, k=1, iterations=50)

        # Prepare node data
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Node text with scenario info
            label = self.graph.nodes[node].get('label', node)
            reps = self.graph.nodes[node].get('repetitions', 0)
            node_text.append(f"Scenario: {label}<br>ID: {node}<br>Executions: {reps}")
            
            # Color: red for executed, lightblue for available but not executed
            if node in self.executed_path_ids:
                node_color.append('red')
                node_size.append(40)  # Larger for executed scenarios
            else:
                node_color.append('lightblue')
                node_size.append(25)

        # Prepare edge data
        edge_x = []
        edge_y = []
        edge_color = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Color edges red if both nodes were executed
            if edge[0] in self.executed_path_ids and edge[1] in self.executed_path_ids:
                edge_color.append('red')
            else:
                edge_color.append('gray')

        # Create edge traces
        edge_traces = []
        for i in range(0, len(edge_x), 3):
            if i + 2 < len(edge_x):
                edge_trace = go.Scatter(
                    x=edge_x[i:i+3], y=edge_y[i:i+3],
                    mode='lines',
                    line=dict(width=2, color=edge_color[i//3]),
                    hoverinfo='none'
                )
                edge_traces.append(edge_trace)

        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in self.graph.nodes()],
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='darkblue')
            ),
            textfont=dict(size=10)
        )

        # Create the figure
        fig = go.Figure(data=edge_traces + [node_trace],
               layout=go.Layout(
                   title=dict(
                       text='RobotMBT Scenario Dependency Graph<br>'
                            '<sub>Red: Executed path, Blue: Available scenarios</sub>',
                       font=dict(size=16)
                   ),
                   showlegend=False,
                   hovermode='closest',
                   margin=dict(b=20, l=5, r=5, t=60),
                   annotations=[dict(
                       text="Hover over nodes for scenario details",
                       showarrow=False,
                       xref="paper", yref="paper",
                       x=0.005, y=-0.002
                   )],
                   xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                   yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
               )

        # Save as standalone HTML
        plot(fig, filename=output_file, auto_open=False)
        print(f"MBT Visualization saved to: {output_file}")

# Standalone test function
def create_sample_visualization():
    """Creates a sample visualization for testing"""
    # Create mock RobotMBT data
    mock_suite = Suite("Sample_MBT_Suite")
    
    # Create sample scenarios
    scenarios = [
        ("S1: User Login", 1),
        ("S2: View Dashboard", 2), 
        ("S3: Search Products", 3),
        ("S4: Add to Cart", 4),
        ("S5: Checkout", 5)
    ]
    
    for name, src_id in scenarios:
        scenario = Scenario(name, mock_suite)
        scenario.src_id = src_id
        mock_suite.scenarios.append(scenario)

    # Build visualization
    visualizer = ModelVisualizer()
    visualizer.build_graph_from_suite(mock_suite)
    
    # Simulate an executed path (S1 -> S3 -> S4 -> S5)
    visualizer.set_executed_path([1, 3, 4, 5])
    
    # Generate the HTML file
    visualizer.generate_plotly_html("sample_mbt_visualization.html")

if __name__ == "__main__":
    create_sample_visualization()