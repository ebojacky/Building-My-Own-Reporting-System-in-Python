import logging
import os
import os.path
import threading
from datetime import datetime, timedelta
import time
from logging.handlers import TimedRotatingFileHandler

import paramiko

import config

import directories

directories.create()

# Setting up logging
log_format = config.lf
log_file_name = f'{config.LOG_PATH}/ireport_sftp.log'
log_handler = TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=10)
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[log_handler])

if config.DETAILED_SFTP_LOGS:
    paramiko.util.log_to_file(config.SFTP_LOG_PATH)

logging.info("Starting")


def run_sft_file_downloader(mcas):
    while True:
        try:
            logging.info("Starting")

            dates = [datetime.strftime(datetime.today() - timedelta(days=i), '%Y%m%d') for i in
                     range(config.SFTP_PERIOD_IN_DAYS)][::-1]

            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(mcas["host"], username=mcas["user"], password=mcas["passwd"])

                with ssh.open_sftp() as sftp:

                    folders = [f for f in sftp.listdir(config.MCAS_CDR_PATH) if f in config.POSSIBLE_FOLDERS]

                    for folder in folders:

                        for date in dates:

                            local_dir = f"{config.CDR_PATH}/{date}"
                            local_dir_done = f"{config.CDR_DONE_PATH}/{date}"
                            local_dir_json = f"{config.CDR_JSON_PATH}/{date}"
                            remote_dir = f"{config.MCAS_CDR_PATH}/{folder}/{date}"

                            directories.create_these([local_dir, local_dir_done, local_dir_json])

                            local_files = sorted([f for f in os.listdir(local_dir) if f[-3:] == ".gz"])
                            done_files = sorted([f for f in os.listdir(local_dir_done) if f[-3:] == ".gz"])
                            json_files = sorted([f for f in os.listdir(local_dir_json) if f[-3:] == ".gz"])
                            remote_files = sorted([f for f in sftp.listdir(remote_dir) if f[-3:] == ".gz"])

                            for file in remote_files:

                                try:

                                    if file not in done_files and file not in local_files and file not in json_files:
                                        remote_path = f"{remote_dir}/{file}"
                                        local_path = f"{local_dir}/{file}"
                                        local_path_temp = f"{local_dir}/{file}.temp"
                                        sftp.get(remote_path, local_path_temp)

                                        try:
                                            os.rename(local_path_temp, local_path)
                                        except WindowsError:
                                            os.remove(local_path)
                                            os.rename(local_path_temp, local_path)

                                        logging.info(f"Successfully downloaded file: {local_path}")

                                except Exception as e:
                                    logging.error(f"Error downloading file: {file} : {str(e)}")

            logging.info("Sleeping")

        except Exception as e:
            logging.critical(str(e))

        time.sleep(config.SFTP_SLEEP_IN_SECONDS)


if __name__ == "__main__":
    # Background Processes
    logging.info("Starting Background Tasks for SFTP")
    for mcas in config.MCAS_SFTP_LIST:
        sftp_thr = threading.Thread(name=f'sftp_thread_{mcas["name"]}', target=run_sft_file_downloader,
                                    args=(mcas,))
        sftp_thr.start()
        time.sleep(5)
