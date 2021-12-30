'''
Run from cron tabs

Check balance of scprime wallet
if the balance is over the max_wallet_balance parameter
send funds to the to_address
'''
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common

common.log("info", "Starting balance.py cron task")

'''
Wallet status:
Encrypted, Unlocked
Height:              165855
Confirmed Balance:   0 H
Unconfirmed Delta:   +0 H
Exact:               0 H
Scprimefunds:        0 SPF
Scprimefund Claims:  0 H

Estimated Fee:       30 uS / KB
'''
def check_balance():
    last_line = ""
    line_count = 0
    for line in common.run_process(f"{common.DIR_CURRENT}/spc wallet balance"):
        line_count += 1
        last_line = line
        if(last_line == 'Wallet status:' and 'Locked' in line):
            #wallet is locked, alert with email
            body = f"{common.HOSTNAME} has a locked wallet!"
            common.send_email("Scprime Host Wallet Locked", body)
        if('Exact:' in line):
            balance = common.parse_scp(line.replace('Exact:', ''))
            if(balance == False):
                common.log("error", "Cannot parse exact SCP amount")
                continue
            max = common.config['host']['max_wallet_balance']
            if(balance > max):
                send_ammount = balance - max
                #remove scientific notation
                send_ammount = common.scp_string(send_ammount)
                to_address = common.config['host']['to_address']
                common.log("info", f"Sending {send_ammount}SCP to {to_address}")
                response = common.run_process(f"{common.DIR_CURRENT}/spc wallet send scprimecoins {send_ammount}SCP {to_address}")
                common.log("info", response.join("\n"))

check_balance()

common.log("info", "Ending balance.py cron task")