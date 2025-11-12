import random
import string

class ScenarioGenerator:
    @staticmethod
    def generate_random_scenario_name(length :int=10):
        """Generates a random scenario name."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_scenario_names(count :int) -> list[str]:
        """Generates a list of unique random scenarios."""
        scenarios :set[str] = set()
        while len(scenarios) < count:
            scenario = ScenarioGenerator.generate_random_scenario_name()
            scenarios.add(scenario)
        return list(scenarios)
