import csv
import datetime
import dateutil.parser as dparser
import json
import logging
import os
import pandas as pd
import pprint
import sys

# Check if the logging directory exists, create if not
if not os.path.isdir('Logging/statement_reader/'):
    try:
        os.mkdir('Logging/')
    except:
        pass
    try:
        os.mkdir('Logging/statement_reader/')
    except:
        pass

# Creating the logger
logger = logging.getLogger('[Bank Statement Ready]')
logger.setLevel(logging.INFO)
logname = 'Logging/statement_reader/statement_reader_{:%Y-%m-%d-%H}.log'.format(datetime.datetime.now())
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(logname)
stream_handler = logging.StreamHandler(sys.stdout)

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

current_dir = os.getcwd()

LIST_DISPLAY_WIDTH = 4
STATEMENTS_TO_READ_PATH = f'{current_dir}\\Statements_ToRead\\'
STATEMENTS_DONE_PATH = f'{current_dir}\\Statements_Read\\'
TRANS_AMOUNTS_TEMPLATE = f'{current_dir}\\transaction_amounts_template.json'
TRANS_TYPES_FILE = f'{current_dir}\\transaction_types.json'
CSV_DATA_FILE = f'{current_dir}\\all_data.csv'
PROCESSED_CCS = f'{current_dir}\\CC_Outputs\\processed_statements.json'


"""
    A function to update the running list of transaction types JSON file with new entries

    Args:
    trans_dict: {string}            Dict of the various transaction types already stored
    list_of_transactions: {list}    List of the various transaction types
    type_num: {int}                 The index of the transaction type that the new entry belongs to
    transaction_name: {string}      The name of the new transaction that needs to be added to the list


    Returns: 
    trans_dict: {string}            Dict of the various transaction types already stored, with the new entry added
"""  
def add_new_trans_type(trans_dict, list_of_transactions, type_num, transaction_name):
    trans_dict[list_of_transactions[type_num]].append(transaction_name)
    return trans_dict


"""
    A function to take in a string with date and return the month represented

    Args:
    mf_transaction: {string}    String of the date that needs parsing 

    Returns: 
    month_shortform {str}       Value for the 3 char shortform of the month. Ex. December is Dec
"""  
def month_finder(mf_transaction_date):
    mf_full_date = dparser.parse(mf_transaction_date)
    month_shortform = datetime.datetime.strftime(mf_full_date, "%b")
    logger.debug(f"Found month {month_shortform} from data {mf_transaction_date}")
    return month_shortform


"""
    A function to build a semi-pretty grid of values, based on the keys of a dictionary

    Args:
    builder_trans_types: {dict}         Dictionary where the keys hold the various transaction types

    Returns: 
    keys_df {dataframe}                 This is a dataframe that holds the values 
                                        of the keys from the input dictionary in a grid format
"""  
def key_frame_builder(keys_list):
    # Take the trans type dictionary, rip the keys out and build a slightly prettier format to view all the keys
    keys_list = [f'{key_index}. {keys}' for key_index, keys in enumerate(keys_list)]
    # A variable to allow changes to the width of the frame (in # of elements)
    keys_breakdown = lambda input_list, frame_width: [input_list[i:i+frame_width] for i in range(0, len(input_list), frame_width)]

    keys_list = keys_breakdown(keys_list, LIST_DISPLAY_WIDTH)  
    keys_df = pd.DataFrame(keys_list).to_string(index = False, header = False)
    
    # logger.debug(f"The Keys: \n{keys_df}")
    return keys_df



try:
    logger.info("Reading in all types of transactions")
    
    # TRANS_TYPES_FILE = transaction_types.json
    with open(TRANS_TYPES_FILE) as types_f: 
        trans_types_src = types_f.read()
    
    trans_types = json.loads(trans_types_src)
    logger.info(f"Types of Transactions: {trans_types}")

    trans_amt_template = dict(trans_types)
    for element in trans_amt_template:
        trans_amt_template[element] = {}

    
    # with open(PROCESSED_CCS) as processed_f: 
    #     month_transaction_amounts_src = processed_f.read()
    
    # month_transaction_amounts = json.loads(month_transaction_amounts_src)
        
    # Creating a src var for the trans_types dict
    # This will only be changed to add new listings to each corresponding type, 
    # as we find listings that are not accounted for 
    trans_list = list(trans_types.keys())

    keys_frame = key_frame_builder(trans_list)

    # Get list of files currently in Statements to Read path, and work through each one
    filenames = next(os.walk(STATEMENTS_TO_READ_PATH), (None, None, []))[2]  # [] if no file

    # for csv in filenames:
    csv = filenames[0]
    logger.info(f"WorkingFile: {csv}")
    statement_df = pd.read_csv(STATEMENTS_TO_READ_PATH + csv, names = ["Date", "TransName", "Debit", "Credit", "CurTot"])
    logger.info(f"Reading in the csv file:\n{statement_df}")

    # Loop through each transaction in the statement
    month_transaction_amounts = trans_amt_template
    for index, transaction in enumerate(statement_df['TransName']):
        trans_month = month_finder(statement_df["Date"][index])
        debit_amt = statement_df["Debit"][index]
        credit_amt = statement_df["Credit"][index]

        # logger.info(f"\nTransaction: {transaction}\nDebit: {debit_amt}\nCredit: {credit_amt}\nMonth:{trans_month}")
        if transaction == "EXPEDIA 72636114008022":
            logger.info(f"\nTransaction: {transaction}\nDebit: {debit_amt}\nCredit: {credit_amt}\nMonth:{trans_month}")
            logger.info(f"Type of Debit Value {type(debit_amt)}")
            logger.info(f"Type of Credit Value {type(credit_amt)}")
            logger.info(f"Is Debit Nan? {pd.isna(debit_amt)}")
            
except Exception as e:

    logger.exception(f"Encountered an issue: {e}")