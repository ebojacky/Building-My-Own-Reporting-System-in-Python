# Application Folders
CDR_PATH = "cdrs"
CDR_DONE_PATH = f"{CDR_PATH}/done"
CDR_JSON_PATH = f"{CDR_PATH}/json"
LOG_PATH = "logs"
DB_PATH = "dbs"
TEMP_HTML = "templates/user_temp_html"
# log file formatting
lf = "%(asctime)s|%(process)s|%(processName)s|%(thread)s|%(threadName)s|%(module)s|%(name)s|%(levelname)s|%(message)s"
# Optional SFTP detailed logs
SFTP_LOG_PATH = f"{LOG_PATH}/sftp.paramiko.log"
DETAILED_SFTP_LOGS = False
# Days to Monitor Input Folders
SFTP_PERIOD_IN_DAYS = 3
COUNTER_PERIOD_IN_DAYS = 3
JSON_PERIOD_IN_DAYS = 3
DATAFRAME_PERIOD_IN_DAYS = 30
# Thread Sleeping times
SFTP_SLEEP_IN_SECONDS = 15
COUNTER_SLEEP_IN_SECONDS = 15
DATABASE_SLEEP_IN_SECONDS = 15
# SFTP
MCAS_CDR_PATH = "/bills/cdrs/"
POSSIBLE_FOLDERS = ["FOLDER1", "FOLDER2", "FOLDER3", "FOLDER4"]
MCAS_SFTP_LIST = [
 {"name": "host1", "host": "1.2.3.1", "user": "username", "passwd": "***"},
 {"name": "host2", "host": "1.2.3.2", "user": "username", "passwd": "***g"},
 {"name": "host3", "host": "1.2.3.3", "user": "username", "passwd": "***"},
 {"name": "host4", "host": "1.2.3.4", "user": "username", "passwd": "***"},
]
# File Counter
COUNTER_THREADS_IN_POOL = 32
# Database Update threads
DATABASE_THREADS = [
 "1.gz",
 "2.gz",
 "3.gz",
 "4.gz",
]
# Graphical Interface
DATA_SOURCES_GUI = [
 "All",
 "1.gz",
 "2.gz",
 "3.gz",
 "4.gz",
]
EVENTS_MAP = {
 "1": "1-Originated Call",
 "2": "2-Terminated Call",
 "3": "3-TCP/IP Recharge",
 "4": "4-Manual Recharge",
 "5": "5-Internal Scratch Card Recharge",
 "6": "6-SIM Deletion",
 "7": "7-SIM Frozen",
 "8": "8-SIM Unfrozen",
 "9": "9-Outstanding Charges Cleared",
 "10": "10-Help Desk Call",
 "11": "11-Language Selection",
 "12": "12-Residual Balance",
 "13": "13-Life Cycle Update",
 "14": "14-Activation",
 "15": "15-RCMS Scratch Card Recharge",
 "16": "16-Emergency",
 "17": "17–3rd Party",
 "18": "18-Regular Charge",
 "19": "19-Class Of Service Change",
 "20": "20-Manual Scratch Card Recharge",
 "21": "21-Penalty Charge",
 "22": "22-Installment Holiday",
 "23": "23-Tariff Plan Selection",
 "25": "25-MO SMSC Activity",
 "26": "26-MT SMSC Activity",
 "27": "27-Toggle Twin MSISDN Diversion",
 "29": "29-Modify Friends and Family",
 "30": "30-SIM Unsuspended",
 "31": "31-Abbreviated Dialling",
 "32": "32-Credit Confiscation",
 "34": "34-IVR Purchase Package",
 "35": "35-Purchase Package",
 "36": "36-Credit Card Recharge",
 "37": "37-Partial Activation",
 "38": "38-Full CAMEL 1 Roaming",
 "39": "39-Unmigrated Subscriber Handling",
 "41": "41-First Call Made",
 "42": "42-Lock Subscription",
 "43": "43-non-real time Recharge",
 "44": "44-Promotion Subscription Status Change",
 "45": "45-PIN Change",
 "46": "46-LDAP Call",
 "47": "47-Audit Recharge",
 "57": "57-First Tariff Plan Selection",
 "58": "58-e-Commerce Request Credit - Reverse",
}
RESULTS_MAP = {
 "1": "1-Successful",
 "2": "2-Called Party Busy",
 "3": "3-Called Party No Answer",
 "4": "4-Route Select Failure",
 "5": "5-Calling Party Abandon",
 "6": "6-Call Aborted",
 "7": "7-SIM In Error",
 "8": "8-Barred as SIM Invalid",
 "9": "9-Barred as SIM Expired",
 "10": "10-Barred By O/G Screening",
}
