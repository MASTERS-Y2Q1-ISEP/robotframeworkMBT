from robotmbt.visualisation.tracepreparer import TracePreparer

class Visualiser:
    @staticmethod
    def visualise() -> object:
        trace_info = TracePreparer.get_trace_info()

        return trace_info