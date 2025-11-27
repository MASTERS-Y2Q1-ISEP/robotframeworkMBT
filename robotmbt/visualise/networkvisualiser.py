import networkx as nx
from math import sqrt
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Rect, Text, Arrow, NormalHead, CustomJS
)
from bokeh.embed import file_html
from bokeh.resources import CDN


class NetworkVisualiser:
    """
    Clean implementation:
    - Level-based layout (BFS)
    - Sized rectangles from multi-line labels
    - Non-overlapping layout
    - Arrows connect at rectangle borders
    - Executed nodes/edges highlighted
    - Text scales when zooming
    """

    # Visual constants
    EXECUTED_NODE_COLOR = "#4C72B0"
    UNEXECUTED_NODE_COLOR = "#D3D3D3"
    EXECUTED_TEXT_COLOR = "#E8E8E8"
    UNEXECUTED_TEXT_COLOR = "#555555"

    EXECUTED_EDGE_COLOR = "#000000"
    UNEXECUTED_EDGE_COLOR = "#808080"
    EXECUTED_EDGE_WIDTH = 2.5
    UNEXECUTED_EDGE_WIDTH = 1.2
    EXECUTED_EDGE_ALPHA = 0.7
    UNEXECUTED_EDGE_ALPHA = 0.3

    ARROWHEAD_SIZE = 8

    NODE_MARGIN = 0.75  # padding between layers
    LAYER_Y_SPACING = 2.0  # vertical gap (could now be dynamic)
    NODE_X_SPACING = 3.0  # horizontal gap for multiple nodes in a level

    def __init__(self, graph):
        self.graph = graph
        self.G = graph.networkx
        self.root = "start"

        trace = graph.get_final_trace()
        self.executed_nodes = set(trace)
        self.executed_edges = {(trace[i], trace[i+1]) for i in range(len(trace)-1)}

        self.node_layout = {}
        self.node_props = {}

    # ============================================================
    # Layout
    # ============================================================

    def _compute_levels(self):
        """Assign BFS levels."""
        levels = {}
        for node in nx.bfs_tree(self.G, self.root):
            if node == self.root:
                levels[node] = 0
            else:
                preds = list(self.G.predecessors(node)) + list(self.G.successors(node))
                parent_level = min(levels[p] for p in preds if p in levels)
                levels[node] = parent_level + 1
        return levels

    def _measure_rect(self, text: str):
        """
        Compute rectangle width/height for multi-line text.
        Width = longest line, height = number of lines * line height + padding.
        """

        lines = text.split("\n")
        longest = max(len(line) for line in lines)
        num_lines = len(lines)

        char_w = 0.15  # width per character
        char_h = 0.50  # height per line
        margin_x = 0.40
        margin_y_top = 0.10
        margin_y_bottom = 0.10  # slightly more to avoid clipping

        width = longest * char_w + margin_x
        height = num_lines * char_h + margin_y_top + margin_y_bottom

        if text == "start":
            height = width

        return width, height

    def _compute_layout(self):
        levels = self._compute_levels()

        # group by level
        by_level = {}
        for node, lvl in levels.items():
            by_level.setdefault(lvl, []).append(node)

        self.node_layout = {}
        self.node_props = {}

        # Compute vertical positions dynamically
        layer_y_positions = {}
        current_y = 0  # start at top
        for lvl in sorted(by_level.keys()):
            nodes = by_level[lvl]

            # Compute max height in this level
            max_h = 0
            for n in nodes:
                w, h = self._measure_rect(self.G.nodes[n]["label"])
                max_h = max(max_h, h)
                self.node_props[n] = {"w": w, "h": h}

            # assign y for this level
            layer_y_positions[lvl] = current_y

            # next layer y = current y - max height - margin
            current_y -= max_h + self.NODE_MARGIN

        # Compute horizontal positions
        for lvl, nodes in by_level.items():
            nodes.sort()
            total_width = 0
            widths = []
            heights = []

            for n in nodes:
                label = self.G.nodes[n]["label"]
                w, h = self._measure_rect(label)
                widths.append(w)
                heights.append(h)
                self.node_props[n] = {"w": w, "h": h}

                total_width += widths[-1]

            # add spacing
            total_width += self.NODE_X_SPACING * (len(nodes) - 1)

            # center horizontally
            x_start = -total_width / 2
            x = x_start
            y = layer_y_positions[lvl]

            for i, n in enumerate(nodes):
                w = widths[i]
                h = heights[i]
                cx = x + w / 2
                cy = y - h / 2
                self.node_layout[n] = (cx, cy)
                self.node_props[n]["x"] = cx
                self.node_props[n]["y"] = cy
                x += widths[i] + self.NODE_X_SPACING

    # ============================================================
    # Geometry
    # ============================================================

    def _line_to_rect_border(self, x1, y1, x2, y2, w, h):
        """
        Intersection of line (x1,y1)->(x2,y2) with rectangle centered at (x2,y2).
        """
        dx = x2 - x1
        dy = y2 - y1
        L = sqrt(dx*dx + dy*dy)
        if L == 0:
            return x2, y2

        dx /= L
        dy /= L

        tx = (w/2) / abs(dx) if dx != 0 else float("inf")
        ty = (h/2) / abs(dy) if dy != 0 else float("inf")
        t = min(tx, ty)
        return x2 - dx*t, y2 - dy*t

    # ============================================================
    # Drawing
    # ============================================================

    def generate_html(self):
        self._compute_layout()

        fig = figure(width=800, height=800,
                     toolbar_location="right",
                     x_range=(-10, 10), y_range=(-20, 5))

        # --------------------------
        # Nodes
        # --------------------------
        rects = dict(x=[], y=[], w=[], h=[], color=[])
        label_data = dict(x=[], y=[], text=[], color=[])

        rects = dict(x=[], y=[], w=[], h=[], color=[])
        labels = dict(x=[], y=[], text=[], color=[])

        for node in self.G.nodes:
            label = self.G.nodes[node]["label"]
            x, y = self.node_layout[node]

            is_exec = node in self.executed_nodes
            color = self.EXECUTED_NODE_COLOR if is_exec else self.UNEXECUTED_NODE_COLOR
            text_color = self.EXECUTED_TEXT_COLOR if is_exec else self.UNEXECUTED_TEXT_COLOR

            if node == "start":
                w, h = self._measure_rect(label)
                diam = max(w, h)
                fig.circle(x=x, y=y, radius=diam/2, color=color)
                text_glyph = Text(
                    x="x", y="y",
                    text="text",
                    text_align="center",
                    text_baseline="middle",
                    text_color="color",
                    text_font_size="9pt"
                )
                text_glyph.tags = ["scalable_text"]
                fig.add_glyph(ColumnDataSource({"x": [x], "y": [y], "text": [label], "color": [text_color]}), text_glyph)
                self.node_props[node] = {
                    "diam": diam,
                    "w": diam,  # needed for arrow computation
                    "h": diam,
                }
            else:
                w = self.node_props[node]["w"]
                h = self.node_props[node]["h"]

                rects["x"].append(x)
                rects["y"].append(y)
                rects["w"].append(w)
                rects["h"].append(h)
                rects["color"].append(color)

                labels["x"].append(x - w / 2)  # left-aligned
                labels["y"].append(y)
                labels["text"].append(label)
                labels["color"].append(text_color)


        fig.rect("x", "y", "w", "h",
                 fill_color="color", line_color="black",
                 source=ColumnDataSource(rects))

        text_glyph = Text(
            x="x", y="y",
            text="text",
            text_align="left",
            text_baseline="middle",
            text_color="color",
            text_font_size="9pt"
        )
        text_glyph.tags = ["scalable_text"]

        fig.add_glyph(ColumnDataSource(labels), text_glyph)

        # --------------------------
        # Edges
        # --------------------------
        for u, v in self.G.edges:
            label = self.G[u][v].get("label")

            ux, uy = self.node_layout[u]
            vx, vy = self.node_layout[v]

            is_exec = (u, v) in self.executed_edges
            ec = self.EXECUTED_EDGE_COLOR if is_exec else self.UNEXECUTED_EDGE_COLOR
            ew = self.EXECUTED_EDGE_WIDTH if is_exec else self.UNEXECUTED_EDGE_WIDTH
            ea = self.EXECUTED_EDGE_ALPHA if is_exec else self.UNEXECUTED_EDGE_ALPHA

            # border positions
            ux2, uy2 = self._line_to_rect_border(vx, vy, ux, uy,
                                                 self.node_props[u]["w"],
                                                 self.node_props[u]["h"])
            vx2, vy2 = self._line_to_rect_border(ux, uy, vx, vy,
                                                 self.node_props[v]["w"],
                                                 self.node_props[v]["h"])

            fig.add_layout(Arrow(
                x_start=ux2, y_start=uy2,
                x_end=vx2, y_end=vy2,
                end=NormalHead(size=self.ARROWHEAD_SIZE,
                               fill_color=ec, line_color=ec),
                line_color=ec, line_width=ew, line_alpha=ea
            ))

            if label:
                mx, my = (ux2 + vx2) / 2, (uy2 + vy2) / 2
                edge_label = Text(
                    x="x", y="y", text="text",
                    text_align="center", text_baseline="middle",
                    text_color="black", text_font_size="7pt"
                )
                edge_label.tags = ["scalable_text"]
                fig.add_glyph(
                    ColumnDataSource(dict(x=[mx], y=[my], text=[label])),
                    edge_label
                )

        # ============================================================
        # Zoom-scaling for text (Bokeh 3.x API)
        # ============================================================

        # store initial span in tags
        fig.x_range.tags = [{"initial_span": fig.x_range.end - fig.x_range.start}]
        fig.y_range.tags = [{"initial_span": fig.y_range.end - fig.y_range.start}]

        zoom_cb = CustomJS(args=dict(xr=fig.x_range, yr=fig.y_range, plot=fig), code="""
            const xspan0 = xr.tags[0].initial_span;
            const yspan0 = yr.tags[0].initial_span;

            const xspan = xr.end - xr.start;
            const yspan = yr.end - yr.start;

            const zoom = Math.min(xspan0 / xspan, yspan0 / yspan);

            for (const r of plot.renderers) {
                if (r.glyph && r.glyph.tags && r.glyph.tags.includes("scalable_text")) {
                    const base = 9;  // base pt size
                    r.glyph.text_font_size = (base * zoom).toFixed(2) + "pt";
                }
            }
            plot.request_render();
        """)

        fig.x_range.js_on_change("start", zoom_cb)
        fig.x_range.js_on_change("end", zoom_cb)
        fig.y_range.js_on_change("start", zoom_cb)
        fig.y_range.js_on_change("end", zoom_cb)

        return file_html(fig, CDN, "graph")
