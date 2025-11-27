import unittest
from typing import Any

import networkx as nx

try:
    from robotmbt.visualise.graphs.stategraph import StateGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseStateGraph(unittest.TestCase):
        def test_state_graph_init(self):
            sg = StateGraph()
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')

        def test_state_graph_ids_empty(self):
            sg = StateGraph()
            si = StateInfo(ModelSpace())
            node_id = sg._get_or_create_id(si)
            self.assertEqual(node_id, 'node0')

        def test_state_graph_ids_duplicate_scenario(self):
            sg = StateGraph()
            si = StateInfo(ModelSpace())
            id0 = sg._get_or_create_id(si)
            id1 = sg._get_or_create_id(si)
            self.assertEqual(id0, id1)

        def test_state_graph_ids_different_scenarios(self):
            sg = StateGraph()

            s00 = StateInfo(create_space_with_prop("prop", [("value", "some_value")]))
            s01 = StateInfo(create_space_with_prop("prop", [("value", "some_value")]))
            s10 = StateInfo(create_space_with_prop("prop", [("value", "another_value")]))
            s11 = StateInfo(create_space_with_prop("prop", [("value", "another_value")]))
            id00 = sg._get_or_create_id(s00)
            id01 = sg._get_or_create_id(s01)
            id10 = sg._get_or_create_id(s10)
            id11 = sg._get_or_create_id(s11)
            self.assertEqual(id00, 'node0')
            self.assertEqual(id01, 'node0')
            self.assertEqual(id00, id01)
            self.assertEqual(id10, 'node1')
            self.assertEqual(id11, 'node1')
            self.assertEqual(id10, id11)
            self.assertNotEqual(id00, id10)
            self.assertNotEqual(id00, id11)
            self.assertNotEqual(id01, id10)
            self.assertNotEqual(id01, id11)

        def test_state_graph_add_new_node(self):
            sg = StateGraph()

            sg.ids['test'] = StateInfo(create_space_with_prop("prop", [("value", "some_value")]))
            sg._add_node('test')

            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertIn('test', sg.networkx.nodes)
            self.assertEqual(sg.networkx.nodes['test']['label'],
                             str(StateInfo(create_space_with_prop("prop", [("value", "some_value")]))))

        def test_state_graph_add_existing_node(self):
            sg = StateGraph()

            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(len(sg.networkx.nodes), 1)

            sg._add_node('start')

            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(len(sg.networkx.nodes), 1)

        def test_state_graph_update_single(self):
            sg = StateGraph()

            scenario = ScenarioInfo('1')
            space = create_space_with_prop("prop", [("value", "some_value")])
            ti = TraceInfo([scenario], space)
            sg.update_visualisation(ti)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['node0']['label'], str(StateInfo(space)))

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', 'node0')], '1')

        def test_state_graph_update_multi(self):
            sg = StateGraph()

            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')
            scenario3 = ScenarioInfo('3')

            space1 = create_space_with_prop("prop", [("value", "some_value")])
            space2 = create_space_with_prop("prop", [("value", "other_value")])
            space3 = create_space_with_prop("prop", [("value", "another_value")])

            ti1 = TraceInfo([scenario1], space1)
            ti2 = TraceInfo([scenario1, scenario2], space2)
            ti3 = TraceInfo([scenario1, scenario2, scenario3], space3)

            sg.update_visualisation(ti1)
            sg.update_visualisation(ti2)
            sg.update_visualisation(ti3)

            self.assertEqual(len(sg.networkx.nodes), 4)
            self.assertEqual(len(sg.networkx.edges), 3)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['node0']['label'], str(StateInfo(space1)))
            self.assertEqual(sg.networkx.nodes['node1']['label'], str(StateInfo(space2)))
            self.assertEqual(sg.networkx.nodes['node2']['label'], str(StateInfo(space3)))

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)

            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', 'node0')], '1')
            self.assertEqual(edge_labels[('node0', 'node1')], '2')
            self.assertEqual(edge_labels[('node1', 'node2')], '3')

        def test_state_graph_update_multi_loop(self):
            sg = StateGraph()

            scenario1 = ScenarioInfo('1')
            scenario2 = ScenarioInfo('2')
            scenario3 = ScenarioInfo('3')

            space1 = create_space_with_prop("prop", [("value", "some_value")])
            space2 = create_space_with_prop("prop", [("value", "other_value")])
            space3 = create_space_with_prop("prop", [("value", "some_value")])

            ti1 = TraceInfo([scenario1], space1)
            ti2 = TraceInfo([scenario1, scenario2], space2)
            ti3 = TraceInfo([scenario1, scenario2, scenario3], space3)

            sg.update_visualisation(ti1)
            sg.update_visualisation(ti2)
            sg.update_visualisation(ti3)

            self.assertEqual(len(sg.networkx.nodes), 3)
            self.assertEqual(len(sg.networkx.edges), 3)

            self.assertEqual(sg.networkx.nodes['start']['label'], 'start')
            self.assertEqual(sg.networkx.nodes['node0']['label'], str(StateInfo(space1)))
            self.assertEqual(sg.networkx.nodes['node0']['label'], str(StateInfo(space3)))
            self.assertEqual(sg.networkx.nodes['node1']['label'], str(StateInfo(space2)))

            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node0'), sg.networkx.edges)

            edge_labels = nx.get_edge_attributes(sg.networkx, "label")
            self.assertEqual(edge_labels[('start', 'node0')], '1')
            self.assertEqual(edge_labels[('node0', 'node1')], '2')
            self.assertEqual(edge_labels[('node1', 'node0')], '3')


    def create_space_with_prop(name: str, attrs: list[tuple[str, Any]]) -> ModelSpace:
        space = ModelSpace()
        prop = ModelSpace()
        for (key, val) in attrs:
            prop.__setattr__(key, val)
        space.props[name] = prop
        return space

if __name__ == '__main__':
    unittest.main()
