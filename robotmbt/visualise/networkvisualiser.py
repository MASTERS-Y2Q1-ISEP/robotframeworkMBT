from bokeh.core.property.vectorization import value
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, Rect, Text, ResetTool, SaveTool, WheelZoomTool, PanTool, Plot, Range1d, \
    Title, FullscreenTool

from grandalf.graphs import Vertex as GVertex, Edge as GEdge, Graph as GGraph
from grandalf.layouts import SugiyamaLayout

from networkx import DiGraph
from robot.api import logger

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph

# Padding between different nodes
HORIZONTAL_PADDING_BETWEEN_NODES = 50
VERTICAL_PADDING_BETWEEN_NODES = 50

# Padding within the nodes between the borders and inner text
HORIZONTAL_PADDING_WITHIN_NODES = 5
VERTICAL_PADDING_WITHIN_NODES = 5

# Colors for different parts of the graph
FINAL_TRACE_NODE_COLOR = '#CCCC00'
OTHER_NODE_COLOR = '#999989'

# Dimensions of the plot in the window
INNER_WINDOW_WIDTH = 846
INNER_WINDOW_HEIGHT = 882


def generate_html(graph: AbstractGraph, suite_name: str) -> str:
    return NetworkVisualiser(graph, suite_name).generate_html()


class Node:
    def __init__(self, node_id: str, label: str, x: int, y: int, width: float, height: float, in_final_trace: bool):
        self.node_id = node_id
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.in_final_trace = in_final_trace


class Edge:
    def __init__(self, from_node: str, to_node: str, points: list[tuple[float, float]]):
        self.from_node = from_node
        self.to_node = to_node
        self.points = points


class NetworkVisualiser:
    def __init__(self, graph: AbstractGraph, suite_name: str):
        # Extract what we need from the graph
        self.networkx: DiGraph = graph.networkx
        self.final_trace = graph.get_final_trace()

        # Set up a Bokeh figure
        self.plot = Plot()

        # Sugiyama
        nodes, edges = self._create_layout()

        # Add the nodes to the graph
        self._add_nodes(nodes)

        # Add the edges to the graph
        self._add_edges()

        # add title
        self.plot.add_layout(Title(text=suite_name, align="center"), "above")

        # Add the different tools
        self.plot.add_tools(ResetTool(), SaveTool(),
                            WheelZoomTool(), PanTool(),
                            FullscreenTool())

        # Specify the default range - these values represent the aspect ratio of the actual view in the window
        self.plot.x_range = Range1d(-INNER_WINDOW_WIDTH / 2, INNER_WINDOW_WIDTH / 2)
        self.plot.y_range = Range1d(-INNER_WINDOW_HEIGHT + VERTICAL_PADDING_BETWEEN_NODES,
                                    VERTICAL_PADDING_BETWEEN_NODES)

    def generate_html(self):
        return file_html(self.plot, 'inline', "graph")

    def _add_nodes(self, nodes: list[Node]):
        # The ColumnDataSources to store our nodes and edges in Bokeh's format
        node_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'w': [], 'h': [], 'color': []})
        node_label_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'label': []})

        # Add all nodes to the column data sources
        for node in nodes:
            _add_node_to_sources(node, node_source, node_label_source)

        # Add the glyphs for nodes and their labels
        node_glyph = Rect(x='x', y='y', width='w', height='h', fill_color='color')
        self.plot.add_glyph(node_source, node_glyph)

        node_label_glyph = Text(x='x', y='y', text='label', text_align='left', text_baseline='middle',
                                text_font_size='16pt', text_font=value("Courier New"))
        self.plot.add_glyph(node_label_source, node_label_glyph)

    def _add_edges(self):
        # The ColumnDataSources to store our edges in Bokeh's format
        edge_source: ColumnDataSource = ColumnDataSource({'from': [], 'to': [], 'label': []})
        # TODO

    def _create_layout(self) -> tuple[list[Node], list[Edge]]:
        vertices = []
        edges = []
        flips = []

        start = None
        for node_id in self.networkx.nodes:
            v = GVertex(node_id)
            w, h = _calculate_dimensions(self.networkx.nodes[node_id]['label'])
            v.view = NodeView(w, h)
            vertices.append(v)
            if node_id == 'start':
                start = v

        flip = _flip_edges([e for e in self.networkx.edges])

        for (from_id, to_id) in self.networkx.edges:
            from_node = _find_node(vertices, from_id)
            to_node = _find_node(vertices, to_id)
            e = GEdge(from_node, to_node)
            e.view = EdgeView()
            edges.append(e)
            if (from_id, to_id) in flip:
                flips.append(e)

        g = GGraph(vertices, edges)

        sugiyama = SugiyamaLayout(g.C[0])
        sugiyama.init_all(roots=[start], inverted_edges=flips)
        sugiyama.draw()

        ns = []
        for v in g.C[0].sV:
            node_id = v.data
            label = self.networkx.nodes[node_id]['label']
            (x, y) = v.view.xy
            (w, h) = _calculate_dimensions(label)
            ns.append(Node(node_id, label, x, y, w, h, False))

        es = []
        for e in g.C[0].sE:
            from_id = e.v[0]
            to_id = e.v[1]
            points = e.view.points
            es.append(Edge(from_id, to_id, points))

        return ns, es


class NodeView:
    def __init__(self, width: float, height: float):
        self.w, self.h = width, height
        self.xy = (0, 0)


class EdgeView:
    def __init__(self):
        self.points = []

    def setpath(self, points: list[tuple[float, float]]):
        self.points = points


def _find_node(nodes: list[GVertex], node_id: str):
    for node in nodes:
        if node.data == node_id:
            return node
    return None


def _add_node_to_sources(node: Node, node_source: ColumnDataSource, node_label_source: ColumnDataSource):
    # Add to data source
    node_source.data['id'].append(node.node_id)
    node_source.data['x'].append(node.x)
    node_source.data['y'].append(-node.y)
    node_source.data['w'].append(node.width)
    node_source.data['h'].append(node.height)
    node_source.data['color'].append(FINAL_TRACE_NODE_COLOR if node.in_final_trace else OTHER_NODE_COLOR)

    node_label_source.data['id'].append(node.node_id)
    node_label_source.data['x'].append(node.x - node.width / 2 + HORIZONTAL_PADDING_WITHIN_NODES)
    node_label_source.data['y'].append(-node.y)
    node_label_source.data['label'].append(node.label)


def _calculate_dimensions(label: str) -> tuple[float, float]:
    lines = label.splitlines()
    width = 0
    for line in lines:
        width = max(width, len(line) * 19.25)
    height = len(lines) * 43 - 9
    return width + 2 * HORIZONTAL_PADDING_WITHIN_NODES, height + 2 * VERTICAL_PADDING_WITHIN_NODES


def _flip_edges(edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    # Step 1: Build adjacency list from edges
    adj = {}
    for u, v in edges:
        if u not in adj:
            adj[u] = []
        adj[u].append(v)

    # Step 2: Helper function to detect cycles
    def dfs(node, visited, rec_stack, cycle_edges):
        visited[node] = True
        rec_stack[node] = True

        if node in adj:
            for neighbor in adj[node]:
                edge = (node, neighbor)

                if not visited.get(neighbor, False):
                    if dfs(neighbor, visited, rec_stack, cycle_edges):
                        cycle_edges.append(edge)
                elif rec_stack.get(neighbor, False):
                    # Found a cycle, add the edge to the cycle_edges list
                    cycle_edges.append(edge)

        rec_stack[node] = False
        return False

    # Step 3: Detect cycles
    visited = {}
    rec_stack = {}
    cycle_edges = []

    for node in adj:
        if not visited.get(node, False):
            dfs(node, visited, rec_stack, cycle_edges)

    # Step 4: Return the list of edges that need to be flipped
    # In this case, the cycle_edges are the ones that we need to "break" by flipping
    return cycle_edges
