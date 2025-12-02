from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
import networkx as nx


class ScenarioGraph(AbstractGraph):
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

    def select_node_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        return pair[0]

    def select_edge_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        return None

    def create_node_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        return info.name

    def create_edge_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        return ''

    def nodes_equal(self, node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        return node1.src_id == node2.src_id
