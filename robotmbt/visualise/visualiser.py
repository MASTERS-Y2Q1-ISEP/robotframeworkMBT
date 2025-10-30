from .models import ScenarioGraph, TraceInfo, ScenarioInfo
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx, show
from bokeh.models import (
    Plot, Range1d, Circle, MultiLine,
    HoverTool, BoxZoomTool, ResetTool,
    Arrow, NormalHead, LabelSet, Bezier, ColumnDataSource
)
from math import sqrt


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
        networkvisualiser.generate_html()
        return f""
        # return f"<div><p>nodes: {self.graph.nodes}\nedges: {self.graph.edges}\nstart: {self.graph.start}\nend: {self.graph.end}\nids: {[f"{name}: {str(val)}" for (name, val) in self.graph.ids.items()]}</p></div>"


class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    def __init__(self, graph: ScenarioGraph):
        self.plot = None
        self.vertex_radius = 1
        self.graph = graph

    def generate_html(self):
        self.initialise_plot()
        for src, dst in self.graph.networkx.edges():
            x0, y0 = self.graph.pos[src]
            x1, y1 = self.graph.pos[dst]
            if src == dst:
                self.add_self_loop(x=x0, y=y0)
            else:
                self.add_arrow(x0=x0, y0=y0, x1=x1, y1=y1)

        self.draw_from_networkx()
        self.add_labels()
        show(self.plot)

    def initialise_plot(self):
        """
        Define plot based on range of coordinates of the vertices.
        Enable tools
        """
        x_range, y_range = zip(*self.graph.pos.values())
        x_min = min(x_range) - 0.1 * (max(x_range) - min(x_range))
        x_max = max(x_range) + 0.1 * (max(x_range) - min(x_range))
        y_min = min(y_range) - 0.1 * (max(y_range) - min(y_range))
        y_max = max(y_range) + 0.1 * (max(y_range) - min(y_range))

        vertices_range = max(x_max-x_min, y_max-y_min)
        self.vertex_radius = vertices_range / 50

        self.plot = Plot(width=800, height=800,
                         x_range=Range1d(x_min, x_max),
                         y_range=Range1d(y_min, y_max))
        self.plot.add_tools(HoverTool(tooltips=None),
                            BoxZoomTool(), ResetTool())

    def add_labels(self):
        # add labels to nodes
        x_cords = []
        y_cords = []
        labels = []
        for vertex in self.graph.networkx.nodes:
            x_cords.append(self.graph.pos[vertex][0])
            y_cords.append(self.graph.pos[vertex][1]+self.vertex_radius/2)
            labels.append(self.graph.networkx.nodes[vertex]['label'])

        label_source = ColumnDataSource(
            dict(x=x_cords, y=y_cords, label=labels))
        labels = LabelSet(x="x", y="y", text="label", source=label_source,
                          text_color="black", text_align="center")
        self.plot.add_layout(labels)

    def draw_from_networkx(self):
        graph_renderer = from_networkx(self.graph.networkx, self.graph.pos)
        graph_renderer.node_renderer.glyph = Circle(
            radius=self.vertex_radius, fill_color=Spectral4[0])
        graph_renderer.edge_renderer.glyph = MultiLine(
            line_color="black", line_alpha=0.6, line_width=2)
        self.plot.renderers.append(graph_renderer)

    def add_self_loop(self, x: float, y: float):
        # Self-loop as a curved Bezier arsc
        loop = Bezier(
            x0=x,
            y0=y-self.vertex_radius,
            x1=x+self.vertex_radius,
            y1=y,
            # control points
            cx0=x,
            cy0=y-5*self.vertex_radius,
            cx1=x + 5*self.vertex_radius,
            cy1=y,
            # styling
            line_color="red", line_width=2, line_alpha=0.7
        )
        self.plot.add_glyph(loop)
        # Optional arrowhead on the loop (small VeeHead at the end)
        # arrow = Arrow(end=VeeHead(size=10, line_color="red", fill_color="red"),
        #               x_start=x0 + 0.1, y_start=y0 + 0.05,
        #               x_end=x0, y_end=y0)
        # graph.add_layout(arrow)

    def add_arrow(self, x0: float, y0: float, x1: float, y1: float):
        # Normal directed edge
        dx = x1 - x0
        dy = y1 - y0
        length = sqrt(dx**2 + dy**2)
        arrow = Arrow(end=NormalHead(size=10, line_color="black", fill_color="black"),
                      x_start=x0 + dx / length * self.vertex_radius,
                      y_start=y0 + dy / length * self.vertex_radius,
                      x_end=x1 - dx / length * self.vertex_radius,
                      y_end=y1 - dy / length * self.vertex_radius)
        self.plot.add_layout(arrow)
