#!/bin/bash

#Resource URL: https://ttl255.com/jinja2-tutorial-part-4-template-filters/

# place this file in ~/klipper_config/scripts dirctory

# To make this file executable:
#  sudo chmod +x add_jinj2_custom_filter.sh


#####################################################################
### Please set the paths accordingly. In case you don't have all  ###
### the listed folders, just keep that line commented out.        ###
#####################################################################
### Path to your klipper environment folder
env_folder=~/klippy-env/bin/

### Path to your Klipper folder, by default that is '~/klipper'
klipper_folder=~/klipper

#####################################################################
#####################################################################


#####################################################################
################ !!! DO NOT EDIT BELOW THIS LINE !!! ################
#####################################################################
cd $klipper_folder
$env_folder/python $klipper_folder/strtodict_filter.py
