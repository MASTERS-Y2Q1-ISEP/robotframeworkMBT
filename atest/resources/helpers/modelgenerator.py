import jsonpickle
from robot.api.deco import keyword  # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.visualiser import Visualiser


class ModelGenerator:
    @keyword(name='Generate Trace Information') # type:ignore
    def generate_trace_information(self) -> TraceInfo:
        return TraceInfo()

    @keyword(name='Current Trace Contains') # type:ignore
    def current_trace_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str) -> TraceInfo:
        '''
        State should be of format
        "name: key=value"
        '''
        scenario = ScenarioInfo(scenario_name)
        s = state_str.split(': ')
        key, item = s[1].split('=')
        state = StateInfo._create_state_with_prop(s[0], [(key, item)])
        trace_info.update_trace(scenario, state, trace_info.previous_length+1)

        return trace_info
    
    @keyword(name='All Traces Contains List') # type:ignore
    def all_traces_contains_list(self, trace_info: TraceInfo) -> TraceInfo:
        trace_info.all_traces.append([[]])
        return trace_info
    
    @keyword(name='All Traces Contains') # type:ignore
    def all_traces_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str) -> TraceInfo:
        '''
        State should be of format
        "name: key=value"
        '''
        scenario = ScenarioInfo(scenario_name)
        s = state_str.split(': ')
        key, item = s[1].split('=')
        state = StateInfo._create_state_with_prop(s[0], [(key, item)])
        
        trace_info.all_traces[0].append((scenario, state))

        return trace_info

    @keyword(name="Test Suite From JSON")  # type:ignore
    def test_suite_from_json(self, filename: str) -> TraceInfo:
        with open(f'json/{filename}.json', 'r') as f:
            string = f.read()
            decoded_instance = jsonpickle.decode(string)
        visualiser = Visualiser(
            'state', trace_info=decoded_instance)
        return visualiser.trace_info
