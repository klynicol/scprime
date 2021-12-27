'''
If and when we need to kill scripts so other actions can be performed
'''

import sys
sys.path.append("../scprime")

import common

for line in common.run_process("ps -Af"):
    if("scprime/current/spd" in line):
        print(line.split(" "))