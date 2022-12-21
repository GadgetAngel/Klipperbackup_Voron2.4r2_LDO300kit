#!/usr/bin/env bash

# This a script file that will update all the mcu in the ldo300kit
# place this script in /home/pi/klipper 
#
# MCUs found in the ldo300kit:
#  1. Octopus Pro F446 boad
#  2. EBB36v1.2 CAN BUS toolhead boad
#  3. RP2040 mcu on the TinyFAN PCB board
#  4. Raspberry Pi 4B, it controls a 5V relay
#
# Resources: 
#   https://docs.vorondesign.com/community/howto/drachenkatze/automating_klipper_mcu_updates.html
#

#  stop the Klipper service on the raspberry pi
sudo service klipper stop
cd ~/klipper
# get the latestest from klipper on github
git pull

# Octopus Pro F446 board (mcu)
#
#  [mcu]
#  serial: /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00
#
#  KCONFIG_CONFIG=config.octopus-pro-f446 for the BTT Octopus Pro (F446) V1.0 board
#  cat cd ~/klipper/config.octopus-pro-f446
#
#  cd cd ~/klipper
#  make clean KCONFIG_CONFIG=config.octopus-pro-f446
#  make menuconfig KCONFIG_CONFIG=config.octopus-pro-f446
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
make KCONFIG_CONFIG=config.octopus-pro-f446
read -p "Octopus Pro (F446) firmware had been built, please check above for any errors. Press [Enter] to continue flashing, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the Octopus Pro (F446) mcu memeory
./scripts/flash-sdcard.sh /dev/ttyACM0 btt-octopus-pro-f446-v1.0
read -p "Octopus Pro (F446) firmware has been flashed, please check above for any errors. Press [Enter] to continue, or [Ctrl+C] to abort"

# EBB36v1.2 mcu
#
#  [mcu EBBCan]
#  canbus_uuid: befe3bd16119
#
#  KCONFIG_CONFIG=config.CanBoot.ebb36v1.2 for the EBB36v1.2
#  cat ~/CanBoot/config.CanBoot.ebb36v1.2
#
#  cd ~/CanBoot
#  make clean KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
#  make menuconfig KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
#  make KCONFIG_CONFIG=config.CanBoot.ebb36v1.2
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
#
# setup and compile the Klipper firmware for the EBB36v1.2 mcu
make clean KCONFIG_CONFIG=config.ebb36v1.2
make menuconfig KCONFIG_CONFIG=config.ebb36v1.2
make KCONFIG_CONFIG=config.ebb36v1.2
read -p "EBB36v1.2 firmware had been built, please check above for any errors. Press [Enter] to continue flashing, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the EBB36v1.2 mcu memeory
python3 ~/CanBoot/scripts/flash_can.py -i can0 -f ~/klipper/out/klipper.bin -u befe3bd16119
read -p "EBB36v1.2 firmware has been flashed, please check above for any errors. Press [Enter] to continue, or [Ctrl+C] to abort"

# RP2040-zero mcu on the TinyFan PCB board (W25Q16JVUXIQ 2MB NOR-Flash) WITH CANBOOT bootloader
#
#  [mcu tinyfan]
#  serial: /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00
#
#  KCONFIG_CONFIG=config.CanBoot.rp2040 for the RP2040-zero
#  cat ~/CanBoot/config.CanBoot.rp2040
#
#  cd ~/CanBoot  
  make clean KCONFIG_CONFIG=config.CanBoot.rp2040
  make menuconfig KCONFIG_CONFIG=config.CanBoot.rp2040
  make -j4 KCONFIG_CONFIG=config.CanBoot.rp2040
#
#  make menuconfig options CANBOOT bootloader for RP2040-zero:
#       Micro-controller Architecture (Raspberry Pi RP2040)
#       Flash chip (W25Q080 with CLKDIV 2)
#       Build CanBoot deployment application (Do not build)
#       Communication interface (USB)
#       USB ids -->  USB Vendor ID: 0x2e8a; USB device ID: 0x0003; USB serial number from CHIPID : E0C9125B0D9B
#       [*] Support bootloader entry on rapid double click of reset button
#       [*] Enable bootloader entry on button (or gpio) state  --- not used at this time
#       (!gpio29) Button GPIO Pin  --- not used at this time
#       [*] Enable Status LED
#       (gpio16) Status LED GPIO Pin
#  * Support bootloader entry on rapid double click of reset button
#
# official board of rp2040 uses W25Q16JVUXIQ , the Waveshare RP2040 uses W25Q16JVUXIQ
#
# dmesg | tail -n20 
# output from dmesg:
# [ 5442.488982] usb 1-1.2.4: new full-speed USB device number 28 using xhci_hcd
# [ 5442.618175] usb 1-1.2.4: New USB device found, idVendor=2e8a, idProduct=0003, bcdDevice= 1.00
# [ 5442.618206] usb 1-1.2.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
# [ 5442.618219] usb 1-1.2.4: Product: RP2 Boot
# [ 5442.618230] usb 1-1.2.4: Manufacturer: Raspberry Pi
# [ 5442.618239] usb 1-1.2.4: SerialNumber: E0C9125B0D9B
# [ 5442.623063] usb-storage 1-1.2.4:1.0: USB Mass Storage device detected
# [ 5442.623779] scsi host1: usb-storage 1-1.2.4:1.0
# [ 5443.654017] scsi 1:0:0:0: Direct-Access     RPI      RP2              3    PQ: 0 ANSI: 2
# [ 5443.654326] sd 1:0:0:0: Attached scsi generic sg1 type 0
# [ 5443.657543] sd 1:0:0:0: [sdb] 262144 512-byte logical blocks: (134 MB/128 MiB)
# [ 5443.660248] sd 1:0:0:0: [sdb] Write Protect is off
# [ 5443.660265] sd 1:0:0:0: [sdb] Mode Sense: 03 00 00 00
# [ 5443.667335] sd 1:0:0:0: [sdb] No Caching mode page found
# [ 5443.667353] sd 1:0:0:0: [sdb] Assuming drive cache: write through
# [ 5443.678637]  sdb: sdb1
# [ 5443.686752] sd 1:0:0:0: [sdb] Attached SCSI removable disk
#
#$ lsusb 
# output:
#Bus 001 Device 028: ID 2e8a:0003 Raspberry Pi RP2 Boot
#
# pi@LDO300kit:~/CanBoot $ make -j4 KCONFIG_CONFIG=config.CanBoot.rp2040
  # Creating symbolic link out/board
  # Building out/autoconf.h
  # Building out/lib/rp2040/elf2uf2/elf2uf2
  # Compiling out/src/sched.o
  # Compiling out/src/bootentry.o
  # Compiling out/src/command.o
  # Compiling out/src/flashcmd.o
  # Compiling out/src/initial_pins.o
  # Compiling out/src/led.o
  # Compiling out/src/rp2040/armcm_canboot.o
  # Compiling out/src/rp2040/main.o
  # Compiling out/src/rp2040/gpio.o
  # Compiling out/src/rp2040/timer.o
  # Compiling out/src/rp2040/flash.o
  # Compiling out/src/../lib/rp2040/pico/flash/hw_flash.o
  # Compiling out/src/generic/armcm_irq.o
  # Compiling out/src/generic/crc16_ccitt.o
  # Compiling out/src/rp2040/usbserial.o
  # Compiling out/src/generic/usb_cdc.o
  # Compiling out/src/rp2040/chipid.o
  # Building rp2040 stage2 out/stage2.o
  # Preprocessing out/src/rp2040/rp2040_link.ld
  # Building out/compile_time_request.o
  # Linking out/canboot.elf
  # Creating bin file out/canboot.bin
  # Creating uf2 file out/canboot.uf2
# pi@LDO300kit:~/CanBoot $
#
# To flash CANBOOT bootloader to rp2040-zero (lsusb):
sudo make flash KCONFIG_CONFIG=config.CanBoot.rp2040 FLASH_DEVICE="2e8a:0003" 
# output:
# pi@LDO300kit:~/CanBoot $ sudo make flash KCONFIG_CONFIG=config.CanBoot.rp2040 FLASH_DEVICE="2e8a:0003"
  # Flashing out/canboot.uf2
# Loaded UF2 image with 20 pages
# Found rp2040 device on USB bus 1 address 28
# Flashing...
# Resetting interface
# Locking
# Exiting XIP mode
# Erasing
# Flashing
# Rebooting device
# pi@LDO300kit:~/CanBoot 
#
# lsusb:
# output:
# Bus 001 Device 029: ID 2e8a:0003 CanBoot rp2040
# ls /dev/serial/by-id/*
# output:
# pi@LDO300kit:~/CanBoot $ ls /dev/serial/by-id/*
# /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
# /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00
# /dev/serial/by-id/usb-Klipper_stm32f446xx_0F003E00095053424E363420-if00
#
# this is the rp2040 with CanBoot bootloader:
# /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
#  ls -la /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
# lrwxrwxrwx 1 root root 13 Dec 20 01:58 /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -> ../../ttyACM2
# so this RP2040 is using /dev/ttyACM2
#
# Bus 001 Device 030: ID 2e8a:0003 CanBoot rp2040
# /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
# 
#  KCONFIG_CONFIG=config.rp240_withBootloader
#  cat ~/klipper/config.rp240_withBootloader
#
#  cd ~/klipper
#  make clean KCONFIG_CONFIG=config.rp240_withBootloader
#  make menuconfig KCONFIG_CONFIG=config.rp240_withBootloader
#
#  make menuconfig options for RP2040 using Klipper firmware with CANBOOT bootloader:
#       [*]Enable extra low-level configuration options
#       Micro-controller Architecture (Raspbery Pi RP2040)
#       Bootloader offset (16Kib Bootloader)
#       Communication interface (USB)
#       USB ids -->  USB Vendor ID: 0x2e8a; USB device ID: 0x0003; USB serial number from CHIPID : E0C9125B0D9B
#       (gpio16) GPIO pins to set at micro-controller startup
#
#  ls -la /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00
#      lrwxrwxrwx 1 root root 13 Dec 19 22:31 /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -> ../../ttyACM2
#      ls -la /dev/ttyACM2
#          crw-rw---- 1 root dialout 166, 1 Dec 19  2022 /dev/ttyACM2
#          /dev/ttyACM2 is not a symbolic link!
#    so the RP2040-zero mcu is using /dev/ttyACM2
#
#  Resources:
#     https://github.com/Gi7mo/TinyFan/tree/main/Klipper#installation-steps
#
## WITH CANBOOT BOOTLOADER:
## setup and compile the Klipper firmware for the RP2040-zero mcu WITH CANBOOT bootloader

make clean KCONFIG_CONFIG=config.rp240_withBootloader
make menuconfig KCONFIG_CONFIG=config.rp240_withBootloader
make -j4 KCONFIG_CONFIG=config.rp240_withBootloader
#read -p "RP2040-zero firmware with CanBoot bootloader has been built, please check above for any errors. Press [Enter] to continue flashing, or [Ctrl+C] to abort"

# output from klipper compile with CanBoot  bootloader:
# pi@LDO300kit:~/klipper $ make -j4 KCONFIG_CONFIG=config.rp240_withBootloader
  # Creating symbolic link out/board
  # Building out/autoconf.h
  # Compiling out/src/sched.o
  # Compiling out/src/command.o
  # Compiling out/src/basecmd.o
  # Compiling out/src/debugcmds.o
  # Compiling out/src/initial_pins.o
  # Compiling out/src/gpiocmds.o
  # Compiling out/src/stepper.o
  # Compiling out/src/endstop.o
  # Compiling out/src/trsync.o
  # Compiling out/src/adccmds.o
  # Compiling out/src/spicmds.o
  # Compiling out/src/thermocouple.o
  # Compiling out/src/i2ccmds.o
  # Compiling out/src/pwmcmds.o
  # Compiling out/src/spi_software.o
  # Compiling out/src/sensor_adxl345.o
  # Compiling out/src/sensor_angle.o
  # Compiling out/src/sensor_mpu9250.o
  # Compiling out/src/lcd_st7920.o
  # Compiling out/src/lcd_hd44780.o
  # Compiling out/src/buttons.o
  # Compiling out/src/tmcuart.o
  # Compiling out/src/neopixel.o
  # Compiling out/src/pulse_counter.o
  # Compiling out/src/rp2040/main.o
  # Compiling out/src/rp2040/watchdog.o
  # Compiling out/src/rp2040/gpio.o
  # Compiling out/src/rp2040/adc.o
  # Compiling out/src/rp2040/timer.o
  # Compiling out/src/rp2040/bootrom.o
  # Compiling out/src/generic/armcm_boot.o
  # Compiling out/src/generic/armcm_irq.o
  # Compiling out/src/generic/armcm_reset.o
  # Compiling out/src/generic/timer_irq.o
  # Compiling out/src/generic/crc16_ccitt.o
  # Compiling out/src/rp2040/usbserial.o
  # Compiling out/src/generic/usb_cdc.o
  # Compiling out/src/rp2040/chipid.o
  # Compiling out/src/rp2040/hard_pwm.o
  # Compiling out/src/rp2040/spi.o
  # Compiling out/src/rp2040/i2c.o
  # Preprocessing out/src/generic/armcm_link.ld
  # Building out/compile_time_request.o
# Version: v0.11.0-40-gaac613bf
  # Linking out/klipper.elf
  # Creating bin file out/klipper.bin
#
## actually flash the klipper firmware to the RP2040-zero mcu
python3 ~/CanBoot/scripts/flash_can.py -d /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00 -v -f ~/klipper/out/klipper.bin
make flash KCONFIG_CONFIG=config.rp240_withBootloader FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
#read -p "RP2040-zero firmware with CanBoot bootloader has been flashed, please check above for any errors. Press [Enter] to continue, or [Ctrl+C] to abort"

#output from flash:
# pi@LDO300kit:~/CanBoot $ python3 ~/CanBoot/scripts/flash_can.py -d /dev/serial/by-id/usb-CanBoot_rp2040_E0C9125B0D9B-if00 -v -f ~/klipper/out/klipper.bin
# Attempting to connect to bootloader
# CanBoot Connected
# Protocol Version: 1.0.0
# Block Size: 64 bytes
# Application Start: 0x10004000
# MCU type: rp2040
# Flashing '/home/pi/klipper/out/klipper.bin'...
#
# [##################################################]
#
# Write complete: 99 pages
# Verifying (block count = 395)...
#
# [##################################################]
#
# Verification Complete: SHA = 04993AB63FF180D56A1A73C96099D065A70C4570
# CAN Flash Success
#
#
#ls /dev/serial/by-id/*
# /dev/serial/by-id/usb-Klipper_rp2040_E0C9125B0D9B-if00
# lsusb:
# Bus 001 Device 031: ID 2e8a:0003 Klipper rp2040


# RP2040-zero mcu on the TinyFan PCB board (W25Q16JVUXIQ 2MB NOR-Flash) without an additional bootloader
#
#  [mcu tinyfan]
#  serial: /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00
#
#  KCONFIG_CONFIG=config.rp240
#  cat ~/klipper/config.rp240
#
#  cd ~/klipper
#  make clean KCONFIG_CONFIG=config.rp240
#  make menuconfig KCONFIG_CONFIG=config.rp240
#
#  make menuconfig options for RP2040 using Klipper firmware without a bootloader:
#       [*]Enable extra low-level configuration options
#       Micro-controller Architecture (Raspbery Pi RP2040)
#       Bootloader offset (No bootloader)
#       Flash chip (W25Q080 with CLKDIV 2) (GENERIC_03H with CLKDIV 4)
#       Communication interface (USB)
#
#  ls -la /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00
#      lrwxrwxrwx 1 root root 13 Dec 19 04:37 /dev/serial/by-id/usb-Klipper_rp2040_E66138935F916E28-if00 -> ../../ttyACM1
#      ↑ Since their is an "l" as the first symbol then this is a symbolic link to /dev/ttyACM1
#      ls -la /dev/ttyACM1
#          crw-rw---- 1 root dialout 166, 1 Dec 19  2022 /dev/ttyACM1
#          /dev/ttyACM1 is not a symbolic link!
#    so the RP2040-zero mcu is using /dev/ttyACM1
#
# lsusb output:
# Bus 001 Device 013: ID 2e8a:0003 Raspberry Pi RP2 Boot
#
#  Resources:
#     https://github.com/Gi7mo/TinyFan/tree/main/Klipper#installation-steps
#
# setup and compile the Klipper firmware for the RP2040-zero mcu without an additional bootloader
make clean KCONFIG_CONFIG=config.rp2040
make menuconfig KCONFIG_CONFIG=config.rp2040
make KCONFIG_CONFIG=config.rp2040
read -p "RP2040-zero firmware has been built, please check above for any errors. Press [Enter] to continue flashing, or [Ctrl+C] to abort"

make flash FLASH_DEVICE="2e8a:0003" 
read -p "RP2040-zero firmware has been flashed, please check above for any errors. Press [Enter] to continue, or [Ctrl+C] to abort"

# Raspberry pi mcu
#
#  [mcu rpi]
#  serial: /tmp/klipper_host_mcu
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
make KCONFIG_CONFIG=config.rpi
read -p "RPi firmware has been built, please check above for any errors. Press [Enter] to continue flashing, or [Ctrl+C] to abort"

# actually flash the klipper firmware to the Raspberry pi seondary mcu 
make flash KCONFIG_CONFIG=config.rpi

# start the Klipper service back up on the raspberry pi
sudo service klipper start
