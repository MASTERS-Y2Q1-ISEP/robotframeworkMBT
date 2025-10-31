from .models import ScenarioGraph, TraceInfo, ScenarioInfo
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh.models import (
    Plot, Range1d, Circle, MultiLine,
    HoverTool, BoxZoomTool, ResetTool,
    Arrow, NormalHead, LabelSet, Bezier, ColumnDataSource
)
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import html


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

    def generate_visualisation(self) -> str:
        self.graph.calculate_pos()
        networkvisualiser = NetworkVisualiser(self.graph)
        html_bokeh = networkvisualiser.generate_html()
        str = f"<iframe srcdoc=\"{html.escape(html_bokeh)}\", width=\"400\", height=\"400\"></iframe>"

        return str


class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    def __init__(self, graph: ScenarioGraph):
        self.plot = None
        self.graph = graph

        # graph customisation options
        self.edge_color = "black"
        self.node_radius = 1.0

    def generate_html(self) -> str:
        """
        Generate html file from networkx graph via Bokeh
        """
        self.initialise_plot()

        self.draw_from_networkx()

        for src, dst in self.graph.networkx.edges():
            x0, y0 = self.graph.pos[src]
            x1, y1 = self.graph.pos[dst]
            if src == dst:
                self.add_self_loop(x=x0, y=y0)
            else:
                self.add_arrow(x0=x0, y0=y0, x1=x1, y1=y1)

        self.add_labels()
        return file_html(self.plot, CDN, "graph")

    def initialise_plot(self):
        """
        Define plot based on range of coordinates of the nodes.
        Enable tools
        """
        x_range, y_range = zip(*self.graph.pos.values())
        x_min = min(x_range) - 0.1 * (max(x_range) - min(x_range))
        x_max = max(x_range) + 0.1 * (max(x_range) - min(x_range))
        y_min = min(y_range) - 0.1 * (max(y_range) - min(y_range))
        y_max = max(y_range) + 0.1 * (max(y_range) - min(y_range))

        # scale node radius based on range
        nodes_range = max(x_max-x_min, y_max-y_min)
        self.node_radius = nodes_range / 50

        # create plot
        range = Range1d(min(x_min, y_min), max(x_max, y_max))

        self.plot = Plot(width=400, height=400,
                         x_range=range,
                         y_range=range)

        # add tools
        self.plot.add_tools(HoverTool(tooltips=None),
                            BoxZoomTool(), ResetTool())

    def add_labels(self):
        """
        Add labels to the nodes in bokeh plot
        """
        x_cords = []
        y_cords = []
        labels = []
        for node in self.graph.networkx.nodes:
            x_cords.append(self.graph.pos[node][0])
            y_cords.append(self.graph.pos[node][1]+self.node_radius)
            labels.append(self.graph.networkx.nodes[node]['label'])

        label_source = ColumnDataSource(
            dict(x=x_cords, y=y_cords, label=labels))
        labels = LabelSet(x="x", y="y", text="label", source=label_source,
                          text_color="black", text_align="center")
        self.plot.add_layout(labels)

    def draw_from_networkx(self):
        """
        Render graph from networkx and stylise nodes and eges
        """
        graph_renderer = from_networkx(self.graph.networkx, self.graph.pos)
        graph_renderer.node_renderer.glyph = Circle(
            radius=self.node_radius, fill_color=Spectral4[0])
        graph_renderer.edge_renderer.glyph = MultiLine(
            line_color=self.edge_color, line_alpha=0.7, line_width=2)
        self.plot.renderers.append(graph_renderer)

    def add_self_loop(self, x: float, y: float):
        """
        Self-loop as a Bezier curve with arrow head
        """
        loop = Bezier(
            # starting point
            x0=x + self.node_radius,
            y0=y,
            # end point
            x1=x,
            y1=y - self.node_radius,
            # control points
            cx0=x + 5*self.node_radius,
            cy0=y,
            cx1=x,
            cy1=y - 5*self.node_radius,
            # styling
            line_color=self.edge_color,
            line_width=2,
            line_alpha=0.7
        )
        self.plot.add_glyph(loop)

        # add arrow head
        arrow = Arrow(end=NormalHead(size=10, line_color=self.edge_color, fill_color=self.edge_color),
                      x_start=x,
                      y_start=y-self.node_radius-0.01,
                      x_end=x,
                      y_end=y-self.node_radius)
        self.plot.add_layout(arrow)

    def add_arrow(self, x0: float, y0: float, x1: float, y1: float):
        """
        Add arrowhead to edge
        """
        dx = x1 - x0
        dy = y1 - y0
        length = sqrt(dx**2 + dy**2)
        arrow = Arrow(end=NormalHead(size=10, line_color=self.edge_color, fill_color=self.edge_color),
                      x_start=x0 + dx / length * self.node_radius,
                      y_start=y0 + dy / length * self.node_radius,
                      x_end=x1 - dx / length * self.node_radius,
                      y_end=y1 - dy / length * self.node_radius)
        self.plot.add_layout(arrow)
