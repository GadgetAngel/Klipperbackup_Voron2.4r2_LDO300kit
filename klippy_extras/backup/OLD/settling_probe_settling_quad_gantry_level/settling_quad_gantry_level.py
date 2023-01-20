# Mechanicaly conforms a moving gantry to the bed with 4 Z steppers
#
# Copyright (C) 2018  Maks Zolin <mzolin@vorondesign.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

#
# Additional contribution are done by the following people:
# 
# URL Resource: https://github.com/voidtrance/voron/blob/master/printer/klipper/extras/probe.py
#
# add [settling_probe] section to your printer.cfg file
#      settling_sample = True
#
# add [settling_quad_gantry_level] section to your printer.cfg file
#
# Discord List:
#    voidtrance#5003
#    yak#0417
#    GadgetAngel#8701
#
import logging, quad_gantry_level
from . import settling_probe

# Leveling code for XY rails that are controlled by Z steppers as in:
#
# Z stepper1 ----> O                             O <---- Z stepper2
#                  | * <-- probe1   probe2 --> * |
#                  |                             |
#                  |                             | <--- Y2 rail
#   Y1 rail -----> |                             |
#                  |                             |
#                  |=============================|
#                  |            ^                |
#                  |            |                |
#                  |   X rail --/                |
#                  |                             |
#                  | * <-- probe0   probe3 --> * |
# Z stepper0 ----> O                             O <---- Z stepper3

class SettlingQuadGantryLevel(quad_gantry_level.QuadGantryLevel):
    def __init__(self, config):
        printer = config.get_printer()
        quadgantrylevel_config = config.getsection('quad_gantry_level')
        
        # Unregister any pre-existing probe commands first.
        gcode = printer.lookup_object('gcode')
        gcode.register_command('QUAD_GANTRY_LEVEL', None)
        
        quad_gantry_level.QuadGantryLevel.__init__(self, quadgantrylevel_config)
        
        self.probe_helper = settling_probe.ProbePointsHelper(quadgantrylevel_config, self.probe_finalize)
                
    def probe_finalize(self, offsets, positions):
        return quad_gantry_level.QuadGantryLevel.probe_finalize(self, offsets, positions)

def load_config(config):
    return SettlingQuadGantryLevel(config)
