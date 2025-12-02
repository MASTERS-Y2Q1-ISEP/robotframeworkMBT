import networkx as nx
from robot.api import logger

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo


class ScenarioStateGraph(AbstractGraph):
    """
    The scenario-State graph keeps track of both the scenarios and states encountered.
    Its nodes are scenarios together with the state after the scenario has run.
    Its edges represent steps in the trace.
    """

    def select_node_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo]:
        return pair

    def select_edge_info(self, pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo | StateInfo | tuple[
        ScenarioInfo, StateInfo] | None:
        return None

    def create_node_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> str:
        return f"{info[0].name}\n\n{str(info[1])}"

    def create_edge_label(self, info: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo] | None) -> str:
        return ''

    def nodes_equal(self, node1: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo],
                    node2: ScenarioInfo | StateInfo | tuple[ScenarioInfo, StateInfo]) -> bool:
        return node1[0].src_id == node2[0].src_id and node1[1] == node2[1]
