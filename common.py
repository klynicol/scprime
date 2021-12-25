'''
Common functions
'''

from subprocess import run
import os
from shutil import rmtree
from shutil import move
import smtplib
from email.message import EmailMessage
import re
import pathlib
import configparser

DIR_BASE = str(pathlib.Path.home()) + "/scprime/"
DIR_ZIP = DIR_BASE + "zip"
DIR_CURRENT = DIR_BASE + "current"
DIR_DATA = DIR_BASE + "data"
DIR_EXTRACT = DIR_BASE + "extract"
DIR_PROFILES = DIR_BASE + "profiles"
DIR_REPORT_DATA = DIR_BASE + "report_data"


HOSTNAME = os.uname()[1]

config = configparser.ConfigParser()
config.read(f"{DIR_BASE}.ini")

#Run a command and rerturn the results as array
def run_process(cmd):
    args = cmd.split()
    result = run(args, capture_output=True, text=True)
    return repr(result.stdout).split("\n")

#Remove contents of a directory
def remove_contents(path):
    for c in os.listdir(path):
        full_path = os.path.join(path, c)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            rmtree(full_path)

#Move the contents of a diretory to another location
def move_contents(src, dst):
    for elem in os.listdir(src):
        move(os.path.join(src, elem), dst=dst)

def send_email(subject, body, to="mwicklinedev@gmail.com"):
    msg = EmailMessage()
    msg['From'] = "noreply@markwickline.com"
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)
    server = smtplib.SMTP_SSL('smtp.dreamhost.com', 465)
    server.ehlo()
    server.login("noreply@markwickline.com", "scprimetothemoon")
    server.send_message(msg)

'''
Takes a strng such as "1.2 KS" OR "49834 H" (as examples) and parses them
to a float value of SCP

H = Hasting 10^-27 SCP
pS (pico,  10^-12 SCP)
nS (nano,  10^-9 SCP)
uS (micro, 10^-6 SCP)
mS (milli, 10^-3 SCP)
SCP
KS (kilo, 10^3 SCP)
MS (mega, 10^6 SCP)
GS (giga, 10^9 SCP)
TS (tera, 10^12 SCP)
'''
units = {
    'h' : {
        'notation': -27
    },
    'ps' : {
        'notation': -12
    },
    'ns' : {
        'notation': -9
    },
    'us' : {
        'notation': -6
    },
    'ms' : {
        'notation': -3
    },
    'scp' : {
        'notation': 0
    },
    'ks' : {
        'notation': 3
    },
    'ms' : {
        'notation': 6
    },
    'gs' : {
        'notation': 9
    },
    'ts' : {
        'notation': 12
    },
}
def parse_scp(raw):
    raw = raw.replace(" ", "")
    decimal = re.findall('\d*\.?\d+', raw)
    if len(decimal) == 0:
        return False
    decimal = decimal[0]
    unit = raw.replace(decimal, "").lower()
    if unit not in units:
        return False
    scp = float(f"{decimal}e{units[unit]['notation']}")
    return scp
