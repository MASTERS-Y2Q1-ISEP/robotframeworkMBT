from .models import ScenarioGraph, TraceInfo, ScenarioInfo
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh.models import (
    Plot, Range1d, Circle,
    HoverTool, ResetTool,
    Arrow, NormalHead, LabelSet, Bezier, ColumnDataSource,
    SaveTool, WheelZoomTool, PanTool
)
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import html


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide
    a simple interface through which the graph can be updated,
    and retrieved in HTML format.
    """
    GRAPH_WIDTH_PX: int = 600  # in px
    GRAPH_HEIGHT_PX: int = 400  # in px
    GRAPH_PADDING_PERC: int = 15  # %
    MAX_VERTEX_NAME_LEN: int = 20  # no. of characters

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
        str = f"<iframe srcdoc=\"{html.escape(html_bokeh)}\", width=\"{Visualiser.GRAPH_WIDTH_PX}px\", height=\"{Visualiser.GRAPH_HEIGHT_PX}px\"></iframe>"

        return str


class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    EDGE_WIDTH: float = 2.0
    EDGE_ALPHA: float = 0.7
    EDGE_COLOUR: str | tuple[int, int, int] = (
        12, 12, 12)  # 'visual studio black'

    def __init__(self, graph: ScenarioGraph):
        self.plot = None
        self.graph = graph

        # graph customisation options
        self.node_radius = 1.0

    def generate_html(self) -> str:
        """
        Generate html file from networkx graph via Bokeh
        """
        self.initialise_plot()

        for src, dst in self.graph.networkx.edges():
            x0, y0 = self.graph.pos[src]
            x1, y1 = self.graph.pos[dst]
            if src == dst:
                self.add_self_loop(x=x0, y=y0)
            else:
                self.add_arrow(x0=x0, y0=y0, x1=x1, y1=y1)

        self.add_nodes()
        return file_html(self.plot, CDN, "graph")

    def initialise_plot(self):
        """
        Define plot with width, height, x_range, y_range and enable tools.
        x_range and y_range are padded. Plot needs to be a square
        """
        padding: float = Visualiser.GRAPH_PADDING_PERC / 100

        x_range, y_range = zip(*self.graph.pos.values())
        x_min = min(x_range) - padding * (max(x_range) - min(x_range))
        x_max = max(x_range) + padding * (max(x_range) - min(x_range))
        y_min = min(y_range) - padding * (max(y_range) - min(y_range))
        y_max = max(y_range) + padding * (max(y_range) - min(y_range))

        # scale node radius based on range
        nodes_range = max(x_max-x_min, y_max-y_min)
        self.node_radius = nodes_range / 50

        # create plot
        x_range = Range1d(min(x_min, y_min), max(x_max, y_max))
        y_range = Range1d(min(x_min, y_min), max(x_max, y_max))

        self.plot = Plot(width=Visualiser.GRAPH_WIDTH_PX,
                         height=Visualiser.GRAPH_HEIGHT_PX,
                         x_range=x_range,
                         y_range=y_range)

        # add tools
        self.plot.add_tools(ResetTool(), SaveTool(),
                            WheelZoomTool(), PanTool())

    def add_nodes(self):
        """
        Add labels to the nodes in bokeh plot
        """

        x_cords = []
        y_cords = []
        labels = []
        for node in self.graph.networkx.nodes:
            x_cords.append(self.graph.pos[node][0])
            y_cords.append(self.graph.pos[node][1]+self.node_radius)
            labels.append(
                self._cap_name(self.graph.networkx.nodes[node]['label'])
            )

            bokeh_node = Circle(radius=self.node_radius,
                                fill_color=Spectral4[0],
                                x=self.graph.pos[node][0],
                                y=self.graph.pos[node][1])

            self.plot.add_glyph(bokeh_node)

        label_source = ColumnDataSource(
            dict(x=x_cords, y=y_cords, label=labels)
        )

        labels = LabelSet(x="x", y="y", text="label", source=label_source,
                          text_color=NetworkVisualiser.EDGE_COLOUR,
                          text_align="center")

        self.plot.add_layout(labels)

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
            line_color=NetworkVisualiser.EDGE_COLOUR,
            line_width=NetworkVisualiser.EDGE_WIDTH,
            line_alpha=NetworkVisualiser.EDGE_ALPHA,
        )
        self.plot.add_glyph(loop)

        # add arrow head
        arrow = Arrow(
            end=NormalHead(size=10,
                           line_color=NetworkVisualiser.EDGE_COLOUR,
                           fill_color=NetworkVisualiser.EDGE_COLOUR),

            # -0.01 to guarantee that arrow points upwards.
            x_start=x, y_start=y-self.node_radius-0.01,
            x_end=x, y_end=y-self.node_radius
        )

        self.plot.add_layout(arrow)

    def add_arrow(self, x0: float, y0: float, x1: float, y1: float):
        """
        Add arrowhead to edge
        """
        dx = x1 - x0
        dy = y1 - y0
        length = sqrt(dx**2 + dy**2)  # she dx on my dy till I pythagoras

        arrow = Arrow(
            end=NormalHead(
                size=10,
                line_color=NetworkVisualiser.EDGE_COLOUR,
                fill_color=NetworkVisualiser.EDGE_COLOUR),

            x_start=x0 + dx / length * self.node_radius,
            y_start=y0 + dy / length * self.node_radius,
            x_end=x1 - dx / length * self.node_radius,
            y_end=y1 - dy / length * self.node_radius
        )

        self.plot.add_layout(arrow)

    @staticmethod
    def _cap_name(name: str) -> str:
        if len(name) < Visualiser.MAX_VERTEX_NAME_LEN:
            return name

        return f"{name[:(Visualiser.MAX_VERTEX_NAME_LEN-3)]}..."
