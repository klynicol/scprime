'''
2021-12-21

Script run at startup to manage ScPrime host
'''
import common

import os
import sys
from time import sleep
import threading


parm_1 = None

args_len = len(sys.argv)
if(args_len > 1):
    parm_1 = sys.argv[1]

#spd takes this specific enviornment variable to unlock the wallet automatically
os.environ["SCPRIME_WALLET_PASSWORD"] = common.config['host']['seed']

#start the spd and set appropriate directories/ports, also redirect output to the spd.log file.
def start_spd(init = False):
    command = (f"{common.DIR_CURRENT}/spd"
    f" --profile-directory {common.DIR_PROFILES}"
    f" --scprime-directory {common.DIR_DATA}"
    f" --host-addr :{common.config['host']['host_port']}"
    f" --siamux-addr :{common.config['host']['siamux_port']}"
    f" --siamux-addr-ws :{common.config['host']['siamux_ws_port']}"
    f" --host-api-addr :{common.config['host']['host_api_port']}"
    " -M gtcwh > spd.log")
    if(init):
        #Allow comand to run in the background
        command += " &"
    os.system(command)

#Init the spd. This is first first startup.
if(parm_1 == 'init'):
    start_spd()
    common.log('info', "Initialization parameter detected, starting SPD and exiting python script")
    sys.exit()

def startup():
    if(common.is_process_running('scprime/current/spd')):
        return
    common.log('info', "SPD is not running, starting SPD")
    start_spd()

def interval1_function():
    while True:
        startup() #Check to make sure were running.
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