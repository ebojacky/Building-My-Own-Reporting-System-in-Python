import logging
import os.path
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

logger = logging.getLogger(__name__)

Base = declarative_base()


class Count(Base):
    __tablename__ = 'count_results'
    record_id = Column(Integer, primary_key=True)
    time = Column(String)
    filename = Column(String)
    event_label = Column(String)
    results_code = Column(String)
    count = Column(Integer)


def database_updater(database_source, list_of_files, dataframe_results):
    try:
        files_to_do = [file for file in list_of_files if database_source in file]

        list_of_result_data = []

        for file in sorted(files_to_do):
            try:

                date = file.split("/")[-2]

                with open(file, "r") as json_file:
                    for line in json_file:
                        data_dict = eval(line)

                        file_name = data_dict["file"].split("/")[-1]
                        data = data_dict["data"]
                        time = data_dict["time"]

                        result_data = count_results_inserter(file=file_name, data=data, time=time,
                                                             database_source=database_source)
                        list_of_result_data.extend(result_data)

                        dummy_file = f"{config.CDR_DONE_PATH}/{date}/{file_name}"
                        with open(dummy_file, 'w') as creating_new_dummy_file:
                            creating_new_dummy_file.close()

            except Exception as e:
                logging.error(str(e))

        df_results = pd.DataFrame.from_records(list_of_result_data)
        dataframe_results[database_source] = df_results

    except Exception as e:
        logging.critical(str(e))


def database_update_manager():
    logging.info("Starting Database Update")

    dates = [datetime.strftime(datetime.today() - timedelta(days=i), '%Y%m%d') for i in
             range(config.JSON_PERIOD_IN_DAYS)][::-1]

    files_to_do = []

    for date in dates:

        try:
            local_dir_done = f"{config.CDR_DONE_PATH}/{date}"
            local_dir_json = f"{config.CDR_JSON_PATH}/{date}"

            Path(local_dir_done).mkdir(parents=True, exist_ok=True)
            Path(local_dir_json).mkdir(parents=True, exist_ok=True)

            cdr_files_done = os.listdir(local_dir_done)
            cdr_files_json = os.listdir(local_dir_json)

            files_to_do.extend([f"{config.CDR_JSON_PATH}/{date}/{file}" for file in cdr_files_json
                                if file not in cdr_files_done
                                and file[-3:] == ".gz"])
        except Exception as e:
            logging.error(f"Error getting list of files to process: {str(e)}")

    try:
        threads = []
        dataframe_results = {}
        for database_source in config.DATABASE_THREADS:
            db_thr = threading.Thread(name=f'db_update_thread_{database_source}', target=database_updater,
                                      args=(database_source, sorted(files_to_do), dataframe_results))
            threads.append(db_thr)

        for thr in threads:
            thr.start()

        for thr in threads:
            thr.join()

        logging.info("Ending Database Update")

        logging.info("Preparing new dataframe for web")

        new_df = pd.DataFrame()
        for key in dataframe_results.keys():
            new_df = pd.concat([new_df, dataframe_results[key]])

        if len(new_df) > 0:
            new_df.time = pd.to_datetime(new_df.time, format='%Y%m%d%H%M')

        logging.info(f"Finished preparing new dataframe for web : {len(new_df)} new records")
        return new_df

    except Exception as e:
        logging.critical(str(e))


def dataframe_getter(database_source="All", direct_return=True, dataframe_results=None):
    logging.info("Starting Dataframe Getter ")

    df = pd.DataFrame()
    partial_data = False

    try:

        dates = [datetime.strftime(datetime.today() - timedelta(days=i), '%Y%m%d')
                 for i in range(config.DATAFRAME_PERIOD_IN_DAYS)]

        db_files_all = [os.path.join(config.DB_PATH, db)
                        for db in os.listdir(config.DB_PATH) if db[-7:] == ".sqlite"]

        if database_source != "All":
            db_files_all = [file for file in db_files_all if database_source in file or database_source[:-2] in file]
            pass

        db_files = []

        for date in dates:
            db_files.extend([file for file in db_files_all if date in file])

        for db_file in sorted(db_files):
            try:
                with sqlite3.connect(db_file) as con:
                    df_temp = pd.read_sql_query("select * from count_results", con)
                    df = pd.concat([df, df_temp])
                    logging.info(f"Database file read successfully : {db_file}")
            except Exception as e:
                partial_data = True
                logging.info(f"Error accessing db_file : {db_file} : {str(e)}")

        # optimise dataframe

        df.drop(["record_id"], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)
        df.time = pd.to_datetime(df.time, format='%Y%m%d%H%M')

        if partial_data:
            logging.info(f"Successfully retrieved new dataframe for memory partially")
        else:
            logging.info(f"Successfully retrieved new dataframe for memory")

    except Exception as e:
        logging.error(f"Error retrieving new dataframe for memory : {str(e)}")

    logging.info("Ending DataFrame Getter")

    if not direct_return:
        dataframe_results[database_source] = df

    else:
        return df


def dataframe_getter_manager():
    threads = []
    dataframe_results = {}
    for database_source in config.DATABASE_THREADS:
        db_thr = threading.Thread(name=f'df_initial_thread_{database_source}', target=dataframe_getter,
                                  args=(database_source, False, dataframe_results))
        threads.append(db_thr)

    for thr in threads:
        thr.start()

    for thr in threads:
        thr.join()

    final_df = pd.DataFrame()
    for key in dataframe_results.keys():
        final_df = pd.concat([final_df, dataframe_results[key]])

    return final_df


def count_results_inserter(file, data, time, database_source):
    result_data = []
    time_from_epoch = datetime.fromtimestamp(int(time))
    try:
        date_on_db_file = time_from_epoch.strftime('%Y%m%d')
        db_full_path = os.path.join(config.DB_PATH, f"{date_on_db_file}.{database_source}.sqlite")
        engine = create_engine(f"sqlite:///{db_full_path}")

        Base.metadata.create_all(engine)

        session = sessionmaker(bind=engine)
        my_session = session()

        for key, value in data.items():
            new_count = Count(
                time=time_from_epoch.strftime('%Y%m%d%H%M'),
                filename=file,
                event_label=key[0],
                results_code=key[1],
                count=value
            )

            my_session.add(new_count)
            my_session.commit()

            result_data.append(dict(
                time=time_from_epoch.strftime('%Y%m%d%H%M'),
                filename=file,
                event_label=str(key[0]),
                results_code=str(key[1]),
                count=value
                )
            )

        logging.info(f"Successfully updated db with file info: {file}")

    except Exception as e:
        logging.error(f"Error inserting data into db for file: {file} : {str(e)}")

    return result_data

