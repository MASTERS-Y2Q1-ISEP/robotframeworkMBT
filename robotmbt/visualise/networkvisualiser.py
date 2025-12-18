from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.reducedSDVgraph import ReducedSDVGraph
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
from robotmbt.visualise.graphs.stategraph import StateGraph
from bokeh.palettes import Spectral4
from bokeh.models import (
    Plot, Range1d, Circle, Rect,
    Arrow, NormalHead,
    Bezier, ColumnDataSource, ResetTool,
    SaveTool, WheelZoomTool, PanTool, Text,
    FullscreenTool, Title
)
from bokeh.layouts import column
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import networkx as nx

class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    ARROWHEAD_SIZE: int = 6
    EDGE_WIDTH: float = 2.0
    EDGE_ALPHA: float = 0.7
    EDGE_COLOUR: str | tuple[int, int, int] = (12, 12, 12)
    GRAPH_PADDING_PERC: int = 15  # %
    # in px, needs to be equal for height and width otherwise calculations are wrong
    GRAPH_SIZE_PX: int = 600
    LEGEND_HEIGHT_PX: int = 200
    MAX_VERTEX_NAME_LEN: int = 20  # number of characters

    # Colors and styles for executed vs unexecuted elements
    EXECUTED_NODE_COLOR = Spectral4[0]  # Bright blue
    UNEXECUTED_NODE_COLOR = '#D3D3D3'  # Light gray
    EXECUTED_TEXT_COLOR = '#C8C8C8'
    UNEXECUTED_TEXT_COLOR = '#A9A9A9'  # Dark gray
    EXECUTED_EDGE_COLOR = (12, 12, 12)  # Black
    UNEXECUTED_EDGE_COLOR = '#808080'  # Gray
    EXECUTED_EDGE_WIDTH = 2.5
    UNEXECUTED_EDGE_WIDTH = 1.2
    EXECUTED_EDGE_ALPHA = 0.7
    UNEXECUTED_EDGE_ALPHA = 0.3
    EXECUTED_LABEL_COLOR = 'black'
    UNEXECUTED_LABEL_COLOR = '#A9A9A9'

    def __init__(self, graph: AbstractGraph, suite_name: str = ""):
        self.plot = None
        self.graph = graph
        self.suite_name = suite_name
        self.node_props = {}  # Store node properties for arrow calculations
        self.graph_layout = {}

        # graph customisation options
        self.node_radius = 1.0
        self.char_width = 0.1
        self.char_height = 0.1
        self.padding = 0.1

        # Get executed elements for visual differentiation
        final_trace = graph.get_final_trace()
        self.executed_nodes = set(final_trace)
        self.executed_edges = set()
        for i in range(0, len(final_trace) - 1):
            from_node = final_trace[i]
            to_node = final_trace[i + 1]
            self.executed_edges.add((from_node, to_node))

    def generate_html(self) -> str:
        """
        Generate html file from networkx graph via Bokeh
        """
        self._calculate_graph_layout()
        self._initialise_plot()
        self._add_nodes_with_labels()
        self._add_edges()
        
        # Create legend using Bokeh components
        legend = self._create_bokeh_legend()
        
        # Create a column layout with plot and legend
        layout = column(self.plot, legend, sizing_mode='fixed')
        
        return file_html(layout, CDN, "graph")

    def _create_bokeh_legend(self):
        """
        Create a legend using only Bokeh components
        """
        y_padding = 10
        legend_height = self.LEGEND_HEIGHT_PX
        legend_width = self.GRAPH_SIZE_PX
        
        # Create a plot for the legend with no axes or tools
        legend_plot = Plot(
            width=legend_width,
            height=legend_height,
            x_range=Range1d(0, legend_width),
            y_range=Range1d(-y_padding, legend_height + y_padding), # Padding applied to prevent clipping at edges
            toolbar_location=None,
            outline_line_color='#dddddd',
            outline_line_width=1,
            background_fill_color='white',
            border_fill_color='white',
            min_border=10
        )
        
        # Remove grid and axes
        legend_plot.grid.visible = False
        legend_plot.axis.visible = False
        
        # Square properties for vertices
        square_x = 30
        square_width = 20
        square_left = square_x - square_width/2
        square_right = square_x + square_width/2
        
        # Y positions for legend items
        title_y = 180
        executed_square_y = 140
        unexecuted_square_y = 100
        executed_arrow_y = 60
        unexecuted_arrow_y = 20
        
        # Vertices
        vertex_source = ColumnDataSource(data=dict(
            x=[square_x, square_x],
            y=[executed_square_y, unexecuted_square_y],
            width=[square_width, square_width],
            height=[20, 20],
            fill_color=[self.EXECUTED_NODE_COLOR, self.UNEXECUTED_NODE_COLOR],
            line_color=['#333333', '#999999']
        ))
        
        # Vertex labels
        vertex_labels_source = ColumnDataSource(data=dict(
            x=[60, 60],
            y=[executed_square_y, unexecuted_square_y],
            text=[
                "Executed vertex (reached in final trace)",
                "Unexecuted vertex (not reached in final trace)"
            ]
        ))
        
        # Vertex rectangles
        vertices = Rect(x='x', y='y', width='width', height='height',
                    fill_color='fill_color', line_color='line_color',
                    line_width=1)
        legend_plot.add_glyph(vertex_source, vertices)
        
        # Vertex labels
        vertex_text = Text(x='x', y='y', text='text',
                        text_align='left', text_baseline='middle',
                        text_font_size='10pt', text_color='#333333')
        legend_plot.add_glyph(vertex_labels_source, vertex_text)
        
        # Executed edge arrow
        executed_arrow = Arrow(
            end=NormalHead(
                size=8,
                line_color=self.EXECUTED_EDGE_COLOR,
                fill_color=self.EXECUTED_EDGE_COLOR,
                line_width=self.EXECUTED_EDGE_WIDTH
            ),
            x_start=square_left,
            y_start=executed_arrow_y,
            x_end=square_right,
            y_end=executed_arrow_y,
            line_color=self.EXECUTED_EDGE_COLOR,
            line_width=self.EXECUTED_EDGE_WIDTH,
            line_alpha=self.EXECUTED_EDGE_ALPHA
        )
        legend_plot.add_layout(executed_arrow)
        
        # Unexecuted edge arrow
        unexecuted_arrow = Arrow(
            end=NormalHead(
                size=7,
                line_color=self.UNEXECUTED_EDGE_COLOR,
                fill_color=self.UNEXECUTED_EDGE_COLOR,
                line_width=self.UNEXECUTED_EDGE_WIDTH
            ),
            x_start=square_left,
            y_start=unexecuted_arrow_y,
            x_end=square_right,
            y_end=unexecuted_arrow_y,
            line_color=self.UNEXECUTED_EDGE_COLOR,
            line_width=self.UNEXECUTED_EDGE_WIDTH,
            line_alpha=self.UNEXECUTED_EDGE_ALPHA
        )
        legend_plot.add_layout(unexecuted_arrow)
        
        # Edge labels
        edge_labels_source = ColumnDataSource(data=dict(
            x=[60, 60],
            y=[executed_arrow_y, unexecuted_arrow_y],
            text=[
                "Executed edge (traversed in final trace)",
                "Unexecuted edge (not traversed in final trace)"
            ]
        ))
        
        edge_text = Text(x='x', y='y', text='text',
                        text_align='left', text_baseline='middle',
                        text_font_size='10pt', text_color='#333333')
        legend_plot.add_glyph(edge_labels_source, edge_text)
        
        # Legend title
        title_source = ColumnDataSource(data=dict(
            x=[legend_width / 2],
            y=[title_y],
            text=["Legend"]
        ))
        
        title_text = Text(x='x', y='y', text='text',
                        text_align='center', text_baseline='middle',
                        text_font_size='11pt', text_font_style='bold',
                        text_color='#333333')
        legend_plot.add_glyph(title_source, title_text)
        
        return legend_plot

    def _initialise_plot(self):
        """
        Define plot with width, height, x_range, y_range and enable tools.
        x_range and y_range are padded. Plot needs to be a square
        """
        padding: float = self.GRAPH_PADDING_PERC / 100

        x_range, y_range = zip(*self.graph_layout.values())
        x_min = min(x_range) - padding * (max(x_range) - min(x_range))
        x_max = max(x_range) + padding * (max(x_range) - min(x_range))
        y_min = min(y_range) - padding * (max(y_range) - min(y_range))
        y_max = max(y_range) + padding * (max(y_range) - min(y_range))

        # scale node radius based on range
        nodes_range = max(x_max - x_min, y_max - y_min)
        self.node_radius = nodes_range / 150
        self.char_width = nodes_range / 150
        self.char_height = nodes_range / 150

        # create plot
        x_range = Range1d(min(x_min, y_min), max(x_max, y_max))
        y_range = Range1d(min(x_min, y_min), max(x_max, y_max))

        self.plot = Plot(width=self.GRAPH_SIZE_PX,
                         height=self.GRAPH_SIZE_PX,
                         x_range=x_range,
                         y_range=y_range)

        # add title
        self.plot.add_layout(Title(text=self.suite_name, align="center"), "above")

        # add tools
        self.plot.add_tools(ResetTool(), SaveTool(),
                            WheelZoomTool(), PanTool(),
                            FullscreenTool())

    def _calculate_text_dimensions(self, text: str) -> tuple[float, float]:
        """Calculate width and height needed for text based on actual text length"""
        # Calculate width based on character count
        text_length = len(text)
        width = (text_length * self.char_width) + (2 * self.padding)

        # Reduced height for more compact rectangles
        height = self.char_height + self.padding

        return width, height

    def _add_nodes_with_labels(self):
        """
        Add nodes with text labels inside them
        """
        node_labels = nx.get_node_attributes(self.graph.networkx, "label")

        # Create data sources for nodes and labels
        circle_data = dict(x=[], y=[], radius=[], label=[], color=[], text_color=[])
        rect_data = dict(x=[], y=[], width=[], height=[], label=[], color=[], text_color=[])
        text_data = dict(x=[], y=[], text=[], text_color=[])

        for node in self.graph.networkx.nodes:
            # Labels are always defined and cannot be lists
            label = node_labels[node]
            label = self._cap_name(label)
            x, y = self.graph_layout[node]

            # Determine if node is executed
            is_executed = node in self.executed_nodes
            node_color = self.EXECUTED_NODE_COLOR if is_executed else self.UNEXECUTED_NODE_COLOR
            text_color = self.EXECUTED_TEXT_COLOR if is_executed else self.UNEXECUTED_TEXT_COLOR

            if node == self.graph.start_node:
                # For start node (circle), calculate radius based on text width
                text_width, text_height = self._calculate_text_dimensions(
                    label)
                # Calculate radius from text dimensions
                radius = (text_width / 2.5)

                circle_data['x'].append(x)
                circle_data['y'].append(y)
                circle_data['radius'].append(radius)
                circle_data['label'].append(label)
                circle_data['color'].append(node_color)
                circle_data['text_color'].append(text_color)

                # Store node properties for arrow calculations
                self.node_props[node] = {
                    'type': 'circle', 'x': x, 'y': y, 'radius': radius, 'label': label}

            else:
                # For scenario nodes (rectangles), calculate dimensions based on text
                text_width, text_height = self._calculate_text_dimensions(
                    label)

                rect_data['x'].append(x)
                rect_data['y'].append(y)
                rect_data['width'].append(text_width)
                rect_data['height'].append(text_height)
                rect_data['label'].append(label)
                rect_data['color'].append(node_color)
                rect_data['text_color'].append(text_color)

                # Store node properties for arrow calculations
                self.node_props[node] = {'type': 'rect', 'x': x, 'y': y, 'width': text_width, 'height': text_height,
                                         'label': label}

            # Add text for all nodes
            text_data['x'].append(x)
            text_data['y'].append(y)
            text_data['text'].append(label)
            text_data['text_color'].append(text_color)

        # Add circles for start node
        if circle_data['x']:
            circle_source = ColumnDataSource(circle_data)
            circles = Circle(x='x', y='y', radius='radius',
                             fill_color='color', line_color='color')
            self.plot.add_glyph(circle_source, circles)

        # Add rectangles for scenario nodes
        if rect_data['x']:
            rect_source = ColumnDataSource(rect_data)
            rectangles = Rect(x='x', y='y', width='width', height='height',
                              fill_color='color', line_color='color')
            self.plot.add_glyph(rect_source, rectangles)

        # Add text labels for all nodes
        text_source = ColumnDataSource(text_data)
        text_labels = Text(x='x', y='y', text='text',
                           text_align='center', text_baseline='middle',
                           text_color='text_color', text_font_size='9pt')
        self.plot.add_glyph(text_source, text_labels)

    def _get_edge_points(self, start_node, end_node):
        """Calculate edge start and end points at node borders"""
        start_props = self.node_props.get(start_node)
        end_props = self.node_props.get(end_node)

        # Node properties should always exist
        if not start_props or not end_props:
            raise ValueError(
                f"Node properties not found for nodes: {start_node}, {end_node}")

        # Calculate direction vector
        dx = end_props['x'] - start_props['x']
        dy = end_props['y'] - start_props['y']
        distance = sqrt(dx * dx + dy * dy)

        # Self-loops are handled separately, distance should never be 0
        if distance == 0:
            raise ValueError(
                "Distance between different nodes should not be zero")

        # Normalize direction vector
        dx /= distance
        dy /= distance

        # Calculate start point at border
        if start_props['type'] == 'circle':
            start_x = start_props['x'] + dx * start_props['radius']
            start_y = start_props['y'] + dy * start_props['radius']
        else:
            # Find where the line intersects the rectangle border
            rect_width = start_props['width']
            rect_height = start_props['height']

            # Calculate scaling factors for x and y directions
            scale_x = rect_width / (2 * abs(dx)) if dx != 0 else float('inf')
            scale_y = rect_height / (2 * abs(dy)) if dy != 0 else float('inf')

            # Use the smaller scale to ensure we hit the border
            scale = min(scale_x, scale_y)

            start_x = start_props['x'] + dx * scale
            start_y = start_props['y'] + dy * scale

        # Calculate end point at border (reverse direction)
        # End nodes should never be circles for regular edges
        if end_props['type'] == 'circle':
            raise ValueError(
                f"End node should not be a circle for regular edges: {end_node}")
        else:
            rect_width = end_props['width']
            rect_height = end_props['height']

            # Calculate scaling factors for x and y directions (reverse)
            scale_x = rect_width / (2 * abs(dx)) if dx != 0 else float('inf')
            scale_y = rect_height / (2 * abs(dy)) if dy != 0 else float('inf')

            # Use the smaller scale to ensure we hit the border
            scale = min(scale_x, scale_y)

            end_x = end_props['x'] - dx * scale
            end_y = end_props['y'] - dy * scale

        return start_x, start_y, end_x, end_y

    def add_self_loop(self, node_id: str):
        """
        Circular arc that starts and ends at the top side of the rectangle
        Start at 1/4 width, end at 3/4 width, with a circular arc above
        The arc itself ends with the arrowhead pointing into the rectangle
        """
        # Get node properties directly by node ID
        node_props = self.node_props.get(node_id)

        # Node properties should always exist
        if node_props is None:
            raise ValueError(f"Node properties not found for node: {node_id}")

        # Self-loops should only be for rectangle nodes (scenarios)
        if node_props['type'] != 'rect':
            raise ValueError(
                f"Self-loops should only be for rectangle nodes, got: {node_props['type']}")

        x, y = node_props['x'], node_props['y']
        width = node_props['width']
        height = node_props['height']

        # Start: 1/4 width from left, top side
        start_x = x - width / 4
        start_y = y + height / 2

        # End: 3/4 width from left, top side
        end_x = x + width / 4
        end_y = y + height / 2

        # Arc height above the rectangle
        arc_height = width * 0.4

        # Control points for a circular arc above
        control1_x = x - width / 8
        control1_y = y + height / 2 + arc_height

        control2_x = x + width / 8
        control2_y = y + height / 2 + arc_height

        # Determine if edge is executed
        is_executed = (node_id, node_id) in self.executed_edges
        edge_color = self.EXECUTED_EDGE_COLOR if is_executed else self.UNEXECUTED_EDGE_COLOR
        edge_width = self.EXECUTED_EDGE_WIDTH if is_executed else self.UNEXECUTED_EDGE_WIDTH
        edge_alpha = self.EXECUTED_EDGE_ALPHA if is_executed else self.UNEXECUTED_EDGE_ALPHA

        # Create the Bezier curve (the main arc) with the same thickness as straight lines
        loop = Bezier(
            x0=start_x, y0=start_y,
            x1=end_x, y1=end_y,
            cx0=control1_x, cy0=control1_y,
            cx1=control2_x, cy1=control2_y,
            line_color=edge_color,
            line_width=edge_width,
            line_alpha=edge_alpha,
        )
        self.plot.add_glyph(loop)

        # Calculate the tangent direction at the end of the Bezier curve
        # For a cubic Bezier, the tangent at the end point is from the last control point to the end point
        tangent_x = end_x - control2_x
        tangent_y = end_y - control2_y

        # Normalize the tangent vector
        tangent_length = sqrt(tangent_x ** 2 + tangent_y ** 2)
        if tangent_length > 0:
            tangent_x /= tangent_length
            tangent_y /= tangent_length

        # Add just the arrowhead (NormalHead) at the end point, oriented along the tangent
        arrowhead = NormalHead(
            size=NetworkVisualiser.ARROWHEAD_SIZE,
            line_color=edge_color,
            fill_color=edge_color,
            line_width=edge_width
        )

        # Create a standalone arrowhead at the end point
        # Strategy: use a very short Arrow that's essentially just the head
        arrow = Arrow(
            end=arrowhead,
            x_start=end_x - tangent_x * 0.001,  # Almost zero length line
            y_start=end_y - tangent_y * 0.001,
            x_end=end_x,
            y_end=end_y,
            line_color=edge_color,
            line_width=edge_width,
            line_alpha=edge_alpha
        )
        self.plot.add_layout(arrow)

        # Add edge label - positioned above the arc
        label_x = x
        label_y = y + height / 2 + arc_height * 0.6

        return label_x, label_y

    def _add_edges(self):
        edge_labels = nx.get_edge_attributes(self.graph.networkx, "label")

        # Create data sources for edges and edge labels
        edge_text_data = dict(x=[], y=[], text=[], text_color=[])

        for edge in self.graph.networkx.edges():
            # Edge labels are always defined and cannot be lists
            edge_label = edge_labels[edge]
            edge_label = self._cap_name(edge_label)

            # Determine if edge is executed
            is_executed = edge in self.executed_edges
            edge_color = self.EXECUTED_EDGE_COLOR if is_executed else self.UNEXECUTED_EDGE_COLOR
            edge_width = self.EXECUTED_EDGE_WIDTH if is_executed else self.UNEXECUTED_EDGE_WIDTH
            edge_alpha = self.EXECUTED_EDGE_ALPHA if is_executed else self.UNEXECUTED_EDGE_ALPHA
            label_color = self.EXECUTED_LABEL_COLOR if is_executed else self.UNEXECUTED_LABEL_COLOR

            edge_text_data['text'].append(edge_label)
            edge_text_data['text_color'].append(label_color)

            if edge[0] == edge[1]:
                # Self-loop handled separately
                label_x, label_y = self.add_self_loop(edge[0])
                edge_text_data['x'].append(label_x)
                edge_text_data['y'].append(label_y)

            else:
                # Calculate edge points at node borders
                start_x, start_y, end_x, end_y = self._get_edge_points(
                    edge[0], edge[1])

                # Add arrow between the calculated points
                arrow = Arrow(
                    end=NormalHead(
                        size=NetworkVisualiser.ARROWHEAD_SIZE,
                        line_color=edge_color,
                        fill_color=edge_color,
                        line_width=edge_width),
                    x_start=start_x, y_start=start_y,
                    x_end=end_x, y_end=end_y,
                    line_color=edge_color,
                    line_width=edge_width,
                    line_alpha=edge_alpha
                )
                self.plot.add_layout(arrow)

                # Collect edge label data (position at midpoint)
                edge_text_data['x'].append((start_x + end_x) / 2)
                edge_text_data['y'].append((start_y + end_y) / 2)

        # Add all edge labels at once
        if edge_text_data['x']:
            edge_text_source = ColumnDataSource(edge_text_data)
            edge_labels_glyph = Text(x='x', y='y', text='text',
                                     text_align='center', text_baseline='middle',
                                     text_color='text_color', text_font_size='7pt')
            self.plot.add_glyph(edge_text_source, edge_labels_glyph)

    def _cap_name(self, name: str) -> str:
        if len(name) < self.MAX_VERTEX_NAME_LEN or isinstance(self.graph, StateGraph) \
                or isinstance(self.graph, ScenarioStateGraph) or isinstance(self.graph, ScenarioDeltaValueGraph)\
                or isinstance(self.graph, ReducedSDVGraph):
            return name

        return f"{name[:(self.MAX_VERTEX_NAME_LEN - 3)]}..."

    def _calculate_graph_layout(self):
        try:
            self.graph_layout = nx.bfs_layout(
                self.graph.networkx, self.graph.start_node, align='horizontal')
            # horizontal mirror
            for node in self.graph_layout:
                self.graph_layout[node] = (self.graph_layout[node][0],
                                           -1 * self.graph_layout[node][1])
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.graph_layout = nx.arf_layout(self.graph.networkx, seed=42)
