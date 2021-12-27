'''
Gather stats from the machine and plop them into /report_data folder.
'''
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common

#memory
for line in common.run_process("free -m"):
    