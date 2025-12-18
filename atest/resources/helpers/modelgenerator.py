import jsonpickle
from robot.api.deco import keyword  # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.visualiser import Visualiser


class ModelGenerator:
    @keyword(name="Test Suite From JSON")  # type:ignore
    def test_suite_from_json(self, filename: str) -> TraceInfo:
        with open(f'json/{filename}.json', 'r') as f:
            string = f.read()
            decoded_instance = jsonpickle.decode(string)
        visualiser = Visualiser(
            'state', trace_info=decoded_instance)
        return visualiser.trace_info

    @keyword(name="Get Current Trace From TraceInfo")  # type:ignore
    def get_current_trace_from_traceinfo(self, traceInfo: TraceInfo) -> list[tuple[ScenarioInfo, StateInfo]]:
        return traceInfo.current_trace
