import jsonpickle
from robot.api.deco import keyword  # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.visualiser import Visualiser
import os


class ModelGenerator:
    @keyword(name='Generate Trace Information')  # type:ignore
    def generate_trace_information(self) -> TraceInfo:
        return TraceInfo()

    @keyword(name='Current Trace Contains')  # type:ignore
    def current_trace_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str | None = None) -> TraceInfo:
        '''
        State should be of format
        "name: key=value"
        '''

        (scen_info, state_info) = self.__convert_to_state_info(scenario_name, state_str)
        trace_info.update_trace(scen_info, state_info, trace_info.previous_length+1)

        return trace_info

    @keyword(name='All Traces Contains List')  # type:ignore
    def all_traces_contains_list(self, trace_info: TraceInfo) -> TraceInfo:
        trace_info.all_traces.append([])
        return trace_info

    @keyword(name='All Traces Contains')  # type:ignore
    def all_traces_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str) -> TraceInfo:
        '''
        State should be of format
        "state: key=value"
        '''
        scenario = ScenarioInfo(scenario_name)
        s = state_str.split(': ')
        key, item = s[1].split('=')
        state = StateInfo._create_state_with_prop(s[0], [(key, item)])

        trace_info.all_traces[0].append((scenario, state))

        return trace_info

    @keyword(name='Export to JSON')  # type:ignore
    def export_to_json(self, suite: str, trace_info: TraceInfo) -> str:
        return trace_info.export(suite, True)

    @keyword(name='Import JSON File')  # type:ignore
    def import_json_file(self, filepath: str) -> TraceInfo:
        with open(filepath, 'r') as f:
            string = f.read()
            decoded_instance = jsonpickle.decode(string)
        visualiser = Visualiser('state', trace_info=decoded_instance)
        return visualiser.trace_info

    @keyword(name='Check File Exists')  # type:ignore
    def check_file_exists(self, filepath: str) -> str:
        return 'file exists' if os.path.exists(filepath) else 'file does not exist'

    @keyword(name='Compare Trace Info')  # type:ignore
    def compare_trace_info(self, t1: TraceInfo, t2: TraceInfo) -> str:
        succes = 'imported model equals exported model'
        fail = 'imported models differs from exported model'
        return succes if repr(t1) == repr(t2) else fail

    @keyword(name='Delete JSON File')  # type:ignore
    def delete_json_file(self, filepath: str):
        os.remove(filepath)

    @keyword(name='Get Graph')  # type:ignore
    def get_graph(self, trace_info: TraceInfo, graph_type: str) -> AbstractGraph:
        return Visualiser(graph_type=graph_type, trace_info=trace_info)._get_graph()

    @keyword(name='Scenario Graph Contains Vertices')
    def scen_graph_contains_vertices(self, graph: AbstractGraph, vertices_str: str) -> str | None:
        """
        Returns error msg if not satisfied, else None
        """

        vertices = [v.strip() for v in vertices_str.split(",")]

        for vertex_name in vertices:
            if vertex_name not in graph.networkx.nodes:
                return f"Vertex {vertex_name} is not in the graph nodes: {graph.networkx.nodes}"

        return None

    # ============= #
    # == HELPERS == #
    # ============= #

    @staticmethod
    def __convert_to_state_info(scenario_name: str, keyvaluestr: str | None) -> tuple[ScenarioInfo, StateInfo]:
        """
        Format:
        "scenario1: key1=value1 key2=value2"
        """
        scenario_name = scenario_name.strip()
        if keyvaluestr is None:
            return (ScenarioInfo(scenario_name), StateInfo._create_state_with_prop(scenario_name, []))

        keyvaluestr = keyvaluestr.strip()

        # contains ["key1", "value1 key2", "value2"]-like structure
        split_eq: list[str] = keyvaluestr.split("=")
        if len(split_eq) < 2:
            raise ValueError(
                "Please input a valid state information string of format \"scenario1: key1=value1 key2=value2\""
            )

        keyvalues: list[tuple[str, str]] = []

        prev_key = split_eq[0]
        for index in range(1, len(split_eq)):
            splits: list[str] = split_eq[index].split(" ")  # "value1 key2" for ex.
            prev_value: str = " ".join(splits[:-1])
            new_key: str = splits[-1]

            keyvalues.append((prev_key, prev_value))
            prev_key = new_key

        return (ScenarioInfo(scenario_name), StateInfo._create_state_with_prop(scenario_name, keyvalues))
