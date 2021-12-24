'''
Setup folder structure and download cli for ScPrime host

[ ] chmod entire folder structure
'''

import os
import requests
import sys
import zipfile
import shutil
import configparser

DIR_BASE = ""
DIR_ZIP = DIR_BASE + "zip"
DIR_CURRENT = DIR_BASE + "current"
DIR_DATA = DIR_BASE + "data"
DIR_EXTRACT = DIR_BASE + "extract"
DIR_PROFILES = DIR_BASE + "profiles"

if(len(sys.argv) <= 1):
    print("ersion parameter required")
    sys.exit()

version = sys.argv[1]
version_full = f'ScPrime-v{version}-linux-arm64'
zip_filename = f'{version_full}.zip'
zip_url =  f'https://releases.scpri.me/{version}/{zip_filename}'
zip_file_path = DIR_ZIP + "/" + version + ".zip"

#helper function, checking if dir exists first then making that dir
def mkdir(path):
    if(not os.path.isdir(path)):
        os.mkdir(path)

#setup folder structure
mkdir(DIR_ZIP)
mkdir(DIR_CURRENT)
mkdir(DIR_DATA)
mkdir(DIR_EXTRACT)
mkdir(DIR_PROFILES)

#make the .ini
import configparser
ini = configparser.ConfigParser()

#see if we can pick out the drives on the device


ini['DEFAULT'] = {
    'SEED': '',
    'DRIVES': '',
    'CompressionLevel': '9'
}
with open('.ini', 'w') as configfile:
    ini.write(configfile)

#Download the file into the DIR_ZIP folder
def download(url):
    if(os.path.isfile(zip_file_path)):
        print("zip file already exists in the zip folder")
        return
    get_response = requests.get(url,stream=True)
    if(get_response.status_code != 200):
        print(f"returned status code {get_response.status_code} on {zip_url}")
        print("exiting script")
        sys.exit()
    with open(zip_file_path, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
download(zip_url)

#unzip the file cotents into /current folder
with zipfile.ZipFile(zip_file_path) as myzip:
    myzip.extractall(path=DIR_EXTRACT)

'''
Next we have to take the contents of the extracted file and stick them
into DIR_CURRENT folder. Scprime team is currently creating a root folder
inside the zip with the same name as the zip. If that changes, change the
`extracted_folder` variable
'''
extracted_folder = DIR_EXTRACT + "/" + version_full
#first check if the file were expecting to get is there
if(not os.path.isdir(extracted_folder)):
    print(f"{extracted_folder} doesn't exist, make sure the zip file has the correct contents")
    print("exiting script")
    sys.exit()

#clear the DIR_CURRENT foler
def remove_contents(path):
    for c in os.listdir(path):
        full_path = os.path.join(path, c)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            shutil.rmtree(full_path)
remove_contents(DIR_CURRENT)

#make the transfer
def move_contents(src, dst):
    for elem in os.listdir(src):
        shutil.move(os.path.join(src, elem), dst=dst)
move_contents(extracted_folder, DIR_CURRENT)

#clean up the extracted_folder
shutil.rmtree(extracted_folder)
