from .models import ScenarioGraph, StateGraph, TraceInfo
from bokeh.palettes import Spectral4
from bokeh.models import (
    Plot, Range1d, Circle,
    Arrow, NormalHead, LabelSet,
    Bezier, ColumnDataSource, ResetTool,
    SaveTool, WheelZoomTool, PanTool,
    PointDrawTool, CustomJS, MultiLine, GlyphRenderer,
)
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import html
import networkx as nx


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide
    a simple interface through which the graph can be updated,
    and retrieved in HTML format.
    """
    GRAPH_SIZE_PX: int = 600  # in px, needs to be equal for height and width otherwise calculations are wrong
    GRAPH_PADDING_PERC: int = 15  # %
    MAX_VERTEX_NAME_LEN: int = 20  # no. of characters

    def __init__(self):
        self.graph = StateGraph()

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_final_trace(self, info: TraceInfo):
        self.graph.set_final_trace(info)

    def generate_visualisation(self) -> str:
        self.graph.calculate_pos()
        networkvisualiser = NetworkVisualiser(self.graph)
        html_bokeh = networkvisualiser.generate_html()
        return f"<iframe srcdoc=\"{html.escape(html_bokeh)}\", width=\"{Visualiser.GRAPH_SIZE_PX}px\", height=\"{Visualiser.GRAPH_SIZE_PX}px\"></iframe>"


class NetworkVisualiser:
    EDGE_WIDTH: float = 2.0
    EDGE_ALPHA: float = 0.7
    EDGE_COLOUR: str | tuple[int, int, int] = (12, 12, 12)  # Visual Studio black

    def __init__(self, graph: ScenarioGraph):
        self.plot = None
        self.graph = graph
        self.labels = dict(x=[], y=[], label=[])
        self.label_source = None
        self.node_radius = 1.0

    def generate_html(self) -> str:
        self._initialise_plot()
        node_renderer, node_source = self._add_nodes()
        self._add_edges(node_source)
        draw_tool = PointDrawTool(renderers=[node_renderer], empty_value='black', add=False)
        self.plot.add_tools(draw_tool)
        self.plot.toolbar.active_drag = draw_tool

        labels = LabelSet(x="x", y="y", text="label", source=self.label_source,
                          text_color=NetworkVisualiser.EDGE_COLOUR,
                          text_align="center")
        self.plot.add_layout(labels)

        return file_html(self.plot, CDN, "graph")

    def _initialise_plot(self):
        padding: float = Visualiser.GRAPH_PADDING_PERC / 100
        x_range, y_range = zip(*self.graph.pos.values())
        x_min = min(x_range) - padding * (max(x_range) - min(x_range))
        x_max = max(x_range) + padding * (max(x_range) - min(x_range))
        y_min = min(y_range) - padding * (max(y_range) - min(y_range))
        y_max = max(y_range) + padding * (max(y_range) - min(y_range))

        nodes_range = max(x_max - x_min, y_max - y_min)
        self.node_radius = nodes_range / 50

        self.plot = Plot(width=Visualiser.GRAPH_SIZE_PX,
                         height=Visualiser.GRAPH_SIZE_PX,
                         x_range=Range1d(min(x_min, y_min), max(x_max, y_max)),
                         y_range=Range1d(min(x_min, y_min), max(x_max, y_max)))
        self.plot.add_tools(ResetTool(), SaveTool(), WheelZoomTool(), PanTool())

    def _add_nodes(self):
        node_data = dict(
            id=[n for n in self.graph.networkx.nodes],
            x=[self.graph.pos[n][0] for n in self.graph.networkx.nodes],
            y=[self.graph.pos[n][1] for n in self.graph.networkx.nodes],
            label=[self._cap_name(self.graph.networkx.nodes[n].get("label", "")) for n in self.graph.networkx.nodes],
        )
        node_source = ColumnDataSource(node_data)

        node_renderer = self.plot.add_glyph(node_source,
                                            Circle(radius=self.node_radius, fill_color=Spectral4[0]))

        # store labels for node and edge placement
        self.labels['x'].extend(node_data['x'])
        self.labels['y'].extend([y + self.node_radius for y in node_data['y']])
        self.labels['label'].extend(node_data['label'])

        return node_renderer, node_source

    def _add_edges(self, node_source: ColumnDataSource):
        edges = list(self.graph.networkx.edges())
        xs, ys, edge_labels = [], [], []

        for start, end in edges:
            x0, y0 = self.graph.pos[start]
            x1, y1 = self.graph.pos[end]
            xs.append([x0, x1])
            ys.append([y0, y1])
            edge_labels.append(self._cap_name(self.graph.networkx.edges[start, end].get("label", "")))

        edge_source = ColumnDataSource(data=dict(
            xs=xs, ys=ys, start=[s for s, _ in edges], end=[t for _, t in edges]
        ))

        edge_renderer = GlyphRenderer(data_source=edge_source,
                                      glyph=MultiLine(xs="xs", ys="ys",
                                                      line_color=NetworkVisualiser.EDGE_COLOUR,
                                                      line_width=NetworkVisualiser.EDGE_WIDTH,
                                                      line_alpha=NetworkVisualiser.EDGE_ALPHA))
        self.plot.renderers.append(edge_renderer)

        # arrows
        arrows = []
        for start, end in edges:
            arrow = Arrow(
                end=NormalHead(size=10,
                               line_color=NetworkVisualiser.EDGE_COLOUR,
                               fill_color=NetworkVisualiser.EDGE_COLOUR),
                x_start=self.graph.pos[start][0],
                y_start=self.graph.pos[start][1],
                x_end=self.graph.pos[end][0],
                y_end=self.graph.pos[end][1],
            )
            self.plot.add_layout(arrow)
            arrows.append(arrow)
        edge_source.data["arrows"] = arrows

        # labels: node + edge labels
        self.label_source = ColumnDataSource(data=dict(
            x=self.labels["x"] + [(x0+x1)/2 for x0, x1 in xs],
            y=self.labels["y"] + [(y0+y1)/2 for y0, y1 in ys],
            label=self.labels["label"] + edge_labels
        ))

        # JS callback to update everything dynamically
        update_edges = CustomJS(args=dict(
            node_source=node_source,
            edge_source=edge_source,
            label_source=self.label_source,
            plot=self.plot
        ), code="""
        const node_data = node_source.data;
        const edge_data = edge_source.data;
        const label_data = label_source.data;
        const xmap = {}, ymap = {};
        for (let i = 0; i < node_data.id.length; i++) {
            xmap[node_data.id[i]] = node_data.x[i];
            ymap[node_data.id[i]] = node_data.y[i];
        }

        // edges + arrows
        for (let i = 0; i < edge_data.start.length; i++) {
            const s = edge_data.start[i];
            const e = edge_data.end[i];
            edge_data.xs[i] = [xmap[s], xmap[e]];
            edge_data.ys[i] = [ymap[s], ymap[e]];
            const arrow = edge_data.arrows[i];
            arrow.x_start = xmap[s];
            arrow.y_start = ymap[s];
            arrow.x_end = xmap[e];
            arrow.y_end = ymap[e];
        }

        // node labels
        for (let i = 0; i < node_data.id.length; i++) {
            label_data.x[i] = node_data.x[i];
            label_data.y[i] = node_data.y[i] + 0.05;
        }

        // edge labels
        const offset = node_data.id.length;
        for (let i = 0; i < edge_data.start.length; i++) {
            const s = edge_data.start[i];
            const e = edge_data.end[i];
            label_data.x[i + offset] = (xmap[s] + xmap[e]) / 2;
            label_data.y[i + offset] = (ymap[s] + ymap[e]) / 2;
        }

        edge_source.change.emit();
        label_source.change.emit();
        plot.request_render();
        """)

        node_source.js_on_change("data", update_edges)


    @staticmethod
    def _cap_name(name: str) -> str:
        # TODO: cap name only if scenario graph
        # And figure out how to make large graphs readable with long states
        return name
        if len(name) < Visualiser.MAX_VERTEX_NAME_LEN:
            return name

        return f"{name[:(Visualiser.MAX_VERTEX_NAME_LEN-3)]}..."
