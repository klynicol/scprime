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
    # f" --siamux-addr-ws :{common.config['host']['siamux_ws_port']}"
    f" --host-api-addr :{common.config['host']['host_api_port']}"
    f" --apipassword {common.config['host']['api_password']}"
    f" -M gtcwh > {common.DIR_BASE}spd.log")
    if(init):
        #Allow comand to run in the background
        command += " &"
    os.system(command)

"""
Option	Description
SPD Options	​
–api-addr=	Spd API address (value of spd –api-addr) (default: localhost:4280)
–api-password=	Spd API password, can (and should) be defined using SCPRIME_API_PASSWORD environment variable. By default will try to read password from ‘apipassword’ file created by spd [$SCPRIME_API_PASSWORD]
Autoannounce Options	​
–no-announce	Disable autoannounce
–host-addr=	Spd daemon host address (value of spd –host-addr) (default: :4282)
–check-ip-interval=	Interval between two IP checks (default: 5m)
–announce-interval=	Minimum interval between two announcements (default: 30m)
–mining-check=	If transaction was not included in the block for that amount of time, host will announce again. Must be >= announce-interval (default: 1h)
Autopricing Options	​
–no-pricing	Disable autopricing
–update-interval=	Update settings interval (default: 1h)
–settings=	Comma-separate list of host settings to update. Available are: maxdownloadbatchsize, maxduration, maxrevisebatchsize, windowsize, collateral, collateralbudget, maxcollateral, minbaserpcprice, mincontractprice, mindownloadbandwidthprice, minsectoraccessprice, minstorageprice, minuploadbandwidthprice, maxephemeralaccountbalance, maxephemeralaccountrisk. Updates all listed settings by default
–target-price-usd=	Target price in USD (default: 4.0)
–max-shift-ratio=	Maximum price shift between two updates. Example: current storage price 100 SCP, target price 102 SCP, max shift is 0.005, new price would be 100.5 SCP (default: 0.005
–force-update-diff=	Update price to target if target differs from current by this ratio (not take into account max-shift-ratio during update). Example: current price is 100 SCP, target is 160 SCP, force update diff is 0.5, new price would be 160 SCP (default: 0.5)
"""
def start_supervisor(init = False):
    command = (f"{common.DIR_CURRENT}/supervisor-lite"
    f" --api-addr=localhost:{common.config['host']['host_api_port']}"
    f" --api-password={common.config['host']['api_password']}"
    f" --host-addr=localhost:{common.config['host']['host_port']}"
    f" --no-announce"
    f" > {common.DIR_BASE}supervisor.log")
    if(init):
        #Allow comand to run in the background
        command += " &"
    os.system(command)


#Init the spd. This is first first startup.
if(parm_1 == 'init'):
    start_spd(True)
    common.log('info', "Initialization parameter detected, starting SPD and exiting python script")
    sys.exit()

def startup_spd():
    if(common.is_process_running('scprime/current/spd')):
        return
    common.log('info', "SPD is not running, starting SPD")
    start_spd()

def startup_supervisor():
    if(common.is_process_running('scprime/current/supervisor-lite')):
        return
    common.log('info', "Supervisor is not running, starting Supervisor")
    start_supervisor()


def interval1_function():
    while True:
        startup_spd() #Check to make sure were running.
        startup_supervisor() #Check to make sure were running.
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