'''
Gather stats from the machine and plop them into /report_data folder.
'''
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common

avail_memory = 0
total_memory = 0

#memory
line_count = 0
for line in common.run_process("free -m", "\\n"):
    line_count += 1
    if(line_count == 1):
        continue
    line_parts = line.split(" ")
    total_memory = line_parts[1].strip()
    avail_memory = line_parts[6].strip()
    break

#