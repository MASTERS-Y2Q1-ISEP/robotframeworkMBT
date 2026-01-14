from typing import Any

from robotmbt.visualise.visualiser import Visualiser
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo

GRAPH_TYPE = "scenario-delta-value"


def _update_trace(trace_info: TraceInfo, scenario: str, state: list[tuple[str, Any]], backtracked: bool = False) -> TraceInfo:
    length_of_trace: int = len(trace_info.current_trace) + 1
    if backtracked:
        length_of_trace -= 2  # go one before the current trace

    (scen, stat) = _get_info(scenario=scenario, state=state)
    trace_info.update_trace(scenario=scen, state=stat, length=length_of_trace)

    return trace_info


def _get_info(scenario: str, state: list[tuple[str, Any]]) -> tuple[ScenarioInfo, StateInfo]:
    return (ScenarioInfo(scenario=scenario), StateInfo._create_state_with_prop("props", attrs=state))


def main():
    ts: TraceInfo = TraceInfo()

    ts = _update_trace(ts, "A1", [("states", ["a1"]), ("special", "!")])
    ts = _update_trace(ts, "B2", [("states", ["a1", "b2"]), ("special", "!")])
    ts = _update_trace(ts, "A1", [("states", ["a1"]), ("special", "!")], backtracked=True)
    ts = _update_trace(ts, "B1", [("states", ["a1", "b1"]), ("special", "!")])

    vis = Visualiser(graph_type=GRAPH_TYPE, trace_info=ts)
    # g = vis._get_graph()
    html = vis.generate_visualisation()

    # write html to file:
    with open("./vis.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
