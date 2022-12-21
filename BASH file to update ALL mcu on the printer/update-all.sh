#!/usr/bin/env bash

########################################################################################################
########################################################################################################
# Requirements:
# Place this script in /home/pi/klipper 
# make this bash script file executable (update-all.sh):
# sudo chmod +x ~/klipper/update-all.sh
#
# warnig DO NOT redirect STDOUT to a file: the script will get errors!!
# you will need to be sitting in front of your computer when you run this script, it requires you to interact with it!
# You will need to hit the Q key to exit out of the "make menuconfig" commands.
# Even if you remove all the read commads from the script you will still need to hit Q to move past each of the "make menuconfig" commands
# cd ~/klipper
# ./update-all.sh 
#
# Please read through the notes in this file.  Especially one labeld "NOTE:" they are concerned
# with possible error message you might see that you do not have to worry about!

########################################################################################################
########################################################################################################
# This a script file that will update all the mcu in the ldo300kit:
#
# MCUs found in the ldo300kit:
#  1. Octopus Pro F446 boad via usb
#  2. EBB36v1.2 CAN BUS toolhead boad via CAN Bus using CanBoot 
#  3. RP2040 mcu on the TinyFAN PCB board via usb using CanBoot
#  4. Raspberry Pi 4B, it controls a 5V relay 
#
# Resources: 
#   https://docs.vorondesign.com/community/howto/drachenkatze/automating_klipper_mcu_updates.html
#   make menuconfig docs:
#      https://www.kernel.org/doc/html/latest/kbuild/kconfig-language.html
#      https://stackoverflow.com/questions/4178526/what-does-make-oldconfig-do-exactly-in-the-linux-kernel-makefile
#

#  stop the Klipper service on the raspberry pi
sudo service klipper stop
cd ~/klipper
# get the lateest from klipper on github
git pull

# uncomment the below line if you want to interact with this script:
read -p "Klipper's GitHub repo is downloaded, please check above for any errors. Press [Enter] to compile for Octopus Pro board, or [Ctrl+C] to abort"

########################################################################################################
########################################################################################################
# Octopus Pro F446 board (mcu)
#
# The Ocotopus Pro board uses the SD card to do firmware updates.
#
# ---------------------------------------------------------------
# NOTE1: for some reason the make flash command can cause the Octopus board to get confused. While runing this
# script if you see the following error you will need do a command manually after the script finished:
#  The error is:
#          dfu-util: Invalid DFU suffix signature
#          dfu-util: A valid DFU suffix will be required in a future dfu-util release!!!
#          dfu-util: No DFU capable USB device available
#
#          Failed to flash to /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00: Error running dfu-util
#
#          If the device is already in bootloader mode it can be flashed with the
#          following command:
#          make flash FLASH_DEVICE=0483:df11
#          OR
#          make flash FLASH_DEVICE=1209:beba
#
# what has happened is the make flash commad got confused, and now the Octopus board will look like (if you do a lsusb command):
# Bus 001 Device 030: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
#  you will see your ID number and name for your Octopus board has changedfrom "ID 1d50:614e OpenMoko, Inc. stm32f446xx" to "ID 0483:df11 STMicroelectronics STM Device in DFU Mode"
# DO NOT PANICK!  You board is just in bootloader mode so after the script finishes updating the rest of your mcu run the following command
# manually (at the command prompt):
# cd ~/klipper && make flash KCONFIG_CONFIG=<config.you_name_your_file> FLASH_DEVICE=0483:df11 (or the ID that shows up on the lsusb command)
#
# ---------------------------------------------------------------
#
#  [mcu]
#  serial:  /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00 -> /dev/ttyACM0
#
#  KCONFIG_CONFIG=config.octopus-pro-f446 for the BTT Octopus Pro (F446) V1.0 board
#  cat cd ~/klipper/config.octopus-pro-f446
#
#  cd cd ~/klipper
#  make clean KCONFIG_CONFIG=config.octopus-pro-f446
#  make menuconfig KCONFIG_CONFIG=config.octopus-pro-f446
#  make -j4 KCONFIG_CONFIG=config.octopus-pro-f446
#
#  make menuconfig options for BTT Octopus Pro (F446) v1.0 using Klipper firmware:
#       [*]Enable extra low-level configuration options
#       Micro-controller Architecture (STM32)
#       Procesor model (STM32F446)
#       Bootloader offset (32KiB bootloader)
#       Clock Reference (12 MHz crystal)
#       Communication interface (USB (on PA11/PA12))
#       
#  ls -la /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00
#      lrwxrwxrwx 1 root root 13 Dec 19 04:37 /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00 -> ../../ttyACM0
#      ↑ Since their is an "l" as the first symbol then this is a symbolic link to /dev/ttyACM0
#      ls -la /dev/ttyACM0
#          crw-rw---- 1 root dialout 166, 0 Dec 19 14:23 /dev/ttyACM0
#          /dev/ttyACM0 is not a symbolic link!
#   so the Octopus Pro is using /dev/ttyACM0 
#
#  Resources:
#     https://docs.vorondesign.com/build/software/octopus_klipper.html
#
# setup and compile the Klipper firmware for the Octopus Pro (F446) mcu
make clean KCONFIG_CONFIG=config.octopus-pro-f446
make menuconfig KCONFIG_CONFIG=config.octopus-pro-f446
make -j4 KCONFIG_CONFIG=config.octopus-pro-f446

# uncomment the below line if you want to interact with this script:
read -p "Octopus Pro (F446) firmware had been built, please check above for any errors. Press [Enter] to flash the Octopus Pro, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the Octopus Pro (F446) mcu memeory 
make flash KCONFIG_CONFIG=config.octopus-pro-f446 FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00

#if you see this:
# Failed to flash to /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00: Error running dfu-util
# abort the script and run the following command:
# do a lsusb to find out what device id you have:
# lsusb 
#    Bus 001 Device 030: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
# make flash KCONFIG_CONFIG=config.octopus-pro-f446 FLASH_DEVICE=0483:df11

# uncomment the below line if you want to interact with this script:
read -p "Octopus Pro firmware has been flashed, please check above for any errors (IGNORE dfu-util: can't detach message). Press [Enter] to compile for EBB36v1.2 board, or [Ctrl+C] to abort"

########################################################################################################
########################################################################################################
# EBB36v1.2 mcu with CanBoot Bootloader on the CAN bus
#
# ---------------------------------------------------------------
# NOTE2: Since we need to place the EBB36 board into a programming mode so that CanBoot can send it a file update
# you will see the following message, but they do not mean an error has occurred!
#
#
#  The sofware was designed to display these messages when going into programming mode:
#
#   Flashing out/klipper.bin to /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
# Entering bootloader on /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
# Device reconnect on /sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.2/1-1.2.4
# sudo lib/rp2040_flash/rp2040_flash out/klipper.bin 1 32
#
# Loaded UF2 image with 0 pages
# No rp2040 in BOOTSEL mode was found
#
# DO NOT PANICK!  Just ignore them!
# it just means you board has been place in programming mode!
#
# ---------------------------------------------------------------
#
# ---------------------------------------------------------------
# NOTE3: for some reason the Waveshare RS485 CAN hat can cause errors if you are usig it. Arksine talks about it in the 
# notes secion: https://github.com/Arksine/CanBoot#notes
# If you see the following error you will not have to do anything, except check that your Toolhead board did get updated after
# your printer boots back up (at the end of the script).  Just ignore the errors.  The errors occur during the READ back or
# verification phase. Here is what the error looks like:
#  The error is:
#
#       Verifying (block count = 414)...
#
#       [ERROR:root:Can Read Error
#       Traceback (most recent call last):
#         File "/usr/lib/python3.9/asyncio/streams.py", line 632, in readuntil
#           await self._wait_for_data('readuntil')
#         File "/usr/lib/python3.9/asyncio/streams.py", line 517, in _wait_for_data
#           await self._waiter
#        asyncio.exceptions.CancelledError
#
# DO NOT PANICK!  Just ignore error especially if you see the following after the errors:
#     #################################################]
#
#      Verification Complete: SHA = 5F0ACB276808AA18068C195419A1AD2F21ADE7AA
#      CAN Flash Success
#
# Let the scipt go on its way but double check your Can Bus Toolhead board did get its update, by looking in your UI section called
# "System Loads" -- it will tell you what version of Klipper each mcu is running
# ---------------------------------------------------------------
#  [mcu EBBCan]
#  canbus_uuid: befe3bd16119
#
#  KCONFIG_CONFIG=config.CanBoot.ebb36v1.2 for the EBB36v1.2
#  cat ~/CanBoot/config.CanBoot.ebb36v1.2
#
#  cd ~/CanBoot
#  make clean KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
#  make menuconfig KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
#  make -j4 KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
#
#  make menuconfig options CANBOOT bootloader for EBB36v1.2:
#       Micro-controller Architecture (STM32)
#       Procesor model (STM32G0B1)
#       Clock Reference (8 MHz crystal)
#       Build CanBoot deployment application (Do not build)
#       Communication interface (CAN bus (on PB0/PB1))
#       Application start offset (8KiB offset)
#  (500000) CAN bus speed
#  * Support bootloader entry on rapid double click of reset button
#
# To flash CANBOOT bootloader to EBB36v1.2 board:
# $ sudo dfu-util -a 0 -D ~/CanBoot/out/canboot.bin --dfuse-address 0x08000000:force:mass-erase:leave -d 0483:df11
# 
#  KCONFIG_CONFIG=config.ebb36v1.2
#  cat ~/klipper/config.ebb36v1.2
#
#  cd ~/klipper
#  make clean KCONFIG_CONFIG=config.ebb36v1.2
#  make menuconfig KCONFIG_CONFIG=config.ebb36v1.2
#  make -j4 KCONFIG_CONFIG=config.ebb36v1.2
#
#  make menuconfig options for EBB36v1.2 using Klipper firmware with CANBOOT bootloader:
#       [*]Enable extra low-level configuration options
#       Micro-controller Architecture (STM32)
#       Procesor model (STM32G0B1)
#       Bootloader offset (8KiB bootloader)
#       Clock Reference (8 MHz crystal)
#       Communication interface (CAN bus (on PB0/PB1))
#  (500000) CAN bus speed
#
#  Resources:
#     https://github.com/maz0r/klipper_canbus/blob/main/toolhead/ebb36-42_v1.1.md
#     https://discord.com/channels/460117602945990666/1000794039832035530/1031354886908031128
#
# setup and compile the Klipper firmware for the EBB36v1.2 mcu
make clean KCONFIG_CONFIG=config.ebb36v1.2
make menuconfig KCONFIG_CONFIG=config.ebb36v1.2
make -j4 KCONFIG_CONFIG=config.ebb36v1.2

# uncomment the below line if you want to interact with this script:
read -p "EBB36v1.2 Klipper firmware had been built, please check above for any errors. Press [Enter] to flash EBB36 via the CAN bus, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the EBB36v1.2 mcu memeory
python3 ~/CanBoot/scripts/flash_can.py -i can0 -f ~/klipper/out/klipper.bin -u befe3bd16119

# uncomment the below line if you want to interact with this script:
read -p "EBB36v1.2 firmware has been flashed via the CAN Bus, please check above for any errors. Press [Enter] to compile for RP2040 board, or [Ctrl+C] to abort"

########################################################################################################
########################################################################################################
# This is my RP2040-zero TESTING mcu  (W25Q16JVUXIQ 2MB NOR-Flash) WITH CANBOOT bootloader
#
# [mcu testing_ro2040] 
#  # Testing CanBoot bootloader for RP2040 that will be used on the TinyFan PCB board
#  serial: /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00  --> /dev/ttyACM2
#
#  [mcu tinyfan]
#  # actural working RP2040 on TinyFan PCB but this one does NOT have the CanBoot bootloader installed!
#  serial: /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00 -> /dev/ttyACM1
#
#  KCONFIG_CONFIG=config.CanBoot.rp2040 for the RP2040-zero
#  cat ~/CanBoot/config.CanBoot.rp2040
#
#  cd ~/CanBoot  
#  make clean KCONFIG_CONFIG=config.CanBoot.rp2040
#  make menuconfig KCONFIG_CONFIG=config.CanBoot.rp2040
#  make -j4 KCONFIG_CONFIG=config.CanBoot.rp2040
#
#  make menuconfig options CANBOOT bootloader for RP2040-zero:
#       Micro-controller Architecture (Raspberry Pi RP2040)
#       Flash chip (W25Q080 with CLKDIV 2)
#       Build CanBoot deployment application (Do not build)
#       Communication interface (USB)
#       USB ids -->  USB Vendor ID: 0x1d50; USB device ID: 0x614e; USB serial number from CHIPID : E0C9125B0D9B  
#       [*] Support bootloader entry on rapid double click of reset button
#       [ ] Enable bootloader entry on button (or gpio) state  
#       ( ) Button GPIO Pin  
#       [ ] Enable Status LED
#       () Status LED GPIO Pin
#
# official board of rp2040 uses W25Q16JVUXIQ , the Waveshare RP2040 uses W25Q16JVUXIQ
#
# To flash CANBOOT bootloader to rp2040-zero  the first time (lsusb):
#make flash KCONFIG_CONFIG=config.CanBoot.rp2040 FLASH_DEVICE="2e8a:0003" 
# if you ever need to reflash CanBoot bootloader you will have to hit HOLD down the "BOOT" button will plugging in the USB cable to force
# the RP2040 into BOOTSEL mode should see "Bus 001 Device 040: ID 2e8a:0003 Raspberry Pi RP2 Boot"
#make flash KCONFIG_CONFIG=config.CanBoot.rp2040 FLASH_DEVICE="2e8a:0003"
#after flash takes you will see "Bus 001 Device 041: ID 1d50:614e OpenMoko, Inc. rp2040"
#
# lsusb output:
# Bus 001 Device 041: ID 1d50:614e OpenMoko, Inc. rp2040
#
# ls /dev/serial/by-id/*
# output:
#    /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
# ls -la /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -> /dev/ttyACM2
#
# 
#  KCONFIG_CONFIG=config.rp240_withBootloader
#  cat ~/klipper/config.rp240_withBootloader
#
#  cd ~/klipper
#  make clean KCONFIG_CONFIG=config.rp240_withBootloader
#  make menuconfig KCONFIG_CONFIG=config.rp240_withBootloader
#  make -j4 KCONFIG_CONFIG=config.rp240_withBootloader
#
#  make menuconfig options for RP2040 using Klipper firmware with CANBOOT bootloader:
#       [*]Enable extra low-level configuration options
#       Micro-controller Architecture (Raspbery Pi RP2040)
#       Bootloader offset (16Kib Bootloader)
#       Communication interface (USB)
#       USB ids -->  USB Vendor ID: 0x1d50; USB device ID: 0x614e; USB serial number from CHIPID : E0C9125B0D9B 
#       () GPIO pins to set at micro-controller startup
#
#  ls -la /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
#      lrwxrwxrwx 1 root root 13 Dec 19 22:31 /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -> ../../ttyACM2
#      ls -la /dev/ttyACM2
#          crw-rw---- 1 root dialout 166, 1 Dec 19  2022 /dev/ttyACM2
#          /dev/ttyACM2 is not a symbolic link!
#    so the RP2040-zero mcu is using /dev/ttyACM2
#
# To Flash Klipper to RP2040 the very "FIRST TIME" (when The first 64-bits of the application area area cleared) or (when you have reflashed the CanBoot Bootloader) do the following:
# python3 ~/CanBoot/scripts/flash_can.py -d /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -v -f ~/klipper/out/klipper.bin
#
# After flash_can.py updates the appication area and resets the RP2040, the RP2040 will enumerate on the USB bus and change
# the /dev/serial/by-id/
#
# ls /dev/serial/by-id/*
# output:
#    The new ID is: /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
#
# ls -la /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
#     lrwxrwxrwx 1 root root 13 Dec 20 13:22 /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00 -> ../../ttyACM2
# so the RP2040-zero mcu is using /dev/ttyACM2
# having lsusb:
# Bus 001 Device 042: ID 1d50:614e OpenMoko, Inc. rp2040, notice the Device number is now 42 when it was 41
#
#  Resources:
#     https://github.com/Gi7mo/TinyFan/tree/main/Klipper#installation-steps
#
## WITH CANBOOT BOOTLOADER to update the Klipper firmware mcu:
## setup and compile the Klipper firmware for the RP2040-zero mcu WITH CANBOOT bootloader
make clean KCONFIG_CONFIG=config.rp240_withBootloader
make menuconfig KCONFIG_CONFIG=config.rp240_withBootloader
make -j4 KCONFIG_CONFIG=config.rp240_withBootloader

# uncomment the below line if you want to interact with this script:
read -p "RP2040-zero firmware with CanBoot bootloader has been built, please check above for any errors. Press [Enter] to enter programming mode or [Ctrl+C] to abort"

# to enter programming mode for the RP2040 via USB (so you do not have to press a damn button):
make flash KCONFIG_CONFIG=config.rp240_withBootloader FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00

# uncomment the below line if you want to interact with this script:
read -p "RP2040-zero has been placed into programming mode, please check above for any errors. Press [Enter] to flash RP2040 via USB, or [Ctrl+C] to abort"

# After the make flash command the RP2040 will be in programming mode but the /dev/serial/by-id/ will change:
## actually flash the updated klipper firmware to the RP2040-zero mcu over USB:
python3 ~/CanBoot/scripts/flash_can.py -d /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -f ~/klipper/out/klipper.bin
# After CanBoot reset the device the /dev/serial/by-id/ will change back to /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00

# uncomment the below line if you want to interact with this script:
read -p "RP2040-zero with CanBoot bootloader and Klipper firmware has been flashed, please check above for any errors. Press [Enter] to compile for Raspberry Pi 4B, or [Ctrl+C] to abort"

########################################################################################################
########################################################################################################
# Raspberry pi mcu
#
#  [mcu rpi]
#  serial: /tmp/klipper_host_mcu -> /dev/pts/0
#
#  KCONFIG_CONFIG=config.rpi
#  cat ~/klipper/config.rpi
#
#  cd ~/klipper
#  make clean KCONFIG_CONFIG=config.rpi
#  make menuconfig KCONFIG_CONFIG=config.rpi
#
#  make menuconfig options for Raspberry Pi 4B so it can be used as a secondary MCU:
#       [ ]Enable extra low-level configuration options
#       Micro-controller Architecture (Linux process)
#
#  ls -la /tmp/klipper_host_mcu
#      lrwxrwxrwx 1 root root 10 Dec 19 04:37 /tmp/klipper_host_mcu -> /dev/pts/0
#      ↑ since their is an "l" as the first symbol then this is a symbolic link to /dev/pts/0
#      ls -la /dev/pts/0
#          crw-rw---- 1 root tty 136, 0 Dec 19 14:25 /dev/pts/0
#          /dev/pts/0  is not a symbolic link!
#   so the raspberry pi mcu is using /dev/pts/0
#
#  Resources:
#     https://www.klipper3d.org/RPi_microcontroller.html#building-the-micro-controller-code
#
# setup and compile the Klipper firmware for the Raspberry pi seondary mcu 
make clean KCONFIG_CONFIG=config.rpi
make menuconfig KCONFIG_CONFIG=config.rpi
make -j4 KCONFIG_CONFIG=config.rpi

# uncomment the below line if you want to interact with this script:
read -p "RPi firmware has been built, please check above for any errors. Press [Enter] to flash Raspberry Pi, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the Raspberry pi seondary mcu 
make flash KCONFIG_CONFIG=config.rpi

# start the Klipper service back up on the raspberry pi
sudo service klipper start

# uncomment the below line if you want to interact with this script:
read -p "The Klipper Service has been started. Ensure your printer is up and running with out errors. Press [Enter] to exit this script"
