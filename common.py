'''
Common functions
'''

from subprocess import run
import os
from shutil import rmtree
from shutil import move
import smtplib
from email.message import EmailMessage

#Run a command and rerturn the results as array
def run_process(cmd):
    args = cmd.split()
    result = run(args, capture_output=True, text=True)
    return repr(result.stdout).split("\n")

def remove_contents(path):
    for c in os.listdir(path):
        full_path = os.path.join(path, c)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            rmtree(full_path)

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