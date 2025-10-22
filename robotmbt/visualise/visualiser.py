from .models import ScenarioGraph, TraceInfo, ScenarioInfo
import plotly.graph_objects as go


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide a simple interface through which the graph can be updated, and retrieved in HTML format.
    """
    def __init__(self):
        self.graph = ScenarioGraph()

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_start(self, scenario: ScenarioInfo):
        self.graph.set_starting_node(scenario)

    def set_end(self, scenario: ScenarioInfo):
        self.graph.set_ending_node(scenario)

    def generate_graph(self, edge_trace: go.Scatter, node_trace: go.Scatter):
        fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
        fig.show()

    def generate_edge_trace(self) -> go.Scatter:
        edge_x = []
        edge_y = []
        for edge in self.graph.networkx.edges:
            x0, y0 = self.graph.pos[edge[0]]
            x1, y1 = self.graph.pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            # None acts as seperator for between edges
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            # None acts as seperator for between edges
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        return edge_trace
    
    def generate_node_trace(self) -> go.Scatter:
        node_x = []
        node_y = []
        for vertex, pos in self.graph.pos.items():
            x, y = pos
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='#00F',
                size=10,
                line_width=2))
        
        return node_trace


    # TODO: use a graph library to actually create a graph
    def generate_html(self) -> str:
        self.graph.calculate_pos()
        edge_trace = self.generate_edge_trace()
        node_trace = self.generate_node_trace()
        self.generate_graph(edge_trace, node_trace)
        self.generate_graph()
        return f""
        # return f"<div><p>nodes: {self.graph.nodes}\nedges: {self.graph.edges}\nstart: {self.graph.start}\nend: {self.graph.end}\nids: {[f"{name}: {str(val)}" for (name, val) in self.graph.ids.items()]}</p></div>"
