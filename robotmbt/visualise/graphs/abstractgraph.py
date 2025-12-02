from abc import ABC, abstractmethod
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
import networkx as nx


class AbstractGraph(ABC):
    def __init__(self, info: TraceInfo):
        # The underlying storage - a NetworkX DiGraph
        self.networkx = nx.DiGraph()

        # Keep track of node IDs
        self.ids = {}

        # Add the start node
        self.networkx.add_node('start', label='start')

        # Add nodes and edges for all traces
        for trace in info.all_traces:
            for i in range(len(trace)):
                if i > 0:
                    from_node = self._get_or_create_id(self.select_node_info(trace[i - 1]))
                else:
                    from_node = 'start'
                to_node = self._get_or_create_id(self.select_node_info(trace[i]))
                self._add_node(from_node)
                self._add_node(to_node)
                self.networkx.add_edge(from_node, to_node,
                                       label=self.create_edge_label(self.select_edge_info(trace[i])))

        # Set the final trace and add any missing nodes/edges
        self.final_trace = ['start']
        for i in range(len(info.current_trace)):
            if i > 0:
                from_node = self._get_or_create_id(self.select_node_info(info.current_trace[i - 1]))
            else:
                from_node = 'start'
            to_node = self._get_or_create_id(self.select_node_info(info.current_trace[i]))
            self.final_trace.append(to_node)
            self._add_node(from_node)
            self._add_node(to_node)
            self.networkx.add_edge(from_node, to_node,
                                   label=self.create_edge_label(self.select_edge_info(info.current_trace[i])))

    def get_final_trace(self) -> list[str]:
        """
        Get the final trace as ordered node ids.
        Edges are subsequent entries in the list.
        """
        return self.final_trace

    def _get_or_create_id(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        """
        Get the ID for a state that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            if self.nodes_equal(self.ids[i], info):
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = info
        return new_id

    def _add_node(self, node: str):
        """
        Add node if it doesn't already exist.
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=self.create_node_label(self.ids[node]))

    @abstractmethod
    def select_node_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        """
        Select the info to use to compare nodes and generate their labels for a specific graph type.
        """
        pass

    @abstractmethod
    def select_edge_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        """
        Select the info to use to generate the label for each edge for a specific graph type.
        """
        pass

    @abstractmethod
    def create_node_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        """
        Create the label for a node given its chosen information.
        """
        pass

    @abstractmethod
    def create_edge_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        """
        Create the label for an edge given its chosen information.
        """
        pass

    @abstractmethod
    def nodes_equal(self, node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        """
        Check whether two nodes are equal given their chosen information.
        """
        pass
