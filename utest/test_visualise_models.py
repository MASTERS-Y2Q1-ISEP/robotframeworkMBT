import unittest

try:
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseModels(unittest.TestCase):
        """
        Contains tests for robotmbt/visualise/models.py
        """

        """
        Class: ScenarioInfo
        """

        def test_scenarioInfo_str(self):
            si = ScenarioInfo('test')
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 'test')

        def test_scenarioInfo_Scenario(self):
            s = Scenario('test')
            s.src_id = 0
            si = ScenarioInfo(s)
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 0)

        # ==============================================
        # Tests for _split_name() method
        # ==============================================
        
        def test_split_name_empty_string(self):
            result = ScenarioInfo._split_name("")
            self.assertEqual(result, "")
            self.assertNotIn('\n', result)

        def test_split_name_single_short_word(self):
            result = ScenarioInfo._split_name("Hello")
            self.assertEqual(result, "Hello")
            self.assertNotIn('\n', result)

        def test_split_name_single_exact_length_word(self):
            exact_20 = "abcdefghijklmnopqrst"
            result = ScenarioInfo._split_name(exact_20)
            self.assertEqual(result, exact_20)
            self.assertNotIn('\n', result)

        def test_split_name_single_long_word(self):
            name = "ThisIsAReallyLongNameWithoutAnySpacesAtAll"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, name)
            self.assertNotIn('\n', result)

        def test_split_name_two_words_short(self):
            result = ScenarioInfo._split_name("Hello World")
            self.assertEqual(result, "Hello World")
            self.assertNotIn('\n', result)

        def test_split_name_two_words_exceeds_limit(self):
            name = "Supercalifragilistic Hello"
            result = ScenarioInfo._split_name(name)

            self.assertEqual(result.replace('\n', ' '), name)
            self.assertIn('\n', result)

        def test_split_name_multiple_words_need_split(self):
            name = "This is a very long scenario name that should be split"
            result = ScenarioInfo._split_name(name)

            self.assertEqual(result.replace('\n', ' '), name)
            self.assertIn('\n', result)

        """
        Class: TraceInfo
        """

        def test_trace_info_update_normal(self):
            info = TraceInfo()

            self.assertEqual(len(info.current_trace), 0)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 3)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 0)

        def test_trace_info_update_backtrack(self):
            info = TraceInfo()

            self.assertEqual(len(info.current_trace), 0)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 3)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 4)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 5)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 6)]), 4)

            self.assertEqual(len(info.current_trace), 4)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

if __name__ == '__main__':
    unittest.main()