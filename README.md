# Installation
> ### drive setup
> `sudo fdisk -l` view drives and partitions
> `sudo fdisk /dev/sda` then press n to create partition
> `cd /mnt`
`sudo mkdir sda1` make folders the same names as the partitions
`sudo mount /dev/sda1 /mnt/sda1` mount the drives
### scprime
`cd ~`
`mkdir scprime`
`cd scprime`
`sudo apt install python`
`sudo apt install smartmontools`
`sudo apt update`
`wget https://markwickline.com/scprime/install.py`
`wget https://markwickline.com/scprime/run.py`
`python3 install.py 1.6.0`
`python3 run.py init`
- BLOCKCHAIN NOW SYNCING, check back in a few hours and check consensus with spc
`cd current`
`./spc wallet init`
- copy paste seed to .ini file and backup documents
- add folders to all the drives
``
`./spc `


### Useful linux commands
`lsblk -S` list devices
