from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo


class ScenarioGraph(AbstractGraph):
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

    @staticmethod
    def select_node_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        return pair[0]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        return None

    @staticmethod
    def create_node_label(info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        return info.name

    @staticmethod
    def create_edge_label(info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        return ''

    @staticmethod
    def nodes_equal(node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        return node1.src_id == node2.src_id
