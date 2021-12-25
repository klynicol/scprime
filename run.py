'''
2021-12-21

Script run at startup to manage ScPrime host
'''
import common

import logging
import os
import sys
from time import sleep
import threading

logging.basiccommon.config(filename="run.log", level=logging.INFO)


parm_1 = None

args_len = len(sys.argv)
if(args_len > 1):
    parm_1 = sys.argv[1]

#spd takes this specific enviornment variable to unlock the wallet automatically
os.environ["SCPRIME_WALLET_PASSWORD"] = common.config['host']['seed']

#Log helper function
#level= info | debug | warning | error
def log(level, message):
    print(message)
    logging.__getattribute__(level)(message)

#Check if process is already running
def is_process_running(process_name):
    tmp = os.popen("ps -Af").read()
    return tmp.count(process_name) > 0

#start the spd and set appropriate directories, also redirect output to the spd.log file.
def start_spd():
    os.system(f"nohup {common.DIR_CURRENT}/spd --profile-directory {common.DIR_PROFILES} --scprime-directory {common.DIR_DATA} -M gtcwh > spd.log &")

#Init the spd. This is first first startup.
if(parm_1 == 'init'):
    start_spd()
    log('info', "Initialization parameter detected, starting SPD and exiting python script")
    sys.exit()

def startup():
    if(is_process_running('scprime/current/spd')):
        return
    log('info', "SPD is not running, starting SPD")
    start_spd()

def interval1_function():
    while True:
        startup()
        sleep(300) # 5 minutes

# def interval2_function():
#     while True:
#         check_disks()
#         sleep(86400) # 24 hours

#Interval 1
interval1_thread = threading.Thread(target=interval1_function)
interval1_thread.start()

# interval2_thread = threading.Thread(target=interval2_function)
# interval2_thread.start()

#joins make sure that the thread ends when the script ends.
interval1_thread.join()
# interval2_thread.join()