# Mechanicaly conforms a moving gantry to the bed with 4 Z steppers
#
# Copyright (C) 2018  Maks Zolin <mzolin@vorondesign.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
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
        
        self.probe_helper = settling_probe.ProbePointsHelper(quadgantrylevel_config, quad_gantry_level.probe_finalize)

def load_config(config):
    return SettlingQuadGantryLevel(config)
