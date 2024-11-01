import csv
import datetime
import dateutil.parser as dparser
import json
import logging
import math
import os
import pandas as pd
import pathlib
import pprint
import re
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

logger.info(f"Working Dir: {current_dir}")

LIST_DISPLAY_WIDTH = 4
STATEMENTS_TO_READ_PATH = '{0}\\Statements_ToRead\\'.format(current_dir)
TRANS_STORED_FILE = '{0}\\transaction_stored.txt'.format(current_dir)
CSV_DATA_FILE = '{0}\\all_data.csv'.format(current_dir)


"""
    A function to pull the transaction metadata that's been stored

    Returns:
    trans_stored_cache {dict}       Key:Value sets for each TransactionType:[All Transaction names that have previously been categorized into this TransType ]
"""
def build_transaction_cache():

    with open(TRANS_STORED_FILE) as tsf:
        trans_stored_cache = tsf.read()

    trans_stored_cache = json.loads(trans_stored_cache)

    return trans_stored_cache


"""
    A function to write all the newly categorized transactions to the local cache

    Args:
    transaction_updates_dict {dict}       Key:Value sets for each TransactionType:[All Transaction names that have previously been categorized into this TransType]
"""
def update_local_transaction_file(transaction_updates_dict):
    with open(TRANS_STORED_FILE, 'wt') as tsf_final:
        tsf_final.write(json.dumps(transaction_updates_dict, indent=4, sort_keys=True))


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
    A function to take in a string of the Sheet name and return the Year found in it

    Args:
    spreadsheet_name: {string}    String of the spreadsheet name

    Returns:
    month_shortform {string}       Value for the 4 digit year
"""
def year_finder(spreadsheet_name):
    year = re.search("\d{3}", spreadsheet_name)
    if year == "":
        return None

    return year


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


def main():

    try:

        # Pulling in all previously categorized transaction names, for future cross-referencing
        categorized_trans_names = build_transaction_cache()

        # Creating a src var for the trans_types dict
        # This will only be changed to add new listings to each corresponding type,
        # as we find listings that are not accounted for

        with open(TRANS_STORED_FILE) as tsm:
            trans_monthly_cache = tsm.read()

        trans_monthly_cache = json.loads(trans_monthly_cache)
        trans_monthly_totals = {key: {} for key in trans_monthly_cache.keys()}



        # with open(TRANS_STORED_FILE) as tsm_template:
        #     template_transations = tsm_template.read()

        # template_transations = json.load(template_transations)
        # trans_monthly_totals = {key: {} for key in template_transations.keys()}

        # trans_monthly_totals = json.loads(trans_monthly_totals)

        trans_list = list(categorized_trans_names.keys())

        # Building out the nicely framed transaction types
        keys_frame = key_frame_builder(trans_list)

        # Get list of files currently in Statements to Read path, and work through each one
        filenames = next(os.walk(STATEMENTS_TO_READ_PATH), (None, None, []))[2]  # [] if no file
        logger.info(f"Filenames: {filenames}")

        for csv_file in filenames:
            logger.info(f"The current file: {csv_file}")
            df = pd.read_csv(STATEMENTS_TO_READ_PATH + csv_file, names = ["Date", "TransName", "Debit", "Credit", "CurTot"])
            for index, transaction in enumerate(df['TransName']):
                trans_month = month_finder(df["Date"][index])
                logger.info("\nTransaction: {0}\nDebit: {1}\nCredit: {2}\nDate: {3}\nFile: {4}".format(transaction, df["Debit"][index],df["Credit"][index],df["Date"][index], csv_file))

                # Logic if the transaction is known
                if any(transaction in val for val in categorized_trans_names.values()):
                    found_trans_type = [key for key, value in categorized_trans_names.items() if transaction in value][0]
                    logger.info("Found transaction {0} as type {1}".format(transaction, found_trans_type))

                    # Check if Debit is NaN
                    debit_value = df["Debit"][index]
                    credit_value = df["Credit"][index]

                    if math.isnan(debit_value):  # If Debit is NaN
                        if found_trans_type == "Income":
                            amount = float(credit_value)  # Add for Income
                        else:
                            amount = -float(credit_value)  # Subtract for other types
                    else:
                        amount = float(debit_value)  # Use the Debit value if it's not NaN

                    # Update the transaction totals
                    if trans_month in trans_monthly_totals[found_trans_type]:
                        trans_monthly_totals[found_trans_type][trans_month] += amount
                    else:
                        trans_monthly_totals[found_trans_type][trans_month] = amount



                # if any(transaction in val for val in categorized_trans_names.values()):
                #     found_trans_type = [key for key, value in categorized_trans_names.items() if transaction in value][0]
                #     logger.info("Found transaction {0} as type {1}".format(transaction, found_trans_type))
                #     if trans_month in trans_monthly_totals[found_trans_type]:
                #         trans_monthly_totals[found_trans_type][trans_month] = trans_monthly_totals[found_trans_type][trans_month] + float(df["Debit"][index])
                #     else:
                #         trans_monthly_totals[found_trans_type][trans_month] = float(df["Debit"][index])

                # Adding clause to handle Credit Card
                elif "TFR-TO C/C" in transaction:
                    found_trans_type = "Ignore"
                    reason = "Credit Card Transfer"
                    logger.info("Found transaction {0} as type {1}, it's a {2}".format(transaction, found_trans_type, reason))
                    if trans_month in trans_monthly_totals[found_trans_type]:
                        trans_monthly_totals[found_trans_type][trans_month] = trans_monthly_totals[found_trans_type][trans_month] + float(df["Debit"][index])
                    else:
                        trans_monthly_totals[found_trans_type][trans_month] = float(df["Debit"][index])


                else:
                    # Logic if the transaction isn't currently known
                    trans_type_num = int(input("\n{0}\nEnter Trans Type Number:".format(keys_frame)))

                    if trans_type_num <= len(trans_list)-1:
                        logger.info("Sounds good, I'll create a new entry for {0} in type {1} for {2}".format(transaction, trans_list[trans_type_num],trans_month))
                        categorized_trans_names[trans_list[trans_type_num]].append(transaction)
                        # update_local_transaction_file(categorized_trans_names)
                        # categorized_trans_names = build_transaction_cache()

                        if trans_month in trans_monthly_totals[trans_list[trans_type_num]]:
                            trans_monthly_totals[trans_list[trans_type_num]][trans_month] = trans_monthly_totals[trans_list[trans_type_num]][trans_month] + float(df["Debit"][index])
                        else:
                            trans_monthly_totals[trans_list[trans_type_num]][trans_month] = float(df["Debit"][index])
                    else:
                        raise ValueError("The number you entered doesn't correspond to a possible entry. Goodbye ")


            # Old logic TODO to save the transaction within the trans_types dict.
            # TODO: Build logic to save trans name against running trans type in file for future ref
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
        logger.info(f"The calculated budget{(json.dumps(trans_monthly_totals, indent=4))}")

        # Specify the output file name
        # # Writing JSON dictionary to JSON
        with open('calculated_budget.json', 'wt') as output_file:
            output_file.write(json.dumps(trans_monthly_totals, indent=4, sort_keys=True))

        # logger.info("Closing the csv_file file {0}".format(CSV_DATA_FILE))

        # Define the months in the required order
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Create a list of headers: categories + months
        headers = ["Category"] + months

        # Create the csv_file file
        with open('calculated_budget.csv', mode='w', newline='') as file:
            writer = csv.writer(file)  # Write to the open file object

            # Write the header row
            writer.writerow(headers)

            # Write the data
            for category, expenses in trans_monthly_totals.items():
                # Create a row with the category name followed by the amount spent per month
                row = [category] + [expenses.get(month, None) for month in months]
                writer.writerow(row)

        print("CSV file has been created successfully.")

        logger.info("Writing changes to stored transactions file {0}".format(TRANS_STORED_FILE))
        with open(TRANS_STORED_FILE, 'wt') as tsf_final:
            tsf_final.write(json.dumps(categorized_trans_names, indent=4, sort_keys=True))

        logger.info(f"The processed Transactions Monthly Totals: \n{trans_monthly_totals}")
        logger.info("Saving any new entries back to the source transactions")

if __name__ == "__main__":
    main()