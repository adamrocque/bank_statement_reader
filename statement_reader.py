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
    os.mkdir('Logging/')
    os.mkdir('Logging/statement_reader/')

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
STATEMENTS_TO_READ_PATH = '{0}\\Statements_ToRead\\'.format(current_dir)
STATEMENTS_DONE_PATH = '{0}\\Statements_Read\\'.format(current_dir)
# TRANS_TYPES_FILE = '{0}\\transaction_types_old.txt'.format(current_dir)
TRANS_TYPES_FILE = '{0}\\bank_statement_reader\\transaction_types_old.txt'.format(current_dir)
TRANS_STORED_FILE = '{0}\\bank_statement_reader\\transaction_stored.txt'.format(current_dir)
CSV_DATA_FILE = '{0}\\all_data.csv'.format(current_dir)


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
    logger.debug("Found month {0} from data {1}".format(month_shortform, mf_transaction_date))
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
    keys_list = ['{0}. {1}'.format(key_index, keys) for key_index, keys in enumerate(keys_list)]
    # A variable to allow changes to the width of the frame (in # of elements)
    keys_breakdown = lambda input_list, frame_width: [input_list[i:i+frame_width] for i in range(0, len(input_list), frame_width)]

    keys_list = keys_breakdown(keys_list, LIST_DISPLAY_WIDTH)  
    keys_df = pd.DataFrame(keys_list).to_string(index = False, header = False)
    
    # logger.debug("The Keys: \n{0}".format(keys_df))
    return keys_df


# def trans_types_builder(trans_types_source):
#     trans_types = {}
#     for key in trans_types_source:


try:
    logger.info("Reading in a types of transactions")
    
    csv_file = open(CSV_DATA_FILE, 'w')
    csv_writer = csv.writer(csv_file)

    with open(TRANS_STORED_FILE) as tsf:
        trans_stored_src = tsf.read()
    
    trans_stored_src = json.loads(trans_stored_src)

    with open(TRANS_TYPES_FILE) as f:
        trans_types_src = f.read()

    trans_types_src = json.loads(trans_types_src)

    # Creating a src var for the trans_types dict
    # This will only be changed to add new listings to each corresponding type, 
    # as we find listings that are not accounted for 
    trans_types = trans_types_src
    trans_list = list(trans_types.keys())

    keys_frame = key_frame_builder(trans_list)

    # Get list of files currently in Statements to Read path, and work through each one
    filenames = next(os.walk(STATEMENTS_TO_READ_PATH), (None, None, []))[2]  # [] if no file

    # for csv in filenames:
    csv = filenames[0]
    df = pd.read_csv(STATEMENTS_TO_READ_PATH + csv, names = ["Date", "TransName", "Debit", "Credit", "CurTot"])
    for index, transaction in enumerate(df['TransName']):
        trans_month = month_finder(df["Date"][index])
        logger.info("\nTransaction: {0}\nDebit: {1}\nCredit: {2}".format(transaction, df["Debit"][index],df["Credit"][index]))
        # Logic if the transaction is known
        if any(transaction in val for val in trans_stored_src.values()):
            found_trans_type = [key for key, value in trans_stored_src.items() if transaction in value][0]
            logger.info("Found transaction {0} as type {1}".format(transaction, found_trans_type))
            if trans_month in trans_types[found_trans_type]:
                trans_types[found_trans_type][trans_month] = trans_types[found_trans_type][trans_month] + float(df["Debit"][index])
            else:
                trans_types[found_trans_type][trans_month] = float(df["Debit"][index])

        else:
            # Logic if the transaction isn't currently known
            trans_type_num = int(input("\n{0}\nEnter Trans Type Number:".format(keys_frame)))
            if trans_type_num <= len(trans_list)-1:
                logger.info("Sounds good, I'll create a new entry for {0} in type {1} for {2}".format(transaction, trans_list[trans_type_num],trans_month))
                trans_stored_src[trans_list[trans_type_num]].append(transaction)
                if trans_month in trans_types[trans_list[trans_type_num]]:
                    trans_types[trans_list[trans_type_num]][trans_month] = trans_types[trans_list[trans_type_num]][trans_month] + float(df["Debit"][index])
                else:
                    trans_types[trans_list[trans_type_num]][trans_month] = float(df["Debit"][index])
            else:
                raise ValueError("The number you entered doesn't correspond to a possible entry. Goodbye ")


    # Old logic TODO to save the transaction within the trans_types dict.
    # TODO: Build logic to save trans name against trans type in file for future ref
    # TODO: Build logic to determine if transaction is in previous file to auto fill transType
    # TODO: Add data to the running list of new payments
    # TODO: Take  new entry and add it to the current transaction types dict
    # TODO: Take  new entry and add it to OG transaction types file
    # TODO: Add data to the running list of new payments

    # TODO Build integration with Google
    # TODO Build Google Sheets populator
except Exception as e:

    logger.exception("Encountered an issue: {0}".format(e))

finally:
    logger.info("Closing the csv file {0}".format(CSV_DATA_FILE))
    csv_file.close()

    logger.info("Writing changes to stored transactions file {0}".format(TRANS_STORED_FILE))
    with open(TRANS_STORED_FILE, 'wt') as tsf_final:
        tsf_final.write(json.dumps(trans_stored_src, indent=4, sort_keys=True))
        # pprint.pprint(trans_stored_src, stream=tsf_final)
    logger.info("Saving any new entries back to the source transactions")
