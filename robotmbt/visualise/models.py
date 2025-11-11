from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState
import networkx as nx


class ScenarioInfo:
    """
    This contains all information we need from scenarios, abstracting away from the actual Scenario class:
    - name
    - src_id
    """

    def __init__(self, scenario: Scenario | str):
        if isinstance(scenario, Scenario):
            self.name = scenario.name
            self.src_id = scenario.src_id
        else:
            self.name = scenario
            self.src_id = None

    def __str__(self):
        return f"Scen{self.src_id}: {self.name}"


class StateInfo:
    """
    This contains all information we need from states, abstracting away from the actual ModelSpace class:
    - domain
    - properties
    """

    def __init__(self, state: ModelSpace):
        self.domain = state.ref_id
        self.properties = {}
        for p in state.props:
            if p == 'scenario':
                self.properties['scenario'] = {}
                for attr, value in state.props['scenario']:
                    self.properties['scenario'][attr] = value
                continue
            self.properties[p] = {}
            for attr in dir(state.props[p]):
                self.properties[p][attr] = getattr(state.props[p], attr)

    def __eq__(self, other):
        return self.domain == other.domain and self.properties == other.properties

    def __str__(self):
        res = ""
        for p in self.properties:
            res += f"{p}:\n"
            for k, v in self.properties[p].items():
                res += f"\t{k}={v}\n"
        return res


class TraceInfo:
    """
    This contains all information we need at any given step in trace exploration:
    - trace: the strung together scenarios up until this point
    - state: the model space
    """

    def __init__(self, trace: TraceState, state: ModelSpace):
        self.trace = [ScenarioInfo(s) for s in trace.get_trace()]
        self.state = StateInfo(state)


class ScenarioGraph:
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

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
        self.networkx.add_node('start', label='start')

    def update_visualisation(self, info: TraceInfo):
        """
        Update the visualisation with new trace information from another exploration step.
        This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
        """
        for i in range(0, len(info.trace) - 1):
            from_node = self.__get_or_create_id(info.trace[i])
            to_node = self.__get_or_create_id(info.trace[i + 1])

            self.__add_node(from_node)
            self.__add_node(to_node)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(
                    from_node, to_node, label='')

    def __get_or_create_id(self, scenario: ScenarioInfo) -> str:
        """
        Get the ID for a scenario that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            # TODO: decide how to deal with repeating scenarios, this merges repeated scenarios into a single scenario
            if self.ids[i].src_id == scenario.src_id:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = scenario
        return new_id

    def __add_node(self, node: str):
        """
        Add node if it doesn't already exist
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=self.ids[node].name)

    def __set_starting_node(self, scenario: ScenarioInfo):
        """
        Update the starting node.
        """
        node = self.__get_or_create_id(scenario)
        self.__add_node(node)
        self.networkx.add_edge('start', node, label='')

    def __set_ending_node(self, scenario: ScenarioInfo):
        """
        Update the end node.
        """
        node = self.__get_or_create_id(scenario)
        self.fixed.append(node)

    def set_final_trace(self, info: TraceInfo):
        """
        Update the graph with information on the final trace.
        """
        self.__set_starting_node(info.trace[0])
        self.__set_ending_node(info.trace[-1])

    def calculate_pos(self):
        """
        Calculate the position (x, y) for all nodes in self.networkx
        """
        try:
            self.pos = nx.planar_layout(self.networkx)
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.pos = nx.arf_layout(self.networkx, seed=42)
