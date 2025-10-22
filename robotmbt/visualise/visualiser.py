from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState
import networkx as nx
import matplotlib.pyplot as plt
#numpy
#scipy


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
        return f"Scen{self.src_id}: {self.name}"


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

        # The networkx graph is a directional graph
        self.networkx = nx.DiGraph()

        # Stores the position (x, y) of the nodes
        self.pos = {}

        # List of nodes which positions cannot be changed
        self.fixed = []

        # add the start node
        self.networkx.add_node('start')

    """
    Update the visualisation with new trace information from another exploration step.
    This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
    """
    def update_visualisation(self, info: TraceInfo):
        for i in range(0, len(info.trace) - 1):
            from_node = self.__get_or_create_id(info.trace[i])
            to_node = self.__get_or_create_id(info.trace[i + 1])

            if from_node not in self.networkx.nodes:
                self.networkx.add_node(from_node, text=self.ids[from_node].name)
            if to_node not in self.networkx.nodes:
                self.networkx.add_node(to_node, text=self.ids[to_node].name)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(from_node, to_node)

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
        node = self.__get_or_create_id(scenario)
        self.networkx.add_edge('start', node)

    """
    Update the end node.
    """
    def set_ending_node(self, scenario: ScenarioInfo):
        node = self.__get_or_create_id(scenario)
        self.pos[node] = (len(self.networkx.nodes), 0)
        self.fixed.append(node)

    """
    Calculate the position (x, y) for all nodes in self.networkx
    """
    def calculate_pos(self):
        self.pos['start'] = (0, len(self.networkx.nodes))
        self.fixed.append('start')
        if not self.fixed:
            self.pos = nx.spring_layout(self.networkx, seed=42)
        else:
            self.pos = nx.spring_layout(self.networkx, pos=self.pos, fixed=self.fixed, seed=42, method='energy', gravity=0.25)


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

    def generate_networkx_graph(self):
        # temporary code for visualisation  
        self.graph.calculate_pos()
        nx.draw(self.graph.networkx, pos=self.graph.pos, with_labels=True, node_color="lightblue", node_size=600)
        plt.show()

    # TODO: use a graph library to actually create a graph
    def generate_html(self) -> str:
        self.generate_networkx_graph()
        return f""
        # return f"<div><p>nodes: {self.graph.nodes}\nedges: {self.graph.edges}\nstart: {self.graph.start}\nend: {self.graph.end}\nids: {[f"{name}: {str(val)}" for (name, val) in self.graph.ids.items()]}</p></div>"
