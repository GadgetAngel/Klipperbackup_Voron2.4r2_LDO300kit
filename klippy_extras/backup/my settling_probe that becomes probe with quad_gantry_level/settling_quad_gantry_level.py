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
from . import settling_probe, probe

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
        self.printer = config.get_printer()
        quadgantrylevel_config = config.getsection('quad_gantry_level')
        
        # Unregister any pre-existing probe commands first.
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('QUAD_GANTRY_LEVEL', None)
        
        quad_gantry_level.QuadGantryLevel.__init__(self, quadgantrylevel_config)
        
        self.probe_helper = probe.ProbePointsHelper(quadgantrylevel_config, self.probe_finalize)
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
        
    def handle_ready(self):
        time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.probe_obj = self.printer.lookup_object('probe')
        settling_status = self.probe_obj.get_status(time)
        self.settling_sample = settling_status['settling_sample']
        qgl_obj = self.printer.objects.pop('quad_gantry_level', None)
        self.printer.objects['quad_gantry_level'] = self
        del qgl_obj
        
    def cmd_QUAD_GANTRY_LEVEL(self, gcmd):
        self.probe_obj.settling_sample = gcmd.get_int("SETTLING_SAMPLE", self.settling_sample)
        return quad_gantry_level.QuadGantryLevel.cmd_QUAD_GANTRY_LEVEL(self, gcmd) 
                
    def probe_finalize(self, offsets, positions):
        return quad_gantry_level.QuadGantryLevel.probe_finalize(self, offsets, positions)

def load_config(config):
    return SettlingQuadGantryLevel(config)
