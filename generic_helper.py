import configparser
import datetime
import json
import logging
import os
import pandas as pd
import re

from dateutil import parser

# Initialize the configparser
config = configparser.ConfigParser()

# Load the configuration file
config.read('config.ini')

# Initialize the logger
logger = logging.getLogger(__name__)  # This will use the 'genericHelperLogger' settings in logging.conf


class GenericHelper:
  def __init__(self):
    logger.debug("Initializing GenericHelper")
    self.transaction_grid_width = config["DISPLAY"]["keyframe_grid_width"]


  def month_parser(self, mp_transaction_date):
    """
        A function to take in a string with date and return the month represented

        Args:
        mf_transaction: {string}    String of the date that needs parsing

        Returns:
        month_shortform {str}       Value for the 3 char shortform of the month. Ex. December is Dec
    """      
    parsed_date = parser.parse(mp_transaction_date)
    month_shortform = datetime.datetime.strftime(parsed_date, "%b")
    logger.debug("Found month {0} from data {1}".format(month_shortform, mp_transaction_date))
    
    return month_shortform


  def transaction_grid_builder(self, keys_list):
    """
      A function to build a semi-pretty grid of values, based on the keys of a dictionary

      Args:
      builder_trans_types: {dict}         Dictionary where the keys hold the various transaction types

      Returns:
      keys_df {dataframe}                 This is a dataframe that holds the values
                                          of the keys from the input dictionary in a grid format
    """

    # Take the trans type dictionary, rip the keys out and build a slightly prettier format to view all the keys
    keys_list = ['{0}. {1}'.format(key_index, keys) for key_index, keys in enumerate(keys_list)]
    # A variable to allow changes to the width of the frame (in # of elements)
    keys_breakdown = lambda input_list, frame_width: [input_list[i:i+frame_width] for i in range(0, len(input_list), frame_width)]

    keys_list = keys_breakdown(keys_list, int(self.transaction_grid_width))
    keys_df = pd.DataFrame(keys_list).to_string(index = False, header = False)

    # logger.debug("The Keys: \n{0}".format(keys_df))
    return keys_df