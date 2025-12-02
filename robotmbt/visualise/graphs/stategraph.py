from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import StateInfo, ScenarioInfo


class StateGraph(AbstractGraph):
    """
    The state graph is a more advanced representation of trace exploration, allowing you to see the internal state.
    It represents states as nodes, and scenarios as edges.
    """

    @staticmethod
    def select_node_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        return pair[1]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        return pair[0]

    @staticmethod
    def create_edge_label(info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        return info.name

    @staticmethod
    def create_node_label(info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        return str(info)

    @staticmethod
    def nodes_equal(node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        return node1 == node2
