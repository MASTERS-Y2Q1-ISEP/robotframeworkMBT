from robotmbt.suiteprocessors import SuiteProcessors
from robotmbt.visualisation.models.visualisationinfo import VisualisationInfo

class TracePreparer:
    @staticmethod
    def get_trace_info() -> VisualisationInfo:
        # try to get a Suite Processor instance
        if len(SuiteProcessors.instances) == 0:
            raise RuntimeError("No instances of SuiteProcessor")
        
        # get last one. TODO: see if correct (we have multiple instances sometimes)
        suiteProcessorInstance = SuiteProcessors.instances[-1]

        return VisualisationInfo(trace=suiteProcessorInstance.tracestate, scenarios=suiteProcessorInstance.scenarios)

