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
            """Test splitting an empty string."""
            result = ScenarioInfo._split_name("")
            self.assertEqual(result, "")
        
        def test_split_name_single_short_word(self):
            """Test a single word shorter than the desired length."""
            result = ScenarioInfo._split_name("Hello")
            self.assertEqual(result, "Hello")
        
        def test_split_name_single_exact_length_word(self):
            """Test a single word exactly at the desired length (20 characters)."""
            exact_20 = "abcdefghijklmnopqrst"  # 20 characters
            result = ScenarioInfo._split_name(exact_20)
            self.assertEqual(result, exact_20)
        
        def test_split_name_single_long_word(self):
            """Test single long word without spaces."""
            name = "ThisIsAReallyLongNameWithoutAnySpacesAtAll"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, name)

        def test_split_name_two_words_short(self):
            """Test two short words that fit on one line."""
            result = ScenarioInfo._split_name("Hello World")
            self.assertEqual(result, "Hello World")

        def test_split_name_two_words_exceeds_limit(self):
            """Test two words that together exceed 20 characters."""
            name = "Supercalifragilistic Hello"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, "Supercalifragilistic\nHello")

        def test_split_name_multiple_words_need_split(self):
            """Test multiple words that need to be split."""
            name = "This is a very long scenario name that should be split"
            result = ScenarioInfo._split_name(name)
            # Should be split into multiple lines
            self.assertIn("\n", result)
            lines = result.split("\n")
            self.assertGreater(len(lines), 1)

        def test_split_name_with_very_long_word(self):
            """Test that a very long word is handled correctly in multi-word input."""
            name = "NormalWord ExtremelyLongWordThatExceedsTwentyCharacters AnotherWord"
            result = ScenarioInfo._split_name(name)
            # Check all characters are preserved (no characters lost)
            result_chars = result.replace('\n', '').replace(' ', '')
            expected_chars = name.replace(' ', '')
            self.assertEqual(result_chars, expected_chars)
            # Check that splitting occurred (the long word should cause splitting)
            self.assertIn('\n', result)

        def test_split_name_perfect_split_vs_imperfect(self):
            """Test algorithm chooses split closest to desired length."""
            name = "This is a scenario name test"
            result = ScenarioInfo._split_name(name)
            # Should split after "scenario" (18 chars) vs "scenario name" (23 chars)
            self.assertEqual(result, "This is a scenario\nname test")
        
        def test_split_name_exact_desired_length(self):
            """Test two 10-character words where the total length (21) exceeds desired length (20)."""
            name = "0123456789 0123456789"
            result = ScenarioInfo._split_name(name)
            # Algorithm keeps them together because 21 is closer to 20 than 10 is
            self.assertEqual(result, "0123456789 0123456789")

        def test_split_name_special_characters(self):
            """Test splitting names with special characters and emojis."""
            name = "Test with-dash_and_underscore plus@symbol Café naïve résumé Pokémon 🚀 🎉"
            result = ScenarioInfo._split_name(name)
            # Check if all content is present
            self.assertIn("with-dash_and_underscore", result)
            self.assertIn("plus@symbol", result)
            self.assertIn("Pokémon", result)
            self.assertIn("🚀", result)
            self.assertIn("🎉", result)

        def test_split_name_very_long_sentence(self):
            """Test long sentence gets reasonably split."""
            name = ("Lorem ipsum dolor sit amet consectetur adipiscing elit sed do "
                    "eiusmod tempor incididunt ut labore et dolore magna aliqua")
            result = ScenarioInfo._split_name(name)   
            # Should be split (it's a long sentence)
            self.assertIn("\n", result)
            # Lines shouldn't be empty
            lines = result.split('\n')
            for line in lines:
                self.assertTrue(len(line) > 0)

        """
        Class: StateInfo
        """

        def test_stateInfo_empty(self):
            s = StateInfo(ModelSpace())
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_empty(self):
            space = ModelSpace()
            space.props['prop1'] = ModelSpace()
            s = StateInfo(space)
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_val(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            space.props['prop1'] = prop1
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))

        def test_stateInfo_prop_val_empty(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            prop2 = ModelSpace()
            space.props['prop1'] = prop1
            space.props['prop2'] = prop2
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))
            self.assertFalse('prop2:' in str(s))

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