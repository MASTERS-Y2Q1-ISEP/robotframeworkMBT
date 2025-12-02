from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import StateInfo, ScenarioInfo


class StateGraph(AbstractGraph):
    """
    The state graph is a more advanced representation of trace exploration, allowing you to see the internal state.
    It represents states as nodes, and scenarios as edges.
    """

    def select_node_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        return pair[1]

    def select_edge_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        return pair[0]

    def create_edge_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        return info.name

    def create_node_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        return str(info)

    def nodes_equal(self, node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        return node1 == node2
