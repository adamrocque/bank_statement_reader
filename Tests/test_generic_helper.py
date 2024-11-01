import unittest
from unittest.mock import patch, MagicMock
from generic_helper import GenericHelper  # Assuming your file is named generic_helper.py
import pandas as pd

class TestGenericHelper(unittest.TestCase):

    def setUp(self):
        # Mock the config values and logger
        self.config_patch = patch('generic_helper.config')
        self.mock_config = self.config_patch.start()
        self.mock_config["DISPLAY"] = {"keyframe_grid_width": "4"}

        self.logger_patch = patch('generic_helper.logger')
        self.mock_logger = self.logger_patch.start()

        # Initialize the GenericHelper instance for tests
        self.helper = GenericHelper()

    def tearDown(self):
        self.config_patch.stop()
        self.logger_patch.stop()

    def test_month_parser(self):
        """Test that the month_parser function correctly parses the month from a date string."""
        date_input = "2023-07-15"
        expected_output = "Jul"
        result = self.helper.month_parser(date_input)
        self.assertEqual(result, expected_output, f"Expected month '{expected_output}' but got '{result}'.")

        # Check logger calls
        self.mock_logger.debug.assert_called_with("Found month Jul from data 2023-07-15")


if __name__ == '__main__':
    unittest.main()
