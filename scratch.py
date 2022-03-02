import datetime
import dateutil.parser as dparser
import os
import pandas as pd

cur_dir = os.getcwd()
TRANS_TYPES_FILE = '{0}\\bank_statement_reader\\transaction_types.txt'.format(cur_dir)
STATEMENTS_TO_READ_PATH = '{0}\\Statements_ToRead\\'.format(cur_dir)


# print("Reading in a types of transactions")
# with open(TRANS_TYPES_FILE) as f:
#     trans_types_src = f.read()

def month_finder(mf_transaction):
    # By passing in the date ortion of a transaction, we need to return the month that transaction took place in.
    mf_full_date = dparser.parse(mf_transaction)
    month_shortform = datetime.datetime.strftime(mf_full_date, "%b")
    return month_shortform


filenames = next(os.walk(STATEMENTS_TO_READ_PATH), (None, None, []))[2]  # [] if no file

# saving_df = pd.DataFrame(columns = ["TransType", "TransName", "Debit", "Credit", "CurTot"])

# Parse through the list of files we retrieved, and 
# for csv in filenames:
csv = filenames[0]
df = pd.read_csv(STATEMENTS_TO_READ_PATH + csv, names = ["Date", "TransName", "Debit", "Credit", "CurTot"])


# for transaction in trans_types_src
for index, transaction in enumerate(df['TransName']):
    month_finder(df["Date"][index])
