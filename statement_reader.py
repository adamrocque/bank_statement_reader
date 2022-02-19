import datetime
import json
import logging
import os
import pandas as pd
import sys

# Check if the logging directory exists, create if not
if not os.path.isdir('Logging/statement_reader/'):
    os.mkdir('Logging/')
    os.mkdir('Logging/statement_reader/')

# Creating the logger
logger = logging.getLogger('[Bank Statement Ready]')
logger.setLevel(logging.DEBUG)
logname = 'Logging/statement_reader/statement_reader_{:%Y-%m-%d-%H}.log'.format(datetime.datetime.now())
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(logname)
stream_handler = logging.StreamHandler(sys.stdout)

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

LIST_DISPLAY_WIDTH = 4
STATEMENTS_TO_READ_PATH = 'E:\\Repos\\Bank_Statement_Reader\\Statements_ToRead\\'
STATEMENTS_DONE_PATH = 'E:\\Repos\\Bank_Statement_Reader\\Statements_Read\\'
TRANS_TYPES_FILE = 'E:\\Repos\\Bank_Statement_Reader\\transaction_types.txt'


def key_frame_builder(builder_trans_types):
    # Take the trans type dictionary, rip the keys out and build a slightly prettier format to view all the keys

    keys_list = list(builder_trans_types.keys())
    # A variable to allow changes to the width of the frame (in # of elements)
    frame_width = LIST_DISPLAY_WIDTH
    keys_breakdown = lambda test_list, frame_width: [keys_list[i:i+frame_width] for i in range(0, len(test_list), frame_width)]

    keys_list = keys_breakdown(keys_list, frame_width)  
    keys_df = pd.DataFrame(keys_list).to_string(index = False, header = False)
    
    # logger.debug("The Keys: \n{0}".format(keys_df))
    return keys_df

logger.info("Reading in a types of transactions")
with open(TRANS_TYPES_FILE) as f:
    trans_types_src = f.read()


try:
    trans_types_src = json.loads(trans_types_src)

    # Creating a src var for the trans_types dict
    # This will only be changed to add new listings to each corresponding type, 
    # as we find listings that are not accounted for 
    trans_types = trans_types_src

    keys_frame = key_frame_builder(trans_types)

    # Pulling list of types to ignore when parsing
    ign_list = trans_types['Ignore']

    # Get list of files currently in Statements to Read path, and work through each one
    filenames = next(os.walk(STATEMENTS_TO_READ_PATH), (None, None, []))[2]  # [] if no file

    # saving_df = pd.DataFrame(columns = ["TransType", "TransName", "Debit", "Credit", "CurTot"])

    # Parse through the list of files we retrieved, and 
    # for csv in filenames:
    csv = filenames[0]
    df = pd.read_csv(STATEMENTS_TO_READ_PATH + csv, names = ["Date", "TransName", "Debit", "Credit", "CurTot"])
    for transaction in df['TransName']:
        if transaction not in ign_list:
            trans_found = False
            for trans_type in trans_types:
                if transaction in trans_types[trans_type]:
                    # print()
                    print(trans_type)
                    trans_found = True 
            if not trans_found:
                logger.info("Could not find a transaction type for {0}, let's create one".format(transaction))
                new_trans_entry = input("Of the following, please type the name of the Transaction Type you would like {0} to be considered as: \n{1}\nEnter Here:".format(transaction, keys_frame))
                if new_trans_entry in trans_types.keys():
                    logger.info("Sounds good, I'll create a new entry for {0} in type {1}".format(transaction, new_trans_entry))
                    # TODO: Take  new entry and add it to the current transaction types dict
                    # TODO: Take  new entry and add it to OG transaction types file
                    # TODO: Add data to the 
                else:
                    logger.info("Please enter one of the possible types: \n{0}\nEnter Here:".format(keys_frame))

    
except Exception as e:
    logger.exception("Encountered an issue: {0}".format(e))