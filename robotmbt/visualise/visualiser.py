import graphviz

from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState


"""
This contains all information we need from scenarios, abstracting away from the actual Scenario class:
- name
- src_id
"""
class ScenarioInfo:
    name: str
    src_id: int | None

    def __init__(self, scenario: Scenario | str):
        if isinstance(scenario, Scenario):
            self.name = scenario.name
            self.src_id = scenario.src_id
        else:
            self.name = scenario
            self.src_id = None

    def __str__(self):
        return f"({self.src_id}) {self.name}"


"""
This contains all information we need at any given step in trace exploration:
- trace: the strung together scenarios up until this point
- state: the model space
"""
class TraceInfo:
    trace: list[ScenarioInfo] = []
    # TODO: actually use state
    state: ModelSpace = None

    def __init__(self, trace: TraceState, state: ModelSpace):
        self.trace = [ScenarioInfo(s) for s in trace.get_trace()]
        self.state = state


"""
The scenario graph is the most basic representation of trace exploration.
It represents scenarios as nodes, and the trace as edges.
"""
class ScenarioGraph:
    def __init__(self):
        # We use simplified IDs for nodes, and store the actual scenario info here
        self.ids: dict[str, ScenarioInfo] = {}

        # The nodes are simply a list of IDs
        self.nodes: list[str] = []

        # The edges are simply a list of ID pairs
        self.edges: list[tuple[str, str]] = []

        # The start and end nodes are stored as well
        self.start: str | None = None
        self.end: str | None = None

    """
    Update the visualisation with new trace information from another exploration step.
    This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
    """
    def update_visualisation(self, info: TraceInfo):
        for i in range(0, len(info.trace) - 1):
            from_node = self.__get_or_create_id(info.trace[i])
            to_node = self.__get_or_create_id(info.trace[i + 1])

            if not self.nodes:
                self.nodes = [from_node, to_node]
            else:
                if from_node not in self.nodes:
                    self.nodes.append(from_node)
                if to_node not in self.nodes:
                    self.nodes.append(to_node)

            if not self.edges:
                self.edges = [(from_node, to_node)]
            elif (from_node, to_node) not in self.edges:
                self.edges.append((from_node, to_node))

    """
    Get the ID for a scenario that has been added before, or create and store a new one.
    """
    def __get_or_create_id(self, scenario: ScenarioInfo) -> str:
        for i in self.ids.keys():
            # TODO: decide how to deal with repeating scenarios, this merges repeated scenarios into a single scenario
            if self.ids[i].src_id == scenario.src_id:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = scenario
        return new_id

    """
    Update the starting node.
    """
    def set_starting_node(self, scenario: ScenarioInfo):
        self.start = self.__get_or_create_id(scenario)

    """
    Update the end node.
    """
    def set_ending_node(self, scenario: ScenarioInfo):
        self.end = self.__get_or_create_id(scenario)


"""
The Visualiser class bridges the different concerns to provide a simple interface through which the graph can be updated, and retrieved in HTML format.
"""
class Visualiser:
    def __init__(self):
        self.graph = ScenarioGraph()

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_start(self, scenario: ScenarioInfo):
        self.graph.set_starting_node(scenario)

    def set_end(self, scenario: ScenarioInfo):
        self.graph.set_ending_node(scenario)

    # TODO: use proper graph library instead of dot
    def generate_html(self) -> str:
        dot = 'digraph ScenarioGraph {\n'
        dot += '  node [shape=box, style=filled, fillcolor=lightblue];\n'

        for node_id in self.graph.nodes:
            scenario = self.graph.ids[node_id]
            label = str(scenario)

            color = "lightblue"
            if node_id == self.graph.start:
                color = "green"
            elif node_id == self.graph.end:
                color = "red"

            dot += f'  "{node_id}" [label="{label}", fillcolor="{color}"];\n'

        for from_node, to_node in self.graph.edges:
            dot += f'  "{from_node}" -> "{to_node}";\n'

        dot += '}\n'

        graph = graphviz.Source(dot, format="svg")
        svg_data = graph.pipe().decode("utf-8")

        return f"""
        <div style="width: 100%; overflow-x: auto;">
            {svg_data}
        </div>
        """
