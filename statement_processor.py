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

