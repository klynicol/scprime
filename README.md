# Installation (Ubuntu server x64)

### modules
***
- `sudo apt install python`
- `sudo apt install smartmontools`
- `sudo apt install python3-pip`
- `pip install pytz`
- `sudo apt update`

### drive setup
***
- `sudo fdisk -l` view drives and partitions
- `sudo fdisk /dev/sda` then press n to create partition
- `cd /mnt`
- `sudo mkdir sda1` make folders the same names as the partitions
- `sudo mount /dev/sda1 /mnt/sda1` mount the drives
- `cd sda1`
- `sudo mkdir folder1` break into sub folders (large drives), recommended by the docs
- `sudo mkdir folder2` 
- `sudo mkdir folder2` 
- `sudo mkdir folder4` 

### scprime setup
***
- `cd ~`
- `git clone https://github.com/klynicol/scprime.git`
- `cd scprime`
- `python3 install.py 1.6.0`
- `vi .ini` IMPORTANT, change the ports in .ini file before running the spd.
- `cd ..`
- `chmod -R 777 scprime` permissions required for entire folder structure
- `cd scprime`
- `python3 run.py init`
- BLOCKCHAIN NOW SYNCING, check back in a few hours and check consensus with spc. While this is running you can work on port forwarding.
- `~/scprime/current/spc wallet init`
- copy paste seed to .ini file and backup documents
- add folders to all the drives
- `~/scprime/current/spc host folder add /mnt/sda1/folder1 3600GB`
 * disk total space - 50GB / number of folders, 50GB recommended by the docs to prevent corruption
- `sudo systemctl status cron.service` makes sure cron tabs service in enabled
- `crontab -e` add cron services
 * `@reboot python3 ~/scprime/run.py`
 * `0 6 1 * * python3 ~/scprime/cron/balance.py` at 6:00AM on the first of the month
 * `0 * * * * python3 ~/scprime/cron/chkdisk.py` every hour on the hour
 * `0 7 1 * * python3 ~/scprime/cron/report.py` at 7:00AM on the first of the month
- `sudo systemctl reboot`

### Useful linux commands
`lsblk -S` list devices
