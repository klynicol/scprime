'''
Run from cron tabs

Run a report and send
Report includes
1. HDD usage stats
2. CPU usage stats
3. Contract status
'''
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import common