import configparser
import logging.config
import statement_processor  # Assuming statement_processor.py is in the same directory
import generic_helper  # Assuming statement_processor.py is in the same directory
import math
import os
import pandas as pd

# Load the logging configuration
logging.config.fileConfig('logging.conf')
logger = logging.getLogger("__main__")  # This will use the '__main__' settings in logging.conf

def main():

  processor = statement_processor.StatementProcessor()
  helper = generic_helper.GenericHelper()

  try:
    #  Build the transaction cache
    logger.debug(f"Building caches, default data, and base data")
    categorized_trans_names = processor.transaction_cache
    trans_list = processor.transaction_types_list
    trans_monthly_totals = processor.working_transaction_totals

    keys_frame = helper.transaction_grid_builder(trans_list)

    statements_path = processor.statements_path
    logger.debug(f"Statements path: {statements_path}")

    # Get list of files currently in Statements to Read path, and work through each one
    statements_list = next(os.walk(statements_path), (None, None, []))[2]  # [] if no file
    logger.info(f"Filenames: {statements_list}")

    for statement_file in statements_list:
      
      logger.info(f"Processing: {statement_file}")
      # Add a new column to the dataframe to hold the category of the transaction
      working_statement_df = processor.read_statement_file(statement_file)
      
      # for index, transaction in enumerate(working_statement_df['TransName']):
      for index, transaction in working_statement_df.iterrows():
        trans_name = transaction["TransName"]
        trans_month = helper.month_parser(transaction["Date"])
        debit_value = transaction["Debit"]
        credit_value = transaction["Credit"]
        trans_date = transaction["Date"]

        # Check if the transaction is known
        for category, transactions in categorized_trans_names.items():
          if any(trans_name in item for item in transactions):
            found_trans_type = category
            break
          else:
             found_trans_type = None

        # If transaction is found, update the transaction totals
        if found_trans_type:
          logger.debug(f"Found transaction {trans_name} as type {found_trans_type}")

        # If found_trans_type is None, we need to categorize the transaction
        # Handle Credit Card Transfers as Ignore
        elif "TFR-TO C/C" in trans_name:
          found_trans_type = "Ignore"
          logger.debug(f"Found transaction {trans_name} as type {found_trans_type}, it's a Credit Card Transfer")
          
        # Handle Costco as House
        elif "CIBC MC" in trans_name:
          found_trans_type = "House Purchases"
          logger.debug(f"Found transaction {trans_name} as type {found_trans_type}, it's an Amazon Purchase")
          categorized_trans_names[found_trans_type].append(trans_name)        
          
        # Handle Amazon as House for purchases / returns under $75
        elif "AMZN" in transaction and (debit_value <= 75 or credit_value <= 75):
            found_trans_type = "House Purchases"
            logger.debug(f"Found transaction {trans_name} as type {found_trans_type}, it's an Amazon Purchase")
            categorized_trans_names[found_trans_type].append(trans_name)        

        # Handle EdwardJones Deposits as Raj type transactions
        elif "EDWARD JONES" in trans_name:
          if debit_value == 1750.00:
            found_trans_type = "Raj Joint"
            logger.debug(f"Found transaction {trans_name} as type {found_trans_type}, it's a Edward Jones Deposit")
            categorized_trans_names[found_trans_type].append(trans_name)        
          
          elif debit_value == 1250.00:
            found_trans_type = "Adam RRSP"
            logger.debug(f"Found transaction {trans_name} as type {found_trans_type}, it's a Edward Jones Deposit")
            categorized_trans_names[found_trans_type].append(trans_name)        

        # Handle Groceries as Groceries
        elif any(sub in transaction for sub in ['NATIONS', 'NOFRILLS', 'PACIFIC FRESH FOOD MARKET', 'FORTINOS']):
          logger.debug(f"Found transaction {trans_name} as type House Purchases, it's an Amazon Purchase")
          found_trans_type = "Groceries"  
          categorized_trans_names[found_trans_type].append(trans_name)        

        # Handle Unknown Transactions
        else:
          # Log transaction details
          logger.info(
            f"\nTransaction: {trans_name}\nDebit: {debit_value}\nCredit: {credit_value}\nDate: {trans_date}\nFile: {statement_file}"
          )              
          
          # Ask the user to categorize the transaction
          try:
            trans_type_num = int(input(f"\n{keys_frame}\nEnter Trans Type Number:"))
          
            if trans_type_num < len(trans_list):
              found_trans_type = trans_list[trans_type_num]
              logger.info(f"Creating new entry for {trans_name} in type {found_trans_type} for {trans_month}")
              categorized_trans_names[found_trans_type].append(trans_name)

            else:
              logger.warning("The number you entered doesn't correspond to a possible entry. Skipping")
              found_trans_type = "Unknown"
          
          except ValueError as ve:
              logger.warning("You entered in invalid entry. Skipping")
              found_trans_type = "Unknown"

        # Update the DF with the found transaction type
        working_statement_df.at[index, "TransType"] = found_trans_type
        
        # If the transaction is a return / money entering the account, set the amount to the credit value
        amount = -float(credit_value) if math.isnan(debit_value) else float(debit_value)
        
        # If the transaction is income, set the amount to the credit value as we'll sum the Incomes
        amount = float(credit_value) if found_trans_type == "Income" and math.isnan(debit_value) else amount

        # Update the transaction totals
        trans_monthly_totals[found_trans_type].setdefault(trans_month, 0)
        trans_monthly_totals[found_trans_type][trans_month] += amount

      # Update the categorized transactions Df with the newly processed data at the end of each statement
      processor.update_categorized_transactions_csv(working_statement_df)


  except FileNotFoundError as fnf_error:
      logger.error(f"File not found: {fnf_error}", exc_info=True)

  except ValueError as value_error:
      logger.error(f"Value error: {value_error}", exc_info=True)

  except KeyboardInterrupt as keyboard_interrupt:
      logger.info(f"Saw a keyboard interrupt, exiting")

  except Exception as e:
      logger.error(f"An unexpected error occurred: {e}", exc_info=True)

  finally:
    #  Clean up and write final files
    # Update the transactions cache with the new transactions
    processor.write_transaction_cache()

    # Write the DF into a CSV to be used for future reference
    processor.write_categorized_transactions_csv()

    # Write the categorized transactions as the monthly breakdown for the actual budget
    processor.write_monthly_transactions()
    

if __name__ == "__main__":
    main()