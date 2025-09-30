from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState

class VisualisationInfo:
    def __init__(self, *, scenarios :dict[str, Scenario], trace :TraceState):
        self.scenarios :dict[str, Scenario] = scenarios
        self.trace : TraceState = trace
        # possibly other stuff.
    
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"VisInfo(scenarios='{self.scenarios}', tracestate='{self.trace}')"