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
            """Test a single word longer than the desired length."""
            long_word = "Supercalifragilisticexpialidocious"  # 34 characters
            result = ScenarioInfo._split_name(long_word)
            # Should remain as one line (no spaces to split on)
            self.assertEqual(result, long_word)
        
        def test_split_name_two_words_short(self):
            """Test two short words that fit on one line."""
            result = ScenarioInfo._split_name("Hello World")
            self.assertEqual(result, "Hello World")
        
        def test_split_name_two_words_exceeds_limit(self):
            """Test two words that together exceed 20 characters."""
            result = ScenarioInfo._split_name("HelloSupercalifragilisticexpialidocious")
            # First word sets desired length to 34, second word fits
            self.assertEqual(result, "HelloSupercalifragilisticexpialidocious")
        
        def test_split_name_multiple_words_fit_one_line(self):
            """Test multiple words that fit on one line."""
            result = ScenarioInfo._split_name("This is a short name")
            self.assertEqual(result, "This is a short name")
        
        def test_split_name_multiple_words_need_split(self):
            """Test multiple words that need to be split."""
            name = "This is a very long scenario name that should be split"
            result = ScenarioInfo._split_name(name)
            # Should be split into multiple lines
            self.assertIn("\n", result)
            lines = result.split("\n")
            self.assertGreater(len(lines), 1)
        
        def test_split_name_with_long_word_adjusts_length(self):
            """Test name with extremely long word (45 chars) that exceeds default desired length."""
            name = "NormalWord ExtremelyLongWordThatExceedsTwentyCharacters AnotherWord"
            result = ScenarioInfo._split_name(name)
            self.assertIn("ExtremelyLongWordThatExceedsTwentyCharacters", result)
            result_words = result.replace('\n', ' ').split()
            expected_words = name.split()
            self.assertEqual(result_words, expected_words)
        
        def test_split_name_perfect_split_vs_imperfect(self):
            """Test algorithm prefers split that keeps line length closer to desired length."""
            # This name should split after "scenario" (line length 20) 
            # rather than after "scenario name" (line length 26)
            name = "This is a scenario name test"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, "This is a scenario\nname test")
        
        def test_split_name_exact_desired_length(self):
            """Test two 10-character words where the total length (21) exceeds desired length (20)."""
            name = "0123456789 0123456789"  # Two 10-character words with space
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, "0123456789 0123456789")
        
        def test_split_name_with_trailing_newline_character(self):
            """Test that newline characters in input are handled."""
            name = "First line\nSecond line"
            result = ScenarioInfo._split_name(name)
            # The method splits on spaces, not existing newlines
            # Existing newlines will be treated as part of words
            self.assertIn("\n", result)
        
        def test_split_name_special_characters(self):
            """Test splitting names with special characters."""
            name = "Test with-dash_and_underscore plus@symbol"
            result = ScenarioInfo._split_name(name)
            self.assertIn("with-dash_and_underscore", result)
        
        def test_split_name_multiple_spaces(self):
            """Test that multiple spaces are collapsed to single splits."""
            name = "Test    with    multiple    spaces"
            result = ScenarioInfo._split_name(name)
            # Multiple spaces should be treated as single spaces for splitting
            words = [w for w in result.replace("\n", " ").split(" ") if w]
            self.assertEqual(len(words), 4)
        
        def test_split_name_very_long_sentence(self):
            """Test a long Latin placeholder text sentence gets properly split."""
            name = ("Lorem ipsum dolor sit amet consectetur adipiscing elit sed do "
                    "eiusmod tempor incididunt ut labore et dolore magna aliqua")
            result = ScenarioInfo._split_name(name)
            lines = result.split("\n")
            for line in lines:
                self.assertTrue(len(line) > 0)
            result_words = result.replace('\n', ' ').split()
            expected_words = name.split()
            self.assertEqual(result_words, expected_words)
        
        def test_split_name_edge_case_previous_line_empty(self):
            """Test edge case where previous line becomes empty string."""
            # This tests the condition: if line == '\n'
            name = "A " * 15
            result = ScenarioInfo._split_name(name)
            self.assertIsInstance(result, str)
        
        def test_split_name_unicode_characters(self):
            """Test splitting names with Unicode characters."""
            name = "Café naïve résumé Pokémon"
            result = ScenarioInfo._split_name(name)
            self.assertIn("Pokémon", result)
        
        def test_split_name_leading_trailing_spaces(self):
            """Test name with spaces - algorithm handles word separation."""
            name = "  Leading and trailing spaces  "
            result = ScenarioInfo._split_name(name)
            self.assertIn("Leading", result)
            self.assertIn("trailing", result)
            self.assertIn("spaces", result)
            name = "Leading and trailing spaces"
            result = ScenarioInfo._split_name(name)
            self.assertIn("Leading", result)
        
        def test_split_name_algorithm_correctness(self):
            """Test specific example showing algorithm's splitting behavior."""
            name = "This is a test scenario name example"
            result = ScenarioInfo._split_name(name)
            expected = "This is a test scenario\nname example"
            self.assertEqual(result, expected)
        
        def test_split_name_no_spaces(self):
            """Test a name with no spaces (should not split)."""
            name = "ThisIsAReallyLongNameWithoutAnySpacesAtAll"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, name)
        
        def test_split_name_one_word_per_line(self):
            """Test many single-letter words get grouped into reasonable lines."""
            name = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
            result = ScenarioInfo._split_name(name)
            lines = result.split("\n")
            result_letters = result.replace('\n', ' ').replace(' ', '')
            expected_letters = name.replace(' ', '')
            self.assertEqual(result_letters, expected_letters)
            for line in lines:
                self.assertLessEqual(len(line), 25)

        def test_split_name_returns_string(self):
            """Ensure the method always returns a string."""
            test_cases = [
                "",
                "test",
                "a b c",
                "verylongword" * 5,
                "a" * 100,
            ]
            for name in test_cases:
                with self.subTest(name=name):
                    result = ScenarioInfo._split_name(name)
                    self.assertIsInstance(result, str)

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