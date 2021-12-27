'''
Setup folder structure and download cli for ScPrime host

[ ] chmod entire folder structure
'''
import common

import os
import requests
import sys
import zipfile
import shutil
import configparser

if(len(sys.argv) <= 1):
    print("version parameter required")
    sys.exit()

version = sys.argv[1]
version_full = f'ScPrime-v{version}-linux-arm64'
zip_filename = f'{version_full}.zip'
zip_url =  f'https://releases.scpri.me/{version}/{zip_filename}'
zip_file_path = common.DIR_ZIP + "/" + version + ".zip"

#helper function, checking if dir exists first then making that dir
def mkdir(path):
    if(not os.path.isdir(path)):
        os.mkdir(path)

#setup folder structure
mkdir(common.DIR_ZIP)
mkdir(common.DIR_CURRENT)
mkdir(common.DIR_DATA)
mkdir(common.DIR_EXTRACT)
mkdir(common.DIR_PROFILES)
mkdir(common.DIR_REPORT_DATA)

#see if we can pick out the hard drive names on the device
line_count = 0
drives = []
for line in common.run_process("lsblk -S", '\\n'):
    line_count += 1
    if(line_count == 1 or not line):
        continue
    drives.extend(line.split(" ")[0])

#make the .ini
import configparser
ini = configparser.ConfigParser()
ini['host'] = {
    'dir_base' : 
    'seed': '',
    'drives': '|'.join(drives),
    'max_wallet_balance' : 500,
    'to_address' : 'dfaeieiofajfkeakefjdjd',
    'host_port' : 4282,
    'siamux_port': 4283,
    'host_api_port' : 4285
}
with open('.ini', 'w') as configfile:
    ini.write(configfile)

#Download the file into the common.DIR_ZIP folder
def download_cli(url):
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
download_cli(zip_url)

#unzip the file cotents into /current folder
with zipfile.ZipFile(zip_file_path) as myzip:
    myzip.extractall(path=common.DIR_EXTRACT)

'''
Next we have to take the contents of the extracted file and stick them
into common.DIR_CURRENT folder. Scprime team is currently creating a root folder
inside the zip with the same name as the zip. If that changes, change the
`extracted_folder` variable
'''
extracted_folder = common.DIR_EXTRACT + "/" + version_full
#first check if the file were expecting to get is there
if(not os.path.isdir(extracted_folder)):
    print(f"{extracted_folder} doesn't exist, make sure the zip file has the correct contents")
    print("exiting script")
    sys.exit()

#clear the common.DIR_CURRENT foler
common.remove_contents(common.DIR_CURRENT)

#make the transfer from the extacted folder to common.DIR_CURRENT
common.move_contents(extracted_folder, common.DIR_CURRENT)

#clean up the extracted_folder
shutil.rmtree(extracted_folder)
