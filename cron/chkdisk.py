'''
Run from cron tab

Check the general health of the disks
'''
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common

''' Uses smartctl to make a broad assessment about disk health
(pass or fail). Sends email if FAILED is found.'''
def smartctl():
    for disk_name in common.config['host']['drives'].split("|"):
        line_count = 0
        for line in common.run_process(f"smartctl -H /dev/{disk_name}", '\\n'):
            line_count += 1
            if(line_count == 1):
                continue
            if "SMART overall-health self-assessment test result:" in line:
                if "FAILED" in line:
                    # DISK FAILED, SEND MESSAGE
                    common.log("error", f"Disk /dev/{disk_name} failed")
                    body = f"Disk /dev/{disk_name} failed on scprime host {common.HOSTNAME}"
                    common.send_email("Scprime Host Disk Failure!", body)

smartctl()