'''
2021-12-21

Script run at startup to manage ScPrime host
'''
import logging
import os
import sys
from time import sleep
import subprocess
import pathlib
import configparser
import common

logging.basicConfig(filename="run.log", level=logging.INFO)

parm_1 = None

args_len = len(sys.argv)
if(args_len > 1):
    parm_1 = sys.argv[1]

DIR_BASE = str(pathlib.Path.home()) + "/scprime/"
DIR_CURRENT = DIR_BASE + "current"
DIR_DATA = DIR_BASE + "data"
DIR_PROFILE = DIR_BASE + "pofiles"

#spd takes this specific enviornment variable to unlock the wallet automatically
SEED = "seed" #moving to .ini file
os.environ["SCPRIME_WALLET_PASSWORD"] = SEED

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

#Loop for decting if SPD has crashed for some reason
# while True:
#     sleep(10)
#     startup()

def check_disks():
    print(common.run_process("lsblk -S"))

check_disks()

#check disks for SMART status
#sudo smartctl -H /dev/sda
