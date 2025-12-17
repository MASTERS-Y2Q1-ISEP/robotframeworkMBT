from bokeh.core.property.vectorization import value
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, Rect, Text, ResetTool, SaveTool, WheelZoomTool, PanTool, Plot, Range1d, \
    Title, FullscreenTool, CustomJS, Segment, Arrow, NormalHead

from grandalf.graphs import Vertex as GVertex, Edge as GEdge, Graph as GGraph
from grandalf.layouts import SugiyamaLayout

from networkx import DiGraph

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


class Node:
    def __init__(self, node_id: str, label: str, x: int, y: int, width: float, height: float):
        self.node_id = node_id
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Edge:
    def __init__(self, from_node: str, to_node: str, label: str, points: list[tuple[float, float]]):
        self.from_node = from_node
        self.to_node = to_node
        self.label = label
        self.points = points


class NetworkVisualiser:
    def __init__(self, graph: AbstractGraph, suite_name: str):
        # Extract what we need from the graph
        self.networkx: DiGraph = graph.networkx
        self.final_trace = graph.get_final_trace()
        self.start = graph.start_node

        # Set up a Bokeh figure
        self.plot = Plot()

        # Create Sugiyama layout
        nodes, edges = self._create_layout()

        # Add the nodes to the graph
        self._add_nodes(nodes)

        # Add the edges to the graph
        self._add_edges(nodes, edges)

        # Add our features to the graph (e.g. tools)
        self._add_features(suite_name)

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
            if isinstance(node.node_id, frozenset):
                node_id = tuple(sorted(node.node_id))
            else:
                node_id = node.node_id
            node_source.data['id'].append(node_id)
            node_source.data['x'].append(node.x)
            node_source.data['y'].append(-node.y)
            node_source.data['w'].append(node.width)
            node_source.data['h'].append(node.height)
            node_source.data['color'].append(
                FINAL_TRACE_NODE_COLOR if node.node_id in self.final_trace else OTHER_NODE_COLOR)

            node_label_source.data['id'].append(node_id)
            node_label_source.data['x'].append(node.x - node.width / 2 + HORIZONTAL_PADDING_WITHIN_NODES)
            node_label_source.data['y'].append(-node.y)
            node_label_source.data['label'].append(node.label)

        # Add the glyphs for nodes and their labels
        node_glyph = Rect(x='x', y='y', width='w', height='h', fill_color='color')
        self.plot.add_glyph(node_source, node_glyph)

        node_label_glyph = Text(x='x', y='y', text='label', text_align='left', text_baseline='middle',
                                text_font_size='16pt', text_font=value("Courier New"))
        node_label_glyph.tags = ["scalable_text16"]
        self.plot.add_glyph(node_label_source, node_label_glyph)

    def _add_edges(self, nodes: list[Node], edges: list[Edge]):
        # The ColumnDataSources to store our edges in Bokeh's format
        edge_part_source: ColumnDataSource = ColumnDataSource(
            {'from': [], 'to': [], 'start_x': [], 'start_y': [], 'end_x': [], 'end_y': []})
        edge_arrow_source: ColumnDataSource = ColumnDataSource(
            {'from': [], 'to': [], 'start_x': [], 'start_y': [], 'end_x': [], 'end_y': []})
        edge_label_source: ColumnDataSource = ColumnDataSource({'from': [], 'to': [], 'x': [], 'y': [], 'label': []})

        for edge in edges:
            start_x, start_y = 0, 0
            end_x, end_y = 0, 0
            if isinstance(edge.from_node, frozenset):
                from_id = tuple(sorted(edge.from_node))
            else:
                from_id = edge.from_node
            if isinstance(edge.to_node, frozenset):
                to_id = tuple(sorted(edge.to_node))
            else:
                to_id = edge.to_node
            # Add edges going through the calculated points
            for i in range(len(edge.points) - 1):
                start_x, start_y = edge.points[i]
                end_x, end_y = edge.points[i + 1]

                # Collect possibilities where the edge can start and end
                if i == 0:
                    from_possibilities = _get_connection_coordinates(nodes, edge.from_node)
                else:
                    from_possibilities = [(start_x, start_y)]

                if i == len(edge.points) - 2:
                    to_possibilities = _get_connection_coordinates(nodes, edge.to_node)
                else:
                    to_possibilities = [(end_x, end_y)]

                # Choose connection points that minimize edge length
                start_x, start_y, end_x, end_y = _minimize_distance(from_possibilities, to_possibilities)

                if i < len(edge.points) - 2:
                    # Middle part of edge without arrow
                    edge_part_source.data['from'].append(from_id)
                    edge_part_source.data['to'].append(to_id)
                    edge_part_source.data['start_x'].append(start_x)
                    edge_part_source.data['start_y'].append(-start_y)
                    edge_part_source.data['end_x'].append(end_x)
                    edge_part_source.data['end_y'].append(-end_y)
                else:
                    # End of edge with arrow
                    edge_arrow_source.data['from'].append(from_id)
                    edge_arrow_source.data['to'].append(to_id)
                    edge_arrow_source.data['start_x'].append(start_x)
                    edge_arrow_source.data['start_y'].append(-start_y)
                    edge_arrow_source.data['end_x'].append(end_x)
                    edge_arrow_source.data['end_y'].append(-end_y)

            # Add the label
            edge_label_source.data['from'].append(from_id)
            edge_label_source.data['to'].append(to_id)
            edge_label_source.data['x'].append((start_x + end_x) / 2)
            edge_label_source.data['y'].append(- (start_y + end_y) / 2)
            edge_label_source.data['label'].append(edge.label)

        # Add the glyphs for edges and their labels
        edge_part_glyph = Segment(x0='start_x', y0='start_y', x1='end_x', y1='end_y')
        self.plot.add_glyph(edge_part_source, edge_part_glyph)

        arrow_layout = Arrow(
            end=NormalHead(size=10),
            x_start='start_x', y_start='start_y',
            x_end='end_x', y_end='end_y',
            source=edge_arrow_source
        )
        self.plot.add_layout(arrow_layout)

        edge_label_glyph = Text(x='x', y='y', text='label', text_align='center', text_baseline='middle',
                                text_font_size='8pt', text_font=value("Courier New"))
        edge_label_glyph.tags = ["scalable_text8"]
        self.plot.add_glyph(edge_label_source, edge_label_glyph)

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
            if node_id == self.start:
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
            ns.append(Node(node_id, label, x, y, w, h))

        es = []
        for e in g.C[0].sE:
            from_id = e.v[0].data
            to_id = e.v[1].data
            label = self.networkx.edges[(from_id, to_id)]['label']
            points = e.view.points
            es.append(Edge(from_id, to_id, label, points))

        return ns, es

    def _add_features(self, suite_name: str):
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
        self.plot.x_range.tags = [{"initial_span": INNER_WINDOW_WIDTH}]
        self.plot.y_range.tags = [{"initial_span": INNER_WINDOW_HEIGHT}]

        zoom_cb = CustomJS(args=dict(xr=self.plot.x_range, yr=self.plot.y_range, plot=self.plot), code="""
            const xspan0 = xr.tags[0].initial_span;
            const yspan0 = yr.tags[0].initial_span;

            const xspan = xr.end - xr.start;
            const yspan = yr.end - yr.start;

            const zoom = Math.min(xspan0 / xspan, yspan0 / yspan);

            for (const r of plot.renderers) {
                if (r.glyph && r.glyph.tags && r.glyph.tags.includes("scalable_text16")) {
                    const base = 16;  // base pt size
                    r.glyph.text_font_size = (base * zoom).toFixed(2) + "pt";
                }
                if (r.glyph && r.glyph.tags && r.glyph.tags.includes("scalable_text8")) {
                    const base = 8;  // base pt size
                    r.glyph.text_font_size = (base * zoom).toFixed(2) + "pt";
                }
            }
            plot.request_render();
        """)

        self.plot.x_range.js_on_change("start", zoom_cb)
        self.plot.x_range.js_on_change("end", zoom_cb)
        self.plot.y_range.js_on_change("start", zoom_cb)
        self.plot.y_range.js_on_change("end", zoom_cb)


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


def _get_connection_coordinates(nodes: list[Node], node_id: str) -> list[tuple[float, float]]:
    start_possibilities = []

    # Get node from list
    node = None
    for n in nodes:
        if n.node_id == node_id:
            node = n
            break

    # Left
    start_possibilities.append((node.x - node.width / 2, node.y))
    # Right
    start_possibilities.append((node.x + node.width / 2, node.y))
    # Bottom
    start_possibilities.append((node.x, node.y - node.height / 2))
    # Top
    start_possibilities.append((node.x, node.y + node.height / 2))
    # Left bottom
    start_possibilities.append((node.x - node.width / 2, node.y - node.height / 2))
    # Left top
    start_possibilities.append((node.x - node.width / 2, node.y + node.height / 2))
    # Right bottom
    start_possibilities.append((node.x + node.width / 2, node.y - node.height / 2))
    # Right top
    start_possibilities.append((node.x + node.width / 2, node.y + node.height / 2))

    return start_possibilities


def _minimize_distance(from_pos, to_pos) -> tuple[float, float, float, float]:
    min_dist = -1
    fx, fy, tx, ty = 0, 0, 0, 0

    # Calculate the distance between all permutations
    for fp in from_pos:
        for tp in to_pos:
            distance = (fp[0] - tp[0]) ** 2 + (fp[1] - tp[1]) ** 2
            if min_dist == -1 or distance < min_dist:
                min_dist = distance
                fx, fy, tx, ty = fp[0], fp[1], tp[0], tp[1]

    # Return the permutation with the shortest distance
    return fx, fy, tx, ty

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
