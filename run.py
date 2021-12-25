'''
2021-12-21

Script run at startup to manage ScPrime host
'''
import common

import logging
import os
import sys
from time import sleep
import subprocess
import pathlib
import configparser
import threading

logging.basicConfig(filename="run.log", level=logging.INFO)
config = configparser.ConfigParser()
config.read(".ini")

parm_1 = None

args_len = len(sys.argv)
if(args_len > 1):
    parm_1 = sys.argv[1]

DIR_BASE = str(pathlib.Path.home()) + "/scprime/"
DIR_CURRENT = DIR_BASE + "current"
DIR_DATA = DIR_BASE + "data"
DIR_PROFILE = DIR_BASE + "pofiles"

#spd takes this specific enviornment variable to unlock the wallet automatically
os.environ["SCPRIME_WALLET_PASSWORD"] = config['host']['seed']

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
    os.system(f"nohup {DIR_CURRENT}/spd --profile-directory {DIR_PROFILE} --scprime-directory {DIR_DATA} -M gtcwh > spd.log &")

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

    #Failed code for unlocking the wallet. Environment variable used instead.
    # sleep(10) #wait 10 seconds for SPD to startup
    #Unlock the wallet
    # log('info', "Unlocking wallet")
    # command = [f"{DIR_CURRENT}/spc", "wallet", "unlock"]
    # p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # output = p.communicate(input=SEED)[0]
    # log('info', output)

def check_disks():
    for disk_name in config['host']['drives'].split("|"):
        line_count = 0
        for line in common.run_process(f"smartctl -H /dev/{disk_name}"):
            line_count += 1
            if(line_count == 1):
                continue
            if "SMART overall-health self-assessment test result:" in line:
                if "FAILED" in line:
                    # DISK FAILED, SEND MESSAGE
                    body = f"Disk /dev/{disk_name} failed on scprime host {os.uname()[1]}"
                    common.send_email("Scprime Host Disk Failure!", body)
    print(common.run_process("lsblk -S"))

check_disks()

#check disks for SMART status
#sudo smartctl -H /dev/sda

def interval1_function():
    while True:
        startup()
        sleep(300) # 5 minutes

def interval2_function():
    while True:
        check_disks()
        sleep(86400) # 24 hours

#Interval 1
interval1_thread = threading.Thread(target=interval1_function)
interval1_thread.start()

interval2_thread = threading.Thread(target=interval2_function)
interval2_thread.start()

#joins make sure that the thread ends when the script ends.
interval1_thread.join()
interval2_thread.join()