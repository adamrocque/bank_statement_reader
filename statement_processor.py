import configparser
import csv
import datetime
import json
import logging
import math
import os
import pandas as pd



# Initialize the configparser
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize the logger
logger = logging.getLogger(__name__)  # This will use the 'statementProcessorLogger' settings in logging.conf


class StatementProcessor:
  def __init__(self):
    logger.debug("Initializing StatementProcessor")

    self.start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    # INPUTS
    # statements_path - the path to the directory containing the statements to read
    # categorized_transaction_cache_file - the path to the file containing the historic stored transactions types
    self.current_dir = os.getcwd()
    self.statements_path = os.path.join(self.current_dir, config["INPUT FILES"]["statements_to_read_dir"])
    self.categorized_transaction_cache_file = os.path.join(self.current_dir, config["INPUT FILES"]["stored_transactions_file"])
    
    # WORKING VARIABLES
    self.transaction_cache, self.transaction_types_list, self.working_transaction_totals = self.build_transaction_cache()

    # OUTPUTS
    # output_dir - the path to the directory to output the categorized transactions
    # historic_transactions_db_csv - the path to the file to output all historic categorized transactions as csv, to be used for future database
    # calculated_budget_file - the path to the file to output the calculated monthly budget
    self.output_dir = os.path.join(self.current_dir, config["OUTPUT FILES"]["output_dir"])
    self.historic_transactions_db_csv = os.path.join(self.output_dir, config["OUTPUT FILES"]["historic_transactions_db_csv"])
    self.calculated_budget_file = os.path.join(self.output_dir, config["OUTPUT FILES"]["calculated_budget_file"])
    
    self.categorized_transactions_df = pd.DataFrame(columns=['Date', 'TransName', 'Debit', 'Credit', 'CurTot', 'TransType'])

    logger.debug(f"Current directory: {self.current_dir}")
    logger.debug(f"Statements path: {self.statements_path}")
    logger.debug(f"Stored transactions file: {self.categorized_transaction_cache_file}")


  def build_transaction_cache(self):
    """
        A function to pull the transaction metadata that's been stored

        Returns:
        trans_stored_cache {dict}       Key:Value sets for each TransactionType:[All Transaction names that have previously been categorized into this TransType ]
    """      
    with open(self.categorized_transaction_cache_file, 'r') as tsf:
      trans_stored_cache = json.load(tsf)  # Directly loads JSON data

    trans_list = list(trans_stored_cache.keys())
    trans_monthly_totals = {key: {} for key in trans_stored_cache.keys()}    

    return trans_stored_cache, trans_list, trans_monthly_totals


  def write_transaction_cache(self):
    """
        A function to write all the newly categorized transactions to the local cache

        Args:
        transaction_updates_dict {dict}       Key:Value sets for each TransactionType:[All Transaction names that have previously been categorized into this TransType]
    """    
    with open(self.categorized_transaction_cache_file, 'wt') as tsf_final:
        tsf_final.write(json.dumps(self.transaction_cache, indent=4, sort_keys=True))


  # def process_statement(self):
  #   """
  #       A function to process statements

  #   """    
  #   logger.debug("Processing statement")

  # def update_historic_transactions(self, trans_type, trans_name):
  #   """
  #       A function to update the historic transactions with the new data

  #   """    
  #   logger.debug("Updating historic transactions")
  #   self.transaction_cache[trans_type].append(trans_name)
    
  def update_categorized_transactions_csv(self, categorized_statement_df):
    """
        A function to update the existing categorized transactions with the ones just processed

        Args:
        categorized_statement_df: {pd.DataFrame}    The categorized transactions dataframe

    """    
    logger.debug("Updating categorized transactions")
    self.categorized_transactions_df = pd.concat([self.categorized_transactions_df, categorized_statement_df], ignore_index=True)
    logger.debug(f"Updated categorized transactions: \n{self.categorized_transactions_df}")

  def write_categorized_transactions_csv(self):
    """
        A function to output the categorized transactions to a file

    """    
    logger.debug("Outputting categorized transactions")
    categorized_transactions_file = self.historic_transactions_db_csv.split(".")[0] + "_" + self.start_time + ".csv"
    self.categorized_transactions_df.to_csv(categorized_transactions_file, index=False)
    

  def read_statement_file(self, statement_file_name):
    """
        A function to read the statement file

    """    
    logger.debug(f"Reading statement file: {statement_file_name}")
    statement_df = pd.read_csv(os.path.join(self.statements_path, statement_file_name), names = ["Date", "TransName", "Debit", "Credit", "CurTot"])
    logger.debug(f"Dataframe: \n{statement_df}")

    # Add a new column to the dataframe to hold the category of the transaction
    categorized_statement_df = statement_df.copy()
    categorized_statement_df["TransType"] = None

    return categorized_statement_df
  
  def write_monthly_transactions(self):
    """
        A function to write the monthly transactions

        Args:
        monthly_trans_df: {dict}    Key:Value sets for each TransactionType:[{month_name: sum_of_transactions}]

    """    
    logger.debug("Writing monthly transactions")
    
    # Define the months in the required order
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Create a list of headers: categories + months
    headers = ["Category"] + months

    monthly_transaction_filename = self.calculated_budget_file.split(".")[0] + "_" + self.start_time + ".csv"

    # Create the csv_file file
    with open(monthly_transaction_filename, mode='w', newline='') as file:
      writer = csv.writer(file)  # Write to the open file object

      # Write the header row
      writer.writerow(headers)

      # Write the data
      for category, expenses in self.working_transaction_totals.items():
        # Create a row with the category name followed by the amount spent per month
        row = [category] + [expenses.get(month, None) for month in months]
        writer.writerow(row)
   