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
- `sudo gdisk /dev/sda` then press d to delete all partitions and n to create partition, w to write and close
- `sudo mkfs.ext4 /dev/sda` format the drives
- `cd /mnt`
- `sudo mkdir sda1` make folders the same names as the partitions
- `vi /etc/fstab` edit fstab to mount drives on system start
```
UUID=69c3d213-690f-4622-8034-021af6d7a94b /mnt/sdc1 ext4 defaults 0 0   
UUID=a79f2b0d-c777-4a73-b151-76b5f446df80 /mnt/sdb1 ext4 defaults 0 0   
UUID=8e7a969f-e54a-4bc1-a109-c9d0430be417 /mnt/sdd1 ext4 defaults 0 0   
UUID=4c0104f8-140f-47d1-a0b2-683b2753c84d /mnt/sde1 ext4 defaults 0 0   
UUID=69c3d213-690f-4622-8034-021af6d7a94b /mnt/sdc1 ext4 defaults 0 0   
```
    
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
 * `@reboot python3 ~/scprime/run.py` <- allows run of spd on startup
 * `0 6 1 * * python3 ~/scprime/cron/balance.py` at 6:00AM on the first of the month
 * `0 * * * * python3 ~/scprime/cron/chkdisk.py` every hour on the hour
 * `0 7 1 * * python3 ~/scprime/cron/report.py` at 7:00AM on the first of the month
- `sudo systemctl reboot`
- `./spc host announce <ip-address/ddns>:14282` last step, to announce host

### Upgrade SPD
- Run install.py with version parameter `python3 install.py 1.7.0`
- Reboot server `sudo systemctl reboot`

### Useful linux commands
`lsblk -S` list devices
