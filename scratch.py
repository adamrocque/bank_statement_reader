import os

cur_dir = os.getcwd()
TRANS_TYPES_FILE = '{0}\\bank_statement_reader\\transaction_types.txt'.format(cur_dir)


print("Reading in a types of transactions")
with open(TRANS_TYPES_FILE) as f:
    trans_types_src = f.read()