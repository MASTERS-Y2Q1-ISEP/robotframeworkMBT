import unittest

try:
    import networkx as nx
    from robotmbt.visualise.graphs.stategraph import StateGraph
    from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
    from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False


if VISUALISE:
    class TestVisualiseAbstractGraph(unittest.TestCase):
        """
        Tests for robotmbt/visualise/graphs/abstractgraph.py and its subclasses.
        Includes comprehensive edge case testing for graph construction and _add_edge logic.
        """
        
        def setUp(self):
            """Common setup for tests."""
            self.info = TraceInfo()
            
        def test_abstract_graph_add_edge_labels_for_state_graph_self_loop(self):
            """
            Testing the case where on an edge "scenario2" occurs twice
            Without the "(rep x)" present
            """
            info = TraceInfo()

            scenario1 = ScenarioInfo('scenario1')
            scenario2 = ScenarioInfo('scenario2')
            scenario3 = ScenarioInfo('scenario3')

            space1 = StateInfo._create_state_with_prop(
                "prop", [("value", "some_value")])

            info.update_trace(scenario1, space1, 1)
            info.update_trace(scenario2, space1, 2)
            info.update_trace(scenario3, space1, 3)
            info.update_trace(scenario2, space1, 4)

            sg = StateGraph(info)
            labels = nx.get_edge_attributes(sg.networkx, 'label')
            self.assertEqual(labels[('node0', 'node0')],
                             'scenario2\nscenario3')
            
        def test_add_edge_empty_label_on_existing_edge(self):
            """Test that adding empty label to existing edge returns early."""
            # Create a simple trace
            scenario1 = ScenarioInfo('scenario1')
            scenario2 = ScenarioInfo('scenario2')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            
            self.info.update_trace(scenario1, space, 1)
            self.info.update_trace(scenario2, space, 2)
            
            sg = StateGraph(self.info)
            
            # Get edge from start to node0 (scenario1)
            start_to_node0 = ('start', 'node0')
            
            # Get initial label
            initial_label = sg.networkx.edges[start_to_node0]['label']
            
            # Call _add_edge with empty label (should return early)
            sg._add_edge('start', 'node0', '')
            
            # Label should remain unchanged
            self.assertEqual(sg.networkx.edges[start_to_node0]['label'], initial_label)
            
        def test_add_edge_duplicate_label_prevention(self):
            """Test that duplicate labels are not added to existing edge."""
            # Create a trace with scenario repeated
            scenario = ScenarioInfo('scenario')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            
            # Create self-loop: scenario -> same scenario
            self.info.update_trace(scenario, space, 1)
            self.info.update_trace(scenario, space, 2)  # Same state, creates self-loop
            
            sg = StateGraph(self.info)
            
            # Get the self-loop edge
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1]]
            self.assertGreater(len(self_loop_edges), 0)
            
            self_loop_edge = self_loop_edges[0]
            initial_label = sg.networkx.edges[self_loop_edge]['label']
            
            # Try to add duplicate label (should be prevented)
            sg._add_edge(self_loop_edge[0], self_loop_edge[1], initial_label.split('\n')[0])
            
            # Label should remain the same (not duplicated)
            self.assertEqual(sg.networkx.edges[self_loop_edge]['label'], initial_label)
            
        def test_add_edge_multiple_label_merges(self):
            """Test merging more than 2 labels on the same edge."""
            # Create a complex trace with same scenario repeated multiple times
            scenario = ScenarioInfo('scenario')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            
            # Create multiple self-loops with same scenario
            for i in range(1, 6):  # 5 repetitions
                self.info.update_trace(scenario, space, i)
                
            sg = StateGraph(self.info)
            
            # Find self-loop edge (from node0 to node0)
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1] and e[0] != 'start']
            self.assertGreater(len(self_loop_edges), 0)
            
            self_loop_edge = self_loop_edges[0]
            labels = sg.networkx.edges[self_loop_edge]['label'].split('\n')
            
            # Since duplicates are prevented, we should only have 1 label
            self.assertEqual(len(labels), 1)
            
            # Check the label is the scenario name
            self.assertEqual(labels[0], 'scenario')
                
        def test_add_edge_new_label_appends_correctly(self):
            """Test that new label is appended with newline separator."""
            # Create initial edge with label
            scenario1 = ScenarioInfo('scenario1')
            scenario2 = ScenarioInfo('scenario2')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            
            self.info.update_trace(scenario1, space, 1)
            sg = StateGraph(self.info)
            
            # Manually add a different label to the same edge
            # This simulates what happens when the same transition occurs
            # with a different scenario in backtracking
            sg._add_edge('start', 'node0', 'scenario3')
            
            label = sg.networkx.edges[('start', 'node0')]['label']
            labels = label.split('\n')
            
            # Should contain both labels
            self.assertIn('scenario1', labels)
            self.assertIn('scenario3', labels)
            self.assertEqual(len(labels), 2)
            
        def test_add_edge_with_nonexistent_nodes(self):
            """Test edge creation when nodes don't exist yet."""
            sg = StateGraph(self.info)
            
            # Create node info and store in ids first
            scenario = ScenarioInfo('test')
            node_id1 = sg._get_or_create_id(scenario)
            sg.ids[node_id1] = scenario
            
            # Try to add edge with node that hasn't been added to networkx
            sg._add_edge('start', node_id1, 'test_label')
            
            # Both nodes should now exist in networkx
            self.assertIn('start', sg.networkx.nodes)
            self.assertIn(node_id1, sg.networkx.nodes)
            self.assertIn(('start', node_id1), sg.networkx.edges)
            
        def test_self_loop_with_different_scenarios(self):
            """Test self-loop edge with different scenario labels."""
            scenario1 = ScenarioInfo('scenario1')
            scenario2 = ScenarioInfo('scenario2')
            scenario3 = ScenarioInfo('scenario3')
            space = StateInfo._create_state_with_prop("prop", [("value", "some_value")])
            
            # Create trace: scenario1 -> scenario2 -> scenario3 -> same state
            self.info.update_trace(scenario1, space, 1)
            self.info.update_trace(scenario2, space, 2)
            self.info.update_trace(scenario3, space, 3)
            self.info.update_trace(scenario2, space, 4)  # Back to same state
            
            sg = StateGraph(self.info)
            
            # Find self-loop edges
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1]]
            
            # Should have at least one self-loop
            self.assertGreater(len(self_loop_edges), 0)
            
            # Check label merging for self-loop
            for edge in self_loop_edges:
                labels = sg.networkx.edges[edge]['label'].split('\n')
                # Should contain scenario3 and scenario2 (from the repetition)
                self.assertIn('scenario3', labels)
                self.assertIn('scenario2', labels)
                
        def test_graph_construction_with_empty_trace(self):
            """Test graph creation with empty trace info."""
            sg = StateGraph(self.info)
            
            # Should only have start node
            self.assertEqual(len(sg.networkx.nodes), 1)
            self.assertIn('start', sg.networkx.nodes)
            self.assertEqual(len(sg.networkx.edges), 0)
            self.assertEqual(sg.get_final_trace(), ['start'])
            
        def test_graph_construction_with_single_step(self):
            """Test graph with only one scenario in trace."""
            scenario = ScenarioInfo('single')
            space = StateInfo._create_state_with_prop("prop", [("value", "test")])
            
            self.info.update_trace(scenario, space, 1)
            sg = StateGraph(self.info)
            
            # Should have start and one scenario node
            self.assertEqual(len(sg.networkx.nodes), 2)
            self.assertEqual(len(sg.networkx.edges), 1)
            self.assertIn(('start', 'node0'), sg.networkx.edges)
            
        def test_graph_construction_complex_backtracking(self):
            """Test graph with complex backtracking pattern."""
            scenario1 = ScenarioInfo('A')
            scenario2 = ScenarioInfo('B') 
            scenario3 = ScenarioInfo('C')
            scenario4 = ScenarioInfo('D')
            
            space1 = StateInfo._create_state_with_prop("prop", [("value", "1")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "2")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "3")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "4")])
            
            # Create: A -> B -> C -> backtrack -> B -> D
            self.info.update_trace(scenario1, space1, 1)
            self.info.update_trace(scenario2, space2, 2)
            self.info.update_trace(scenario3, space3, 3)
            self.info.update_trace(scenario2, space2, 2)  # Backtrack
            self.info.update_trace(scenario4, space4, 3)  # New path
            
            sg = StateGraph(self.info)
            
            # Check final trace
            final_trace = sg.get_final_trace()
            self.assertEqual(len(final_trace), 4)  # start + A + B + D
            
            # Check that backtracked path (A->B->C) is in all_traces
            self.assertEqual(len(self.info.all_traces), 1)
            backtracked_trace = self.info.all_traces[0]
            self.assertEqual(len(backtracked_trace), 3)  # A, B, C
            
        def test_edge_label_ordering(self):
            """Test that edge labels maintain chronological order."""
            scenario1 = ScenarioInfo('first')
            scenario2 = ScenarioInfo('second')
            scenario3 = ScenarioInfo('third')
            space = StateInfo._create_state_with_prop("prop", [("value", "same")])
            
            # Create self-loops: first -> second -> third -> same state
            self.info.update_trace(scenario1, space, 1)
            self.info.update_trace(scenario2, space, 2)
            self.info.update_trace(scenario3, space, 3)
            
            sg = StateGraph(self.info)
            
            # Check edge from start to node0
            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], 'first')
            
            # Find self-loop edge (from node0 to node0)
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1] and e[0] != 'start']
            self.assertGreater(len(self_loop_edges), 0)
            
            edge = self_loop_edges[0]
            labels = sg.networkx.edges[edge]['label'].split('\n')
            
            # Labels should be in chronological order: second, third
            self.assertEqual(labels[0], 'second')
            self.assertEqual(labels[1], 'third')
            self.assertEqual(len(labels), 2)
            
        def test_multiple_edges_same_label_different_nodes(self):
            """Test same label on different edges (should not interfere)."""
            scenario1 = ScenarioInfo('same_name')
            scenario2 = ScenarioInfo('same_name')  # Same name, different object
            scenario3 = ScenarioInfo('different')
            
            space1 = StateInfo._create_state_with_prop("prop", [("value", "1")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "2")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "3")])
            
            # Create: A -> B -> C where A and B have same name but different states
            self.info.update_trace(scenario1, space1, 1)
            self.info.update_trace(scenario2, space2, 2)
            self.info.update_trace(scenario3, space3, 3)
            
            sg = StateGraph(self.info)
            
            # Check that edges have correct labels
            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], 'same_name')
            self.assertEqual(sg.networkx.edges[('node0', 'node1')]['label'], 'same_name')
            self.assertEqual(sg.networkx.edges[('node1', 'node2')]['label'], 'different')
            
        def test_edge_addition_with_special_characters_in_label(self):
            """Test edge labels with special characters."""
            # Use special characters that don't include newlines
            # for the scenario names to avoid splitting issues
            scenario1 = ScenarioInfo('scenario:with:colons')
            scenario2 = ScenarioInfo('scenario with spaces')
            scenario3 = ScenarioInfo('scenario\twith\ttabs')
            
            space = StateInfo._create_state_with_prop("prop", [("value", "test")])
            
            # Create trace with special characters
            self.info.update_trace(scenario1, space, 1)
            self.info.update_trace(scenario2, space, 2)
            self.info.update_trace(scenario3, space, 3)
            
            sg = StateGraph(self.info)
            
            # Check edge from start to node0
            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], 'scenario:with:colons')
            
            # Find self-loop edge (from node0 to node0)
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1] and e[0] != 'start']
            self.assertGreater(len(self_loop_edges), 0)
            
            edge = self_loop_edges[0]
            labels = sg.networkx.edges[edge]['label'].split('\n')
            
            # Should contain second and third scenarios (self-loops)
            # Note: scenario2 doesn't have newlines, so it won't be split
            self.assertIn('scenario with spaces', labels)
            self.assertIn('scenario\twith\ttabs', labels)
            self.assertEqual(len(labels), 2)
                
        def test_graph_with_circular_dependency(self):
            """Test graph with circular path (A->B->C->A)."""
            scenario1 = ScenarioInfo('A')
            scenario2 = ScenarioInfo('B')
            scenario3 = ScenarioInfo('C')
            
            space1 = StateInfo._create_state_with_prop("prop", [("value", "1")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "2")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "3")])
            
            # Create circular path
            self.info.update_trace(scenario1, space1, 1)
            self.info.update_trace(scenario2, space2, 2)
            self.info.update_trace(scenario3, space3, 3)
            self.info.update_trace(scenario1, space1, 4)  # Back to A
            
            sg = StateGraph(self.info)
            
            # Check edges exist
            self.assertIn(('start', 'node0'), sg.networkx.edges)
            self.assertIn(('node0', 'node1'), sg.networkx.edges)
            self.assertIn(('node1', 'node2'), sg.networkx.edges)
            self.assertIn(('node2', 'node0'), sg.networkx.edges)  # Circular
            
        def test_final_trace_correctness_after_backtracking(self):
            """Test that final trace is correct after complex backtracking."""
            scenario1 = ScenarioInfo('A')
            scenario2 = ScenarioInfo('B')
            scenario3 = ScenarioInfo('C')
            scenario4 = ScenarioInfo('D')
            
            space1 = StateInfo._create_state_with_prop("prop", [("value", "1")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "2")])
            space3 = StateInfo._create_state_with_prop("prop", [("value", "3")])
            space4 = StateInfo._create_state_with_prop("prop", [("value", "4")])
            
            # Complex backtracking scenario
            self.info.update_trace(scenario1, space1, 1)
            self.info.update_trace(scenario2, space2, 2)
            self.info.update_trace(scenario3, space3, 3)
            self.info.update_trace(scenario2, space2, 2)  # Backtrack
            self.info.update_trace(scenario4, space4, 3)
            self.info.update_trace(scenario3, space3, 4)
            self.info.update_trace(scenario4, space4, 5)
            
            sg = StateGraph(self.info)
            
            # Final trace should be: start -> A -> B -> D -> C -> D
            final_trace = sg.get_final_trace()
            
            # Check it's a valid path in the graph
            for i in range(len(final_trace) - 1):
                self.assertIn((final_trace[i], final_trace[i + 1]), sg.networkx.edges)
                
        def test_different_graph_types_edge_handling(self):
            """Test that different graph types handle edges correctly."""
            scenario = ScenarioInfo('test')
            space = StateInfo._create_state_with_prop("prop", [("value", "test")])
            
            self.info.update_trace(scenario, space, 1)
            
            # Test different graph types
            graph_types = [
                (StateGraph, 'test'),  # StateGraph uses scenario name as edge label
                (ScenarioGraph, ''),    # ScenarioGraph has empty edge labels
                (ScenarioStateGraph, '') # ScenarioStateGraph has empty edge labels
            ]
            
            for graph_class, expected_label in graph_types:
                with self.subTest(graph_class=graph_class.__name__):
                    graph = graph_class(self.info)
                    edges = list(graph.networkx.edges())
                    self.assertGreater(len(edges), 0)
                    
                    for edge in edges:
                        if edge != ('start', 'start'):  # Skip self-loop on start if any
                            self.assertEqual(graph.networkx.edges[edge]['label'], expected_label)
                            
        def test_edge_attributes_preserved(self):
            """Test that edge attributes other than 'label' are not affected."""
            scenario1 = ScenarioInfo('A')
            scenario2 = ScenarioInfo('B')
            
            space1 = StateInfo._create_state_with_prop("prop", [("value", "1")])
            space2 = StateInfo._create_state_with_prop("prop", [("value", "2")])
            
            self.info.update_trace(scenario1, space1, 1)
            self.info.update_trace(scenario2, space2, 2)
            
            sg = StateGraph(self.info)
            
            # Add custom attribute to an edge
            edge = ('start', 'node0')
            sg.networkx.edges[edge]['custom_attr'] = 'test_value'
            
            # Call _add_edge (should preserve custom attribute)
            sg._add_edge('start', 'node0', 'new_label')
            
            # Custom attribute should still exist
            self.assertEqual(sg.networkx.edges[edge].get('custom_attr'), 'test_value')
            # Label should be updated
            self.assertIn('new_label', sg.networkx.edges[edge]['label'])
            
        def test_concurrent_edge_modification_handling(self):
            """Test that edge modification handles concurrent-like scenarios."""
            # This tests the robustness when edges are modified in quick succession
            scenario = ScenarioInfo('scenario')
            space = StateInfo._create_state_with_prop("prop", [("value", "test")])
            
            # Create many repetitions quickly
            for i in range(10):
                self.info.update_trace(scenario, space, i + 1)
                
            sg = StateGraph(self.info)
            
            # Find self-loop edge
            edges = list(sg.networkx.edges())
            self_loop_edges = [e for e in edges if e[0] == e[1]]
            
            if len(self_loop_edges) > 0:
                edge = self_loop_edges[0]
                labels = sg.networkx.edges[edge]['label'].split('\n')
                
                # Should have multiple labels (though may be merged if same scenario)
                # For StateGraph with same scenario, labels will be merged
                self.assertEqual(len(labels), 1)  # All same scenario name
                self.assertEqual(labels[0], 'scenario')
                
        def test_edge_case_empty_scenario_name(self):
            """Test edge with empty scenario name."""
            scenario = ScenarioInfo('')
            space = StateInfo._create_state_with_prop("prop", [("value", "test")])
            
            self.info.update_trace(scenario, space, 1)
            sg = StateGraph(self.info)
            
            # Edge label should be empty string
            self.assertEqual(sg.networkx.edges[('start', 'node0')]['label'], '')

if __name__ == '__main__':
    unittest.main()