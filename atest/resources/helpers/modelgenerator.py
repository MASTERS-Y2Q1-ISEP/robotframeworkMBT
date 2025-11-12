from robot.api.deco import keyword # type:ignore
from atest.resources.helpers.scenariogenerator import ScenarioGenerator
from robotmbt.visualise.models import TraceInfo, ScenarioInfo

class ModelGenerator:    
    @keyword(name="Generate Trace Information") # type: ignore
    def generate_trace_info(self, scenario_count :int) -> TraceInfo:
        """Generates a list of unique random scenarios."""
        scenario_names :list[str] = ScenarioGenerator.generate_scenario_names(scenario_count)

        scenarios :list[ScenarioInfo]= [ ScenarioInfo(name) for name in scenario_names ]
        return TraceInfo(scenarios, None)
