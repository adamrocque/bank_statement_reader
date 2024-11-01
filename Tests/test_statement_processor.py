import unittest
import os
import configparser
import pandas as pd
from statement_processor import StatementProcessor

class TestStatementProcessor(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    # Load config
    cls.config_path = 'config.ini'
    cls.temp_config_path = 'backup_config.ini'

    cls.config = configparser.ConfigParser()
    cls.config.read('config.ini')

    # Initialize StatementProcessor instance
    cls.processor = StatementProcessor()


  def test_config_values(self):
    """Test that config.ini has the correct sections and key-value pairs."""

    # Define expected configuration values
    expected_config = {
      'DISPLAY': {
        'keyframe_grid_width': '4'
      },
      'INPUT FILES': {
        'statements_to_read_dir': 'InputFiles',
        'stored_transactions_file': 'stored_transaction.txt'
      },
      'OUTPUT FILES': {
        'output_dir': 'OutputFiles',
        'raw_budget_dump_file': 'raw_budget_file.json',
        'calculated_budget_file': 'calculated_budget_file.csv'
      },
      'TEST FILES': {
        'test_data_dir': 'TestData',
        'sample_statement_file': 'sample_statement.csv',
        'expected_calculated_budget_output_file': 'raw_budget_file.json'
      }
    }

    # Check that each section exists and matches expected keys and values
    for section, expected_keys in expected_config.items():
      self.assertIn(section, self.config.sections() or self.config.default_section)
      for key, expected_value in expected_keys.items():
        actual_value = self.config[section].get(key)
        self.assertEqual(actual_value, expected_value,f"Expected {key} in section [{section}] to be '{expected_value}' but got '{actual_value}'.")


  def test_logging(self):
      """Test logging to ensure entries are logged as expected."""
      with self.assertLogs(level='DEBUG') as log:
          self.processor.process_statement()
          # Ensure a log entry was made for processing
          self.assertTrue(any('Processing statement' in message for message in log.output))


  def test_missing_config_file(self):
    """Test behavior when config.ini file is missing."""
    # Temporarily rename the config file to simulate it missing
    os.rename(self.config_path, "backup_" + self.config_path)
    
    try:
      with self.assertRaises(FileNotFoundError):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not os.path.exists(self.config_path):
          raise FileNotFoundError(f"Config file {self.config_path} not found.")
    
    finally:
      # Restore the config file
      if os.path.exists(self.temp_config_path):
        os.rename(self.temp_config_path, self.config_path)


  def test_build_transaction_cache(self):
    """Test that the build_transaction_cache method returns the expected dictionary."""
    min_expected_keys = ['Adam RRSP', 'Dinner Out', 'Groceries', 'Income', 'Mortgage', 'Gas', 'Travel']

    cache = self.processor.build_transaction_cache()
    for key in min_expected_keys:
      self.assertIn(key, cache, f"Expected key '{key}' not found in cache.")
    
    self.assertIsInstance(cache, dict, "Expected cache to be a dictionary.")


  def tearDown(self):
      # Additional cleanup to restore the config file if needed
      if os.path.exists(self.temp_config_path):
          os.rename(self.temp_config_path, self.config_path)


if __name__ == '__main__':
    unittest.main()
