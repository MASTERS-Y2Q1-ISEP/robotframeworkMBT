from bokeh.core.property.vectorization import value
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, Rect, Text, ResetTool, SaveTool, WheelZoomTool, PanTool, Plot, Range1d, \
    Title, FullscreenTool

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


class NetworkVisualiser:
    def __init__(self, graph: AbstractGraph, suite_name: str):
        # Extract what we need from the graph
        self.networkx: DiGraph = graph.networkx
        self.final_trace = graph.get_final_trace()

        # Set up a Bokeh figure
        self.plot = Plot()

        # The ColumnDataSources to store our nodes and edges in Bokeh's format
        self.edge_source: ColumnDataSource = ColumnDataSource({'from': [], 'to': [], 'label': []})

        # Add the nodes to the graph
        self._add_nodes()

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

    def _add_nodes(self):
        # Temporary storage of all nodes and the total widths and heights of the different layers
        layers: dict[int, tuple[float, float]] = {}

        # The ColumnDataSources to store our nodes and edges in Bokeh's format
        node_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'w': [], 'h': [], 'color': []})
        node_label_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'label': []})
        nodes: list[Node] = []

        # Construct all nodes and calculate layer dimensions
        for node_id in self.networkx.nodes:
            nodes.append(self._create_node(node_id, layers))

        # Correctly position and add all nodes to the column data sources
        for node in nodes:
            _position_node_and_add_to_sources(node, layers, node_source, node_label_source)

        # Add the glyphs for nodes and their labels
        node_glyph = Rect(x='x', y='y', width='w', height='h', fill_color='color')
        self.plot.add_glyph(node_source, node_glyph)

        node_label_glyph = Text(x='x', y='y', text='label', text_align='left', text_baseline='middle',
                                text_font_size='16pt', text_font=value("Courier New"))
        self.plot.add_glyph(node_label_source, node_label_glyph)

    def _create_node(self, node_id: str, layers) -> Node:
        # Extract the label and distance of the node from start
        label = self.networkx.nodes[node_id]['label']
        layer = self.networkx.nodes[node_id]['distance']

        # Calculate the node dimensions based on the label
        w, h = _calculate_dimensions(label)

        # Update layer info
        if layer not in layers:
            x = 0
            layers[layer] = (w, h)
        else:
            (width, height) = layers[layer]
            x = width + HORIZONTAL_PADDING_BETWEEN_NODES
            width += w + HORIZONTAL_PADDING_BETWEEN_NODES
            layers[layer] = (width, max(height, h))

        # Construct node from information
        return Node(node_id, label, x, layer, w, h, node_id in self.final_trace)

    def _add_edges(self):
        pass


def _position_node_and_add_to_sources(node: Node, layers, node_source: ColumnDataSource,
                                      node_label_source: ColumnDataSource):
    # Calculate the correct y position based on all layers' heights
    y = 0
    for i in range(node.y + 1):
        (w, h) = layers[i]
        y -= h
        if i != node.y:
            y -= VERTICAL_PADDING_BETWEEN_NODES
        else:
            # Center on x and y
            node.x -= w / 2
            node.y = y + h / 2

    # Add to data source
    node_source.data['id'].append(node.node_id)
    node_source.data['x'].append(node.x + node.width / 2)
    node_source.data['y'].append(node.y)
    node_source.data['w'].append(node.width)
    node_source.data['h'].append(node.height)
    node_source.data['color'].append(FINAL_TRACE_NODE_COLOR if node.in_final_trace else OTHER_NODE_COLOR)

    node_label_source.data['id'].append(node.node_id)
    node_label_source.data['x'].append(node.x + HORIZONTAL_PADDING_WITHIN_NODES)
    node_label_source.data['y'].append(node.y)
    node_label_source.data['label'].append(node.label)


def _calculate_dimensions(label: str) -> tuple[float, float]:
    lines = label.splitlines()
    width = 0
    for line in lines:
        width = max(width, len(line) * 19.25)
    height = len(lines) * 43 - 9
    return width + 2 * HORIZONTAL_PADDING_WITHIN_NODES, height + 2 * VERTICAL_PADDING_WITHIN_NODES
