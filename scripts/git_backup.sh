#!/bin/bash

#Resource URL: https://youtu.be/LQmFUqjWiUs
#              https://devops.ionos.com/tutorials/use-ssh-keys-with-putty-on-windows/
#              https://github.com/th33xitus/kiauh/wiki/How-to-autocommit-config-changes-to-github%3F

# add this file to /home/pi directory on the raspberry pi that run your klipper service

#####################################################################
### Please set the paths accordingly. In case you don't have all  ###
### the listed folders, just keep that line commented out.        ###
#####################################################################
### Path to your config folder you want to backup
config_folder=~/klipper_config

### Path to your Klipper folder, by default that is '~/klipper'
klipper_folder=~/klipper

### Path to your Moonraker folder, by default that is '~/moonraker'
moonraker_folder=~/moonraker

### Path to your Mainsail folder, by default that is '~/mainsail'
mainsail_folder=~/mainsail

### Path to your Fluidd folder, by default that is '~/fluidd'
fluidd_folder=~/fluidd

#####################################################################
#####################################################################


#####################################################################
################ !!! DO NOT EDIT BELOW THIS LINE !!! ################
#####################################################################
grab_version(){
  if [ ! -z "$klipper_folder" ]; then
    echo -n "Getting klipper version="
    cd "$klipper_folder"
    klipper_commit=$(git rev-parse --short=7 HEAD)
    m1="Klipper on commit: $klipper_commit"
    echo $klipper_commit
    cd ..
  fi
  if [ ! -z "$moonraker_folder" ]; then
    echo -n "Getting moonraker version="
    cd "$moonraker_folder"
    moonraker_commit=$(git rev-parse --short=7 HEAD)
    m2="Moonraker on commit: $moonraker_commit"
    echo $moonraker_commit
    cd ..
  fi
  if [ ! -z "$mainsail_folder" ]; then
    echo -n "Getting mainsail version="
    mainsail_ver=$(head -n 1 $mainsail_folder/.version)
    m3="Mainsail version: $mainsail_ver"
    echo $mainsail_ver
  fi
  if [ ! -z "$fluidd_folder" ]; then
    echo -n "Getting fluidd version="
    fluidd_ver=$(head -n 1 $fluidd_folder/.version)
    m4="Fluidd version: $fluidd_ver"
    echo $fluidd_ver
  fi
}

push_config(){
  cd $config_folder
  echo "Copying executable scripts from klippy/extras folder to klipper_config/klippy_extras/ folder"
  find /home/pi/klipper/klippy/extras/*.py -perm /u+x,o+x -print0 | xargs -0 sh -c 'if [ $# -gt 0 ]; then cp -a "$@" /home/pi/klipper_config/klippy_extras/; fi' sh
  echo Pushing updates
  git pull -v
  git add . -v
  current_date=$(date +"%Y-%m-%d %T")
  git commit -m "Backup triggered on $current_date" -m "$m1" -m "$m2" -m "$m3" -m "$m4"
#  git push "git@github.com:GadgetAngel/Klipperbackup_Voron2.4r2_LDO300kit.git"
   git push
}

grab_version
push_config
