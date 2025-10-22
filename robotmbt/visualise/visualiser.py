from .models import ScenarioGraph, TraceInfo, ScenarioInfo
from math import sqrt
import plotly.graph_objects as go


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide a simple interface through which the graph can be updated, and retrieved in HTML format.
    """

    def __init__(self):
        self.graph = ScenarioGraph()
        self.node_size = 30

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_start(self, scenario: ScenarioInfo):
        self.graph.set_starting_node(scenario)

    def set_end(self, scenario: ScenarioInfo):
        self.graph.set_ending_node(scenario)

    def generate_graph(self, edge_trace: go.Scatter, node_trace: go.Scatter, arrow_annotations: list[dict]):
        annotations = [dict(
            xref="paper", yref="paper",
            x=0.005, y=-0.002)] + arrow_annotations

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
        fig.show()

    def generate_edge_trace(self) -> tuple[go.Scatter, list[dict]]:
        edge_x = []
        edge_y = []
        arrow_annotations = []

        for edge in self.graph.networkx.edges:
            # get x, y coordinates
            x0, y0 = self.graph.pos[edge[0]]
            x1, y1 = self.graph.pos[edge[1]]

            # None acts as seperator for between edges
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

            # add arrow annotation

            dx = x1 - x0
            dy = y1 - y0
            edge_length = sqrt(dx**2 + dy**2)

            dotSizeConversion = .01  # length units per dot size
            node_size = self.node_size * dotSizeConversion
            arrow_annotations.append(
                dict(
                    # tail of the arrow
                    ax=x0 + dx / edge_length * node_size,
                    ay=y0 + dy / edge_length * node_size,
                    # head of the arrow
                    x=x1 - dx / edge_length * node_size,
                    y=y1 - dy / edge_length * node_size,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=3,
                    arrowsize=1.5,
                    arrowwidth=1.5,
                    arrowcolor='#333'
                )
            )

        # generate scatter from x, y coordinates of all edges
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.5, color='#333'),
            hoverinfo='none',
            mode='lines')

        return edge_trace, arrow_annotations

    def generate_node_trace(self) -> go.Scatter:
        node_x = []
        node_y = []
        text = []
        for node, pos in self.graph.pos.items():
            x, y = pos
            node_x.append(x)
            node_y.append(y)
            if node != 'start':
                text.append(self.graph.ids[node])
            else:
                text.append('')

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=text,
            textposition="top center",
            textfont_size=10,
            mode='markers+text',
            hoverinfo='none',
            marker=dict(
                color='#00F',
                size=self.node_size,
                line_width=2))

        return node_trace

    def generate_html(self) -> str:
        self.graph.calculate_pos()
        edge_trace, arrow_annotations = self.generate_edge_trace()
        node_trace = self.generate_node_trace()
        self.generate_graph(edge_trace, node_trace, arrow_annotations)
        return f""
        # return f"<div><p>nodes: {self.graph.nodes}\nedges: {self.graph.edges}\nstart: {self.graph.start}\nend: {self.graph.end}\nids: {[f"{name}: {str(val)}" for (name, val) in self.graph.ids.items()]}</p></div>"
