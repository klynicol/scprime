#!/bin/bash
#============================================================================
# System Configuration
OS=none
PACKAGE=none
CURRENT_USER=$USER
HOME_DIRECTORY=$HOME
#============================================================================

installerDebian() {
    echo "Installing for Debian"
    sudo DEBIAN_FRONTEND=noninteractive apt install jq -y
    sudo DEBIAN_FRONTEND=noninteractive apt install curl docker.io -y
    sudo systemctl start docker
    sudo systemctl enable docker

    sudo usermod -aG docker $(whoami)
    if [ "" = "$SUDO_USER" ]; then
        # CURRENT_USER=$(whoami)
        CURRENT_USER=$USER
    else
        sudo usermod -aG docker $SUDO_USER
        CURRENT_USER=$SUDO_USER
    fi
    sudo usermod -aG docker $CURRENT_USER
    HOME_DIRECTORY=`eval echo ~$CURRENT_USER`

    stageWelcome
}

installerRedHat() {
    echo "Installing for RedHat"

    sudo yum install jq -y
    sudo yum install curl -y

    PKG_OK=$(sudo yum list installed | grep docker)
    if [ "" = "$PKG_OK" ]; then
        curl -fsSL https://get.docker.com/ | sh
        sudo systemctl start docker
        sudo systemctl enable docker
    else
        echo -e "${BLUE}â—${DEFAULT} Installation not required for docker.io"
    fi
    sudo usermod -aG docker $(whoami)

    stageWelcome
}

installerAlpine() {
    cp /etc/apk/repositories /tmp/repos
    echo "https://dl-cdn.alpinelinux.org/alpine/latest-stable/community" >> /etc/apk/repositories
    apk update
    apk add jq
    apk add libc6-compat gcompat libstdc++ docker
    rc-update add docker boot
    service docker start

    cp /tmp/repos /etc/apk/repositories
    apk update

    stageWelcome
}

hr() {
    echo -e "${BLUE}====================${DEFAULT}"
}

stageWelcome() {
curl -sSL https://releases.scpri.me/storage_appliance/diy/run-command.sh | sudo bash > ~/xm-run-command.txt
    curl -fsSL https://releases.scpri.me/storage_appliance/diy/xm-installer-linux -o xm-installer
    chmod +x xm-installer
    if [ -f /etc/alpine-release ]; then
        ./xm-installer
    else
        sudo ./xm-installer
    fi
    echo "Installer Finished"
    rm xm-installer
}

clear

if [ `whoami` != root ]; then
    echo Please run this script as root or using sudo
    exit
fi

fetchPackageManager() {
    if [ $PACKAGE = none ]; then
        declare -A osInfo;
        osInfo[/etc/redhat-release]=yum
        osInfo[/etc/arch-release]=pacman
        osInfo[/etc/gentoo-release]=emerge
        osInfo[/etc/SuSE-release]=zypp
        osInfo[/etc/debian_version]=apt-get
        osInfo[/etc/alpine-release]=apk

        for f in ${!osInfo[@]}
        do
            if [[ -f $f ]];then
                PACKAGE=${osInfo[$f]}
            fi
        done
    fi
}

installApp() {
    local PKG=$1

    case $PACKAGE in
        yum)
            PKG_OK=$(sudo yum list installed | grep $PKG)
            if [ "" = "$PKG_OK" ]; then
                echo -e "${GREEN}â—${DEFAULT} Installation required for $PKG"
                sudo yum install $PKG -y
            else
                echo -e "${BLUE}â—${DEFAULT} Installation not required for $PKG"
            fi
        ;;
        apt-get)
            PKG_OK=$(apt-cache policy $PKG | grep "Installed")
            PKG_OK=${PKG_OK#"  "}
            if [ "Installed: (none)" = "$PKG_OK" ]; then
                echo -e "${GREEN}â—${DEFAULT} Installation required for $PKG"
                sudo apt install $PKG -y
            else
                echo -e "${BLUE}â—${DEFAULT} Installation not required for $PKG"
            fi
        ;;
        apk)

        ;;
        *)
            echo "Currently this installer only works with the YUM and APT package managers."
        ;;
    esac;
}

function getOsID() {
    ID=`cat /etc/*release | grep ^ID=`
    ID=`echo $ID | sed -e "s/ID=//g"`
    ID=`echo $ID | tr -d '"'`
    ID=`echo $ID | awk '{print tolower($0)}'`
}

fetchPackageManager

getOsID

case $ID in
    debian|ubuntu)
        OS=Debian
        BACKTITLE="$BACKTITLE ($OS)"
        installerDebian
    ;;
    rhel|fedora|centos)
        OS=RedHat
        BACKTITLE="$BACKTITLE ($OS)"
        installerRedHat
    ;;
    alpine)
        OS=Alpine
        BACKTITLE="$BACKTITLE ($OS)"
        installerAlpine
    ;;
    *)
        echo "Your current OS is not supported: '$ID' - Please contact support."
        echo ""
        echo "You can run the installer manually however, please make sure you have the required dependancies: CURL and Docker"
        echo ""
        echo "Once ready run the following command:"
        echo "curl -fsSL https://releases.scpri.me/storage_appliance/diy/xm-installer-linux -o xm-installer && chmod +x xm-installer && ./xm-installer"
        hr
        echo ""
    ;;
esac
