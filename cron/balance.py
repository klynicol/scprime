'''
Run from cron tabs

Check balance of scprime wallet
if the balance is over the max_wallet_balance parameter
send funds to the to_address
'''
import sys
sys.path.append("../scprime")
import common

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
            # if(balance > common.config['host']['max_wallet_balance']):