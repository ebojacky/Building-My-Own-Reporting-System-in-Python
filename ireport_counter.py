from datetime import datetime, timedelta
from multiprocessing import Pool
from logging.handlers import TimedRotatingFileHandler

import logging
import os.path
import time
import pandas as pd

import config

import directories

directories.create()

# Setting up logging
log_format = config.lf
log_file_name = f'{config.LOG_PATH}/ireport_counter.log'
log_handler = TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=10)
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[log_handler])

logging.info("Starting")


def individual_file_processor(file):
    date = file.split("/")[-2]
    local_dir_json = f"{config.CDR_JSON_PATH}/{date}"

    try:
        # count events and results

        df_cdr = pd.read_csv(file, usecols=["I_GEN_TIME", "I_EVENT_LABEL", "I_RC"])

        middle_time = int(df_cdr["I_GEN_TIME"].median())
        event_and_results_dictionary = df_cdr[["I_EVENT_LABEL", "I_RC"]].value_counts().to_dict()
        logging.info(f"Successfully counted data in file: {file}")

        try:
            file_dict = dict(
                file=file,
                data=event_and_results_dictionary,
                time=middle_time)

            json_file = f'{local_dir_json}/{file.split("/")[-1]}'
            with open(json_file, 'w') as creating_new_csv_file:
                creating_new_csv_file.write(str(file_dict))
                logging.info(f"Successfully created json file: {json_file}")

        except Exception as e:
            logging.error(f"Error writing json data for file: {file} : {str(e)}")

    except Exception as e:
        logging.error(f"Error counting from file: {file} : {str(e)}")


def run_file_data_counter():
    while True:
        logging.info("Starting")

        try:
            dates = [datetime.strftime(datetime.today() - timedelta(days=i), '%Y%m%d') for i in
                     range(config.COUNTER_PERIOD_IN_DAYS)][::-1]

            for date in dates:

                try:

                    local_dir = f"{config.CDR_PATH}/{date}"
                    local_dir_done = f"{config.CDR_DONE_PATH}/{date}"
                    local_dir_json = f"{config.CDR_JSON_PATH}/{date}"

                    directories.create_these([local_dir, local_dir_json, local_dir_done])

                    cdr_files = os.listdir(local_dir)
                    cdr_files_done = os.listdir(local_dir_done)
                    cdr_files_json = os.listdir(local_dir_json)

                    files_to_do = sorted(
                        [f"{config.CDR_PATH}/{date}/{file}" for file in cdr_files
                         if file not in cdr_files_json and file not in cdr_files_done
                         and file[-3:] == ".gz"]
                    )

                    with Pool(config.COUNTER_THREADS_IN_POOL) as p:
                        p.map(individual_file_processor, files_to_do)

                except Exception as e:
                    logging.error(str(e))

        except Exception as e:
            logging.critical(str(e))

        logging.info("Sleeping")

        time.sleep(config.COUNTER_SLEEP_IN_SECONDS)


if __name__ == "__main__":
    run_file_data_counter()
