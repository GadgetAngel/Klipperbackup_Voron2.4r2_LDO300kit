# Z-Probe support
#
# Copyright (C) 2017-2021  Kevin O'Connor <kevin@koconnor.net>
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
# Discord List:
#    voidtrance#5003
#    yak#0417
#    GadgetAngel#8701
#

import probe
import pins
from . import manual_probe

class SettlingProbe(probe.PrinterProbe):
    def __init__(self, config):
        printer = config.get_printer()
        probe_config = config.getsection('probe')
        probe_obj = printer.lookup_object('probe')

        if probe_obj:
            mcu_probe = probe_obj.mcu_probe
        else:
            mcu_probe = probe.ProbeEndstopWrapper(config)

        # Unregister any pre-existing probe commands first.
        gcode = printer.lookup_object('gcode')
        gcode.register_command('PROBE', None)
        gcode.register_command('QUERY_PROBE', None)
        gcode.register_command('PROBE_CALIBRATE', None)
        gcode.register_command('PROBE_ACCURACY', None)
        gcode.register_command('Z_OFFSET_APPLY_PROBE', None)

        pins = printer.lookup_object('pins')
        if 'probe' in pins.chips:
            pins.chips.pop('probe')
            pins.pin_resolvers.pop('probe')

        probe.PrinterProbe.__init__(self, probe_config, mcu_probe)
        self.settling_sample = config.getboolean('settling_sample', False)

    def run_probe(self, gcmd):
        if self.settling_sample:
            gcmd.respond_info("Settling sample (ignored)...")
            speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
            lift_speed = self.get_lift_speed(gcmd)
            sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
            pos = self._probe(speed)
            # move up
            self._move([None, None, pos[2] + sample_retract_dist], lift_speed)
        return probe.PrinterProbe.run_probe(self, gcmd)
        
    def cmd_PROBE_ACCURACY(self, gcmd):
        if self.settling_sample:
            gcmd.respond_info("Settling sample (ignored)...")
            speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
            lift_speed = self.get_lift_speed(gcmd)
            sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
            pos = self._probe(speed)
            # move up
            self._move([None, None, pos[2] + sample_retract_dist], lift_speed)
        return probe.PrinterProbe.cmd_PROBE_ACCURACY(self, gcmd)
        
class ProbePointsHelper(probe.ProbePointsHelper):
    def __init__(self, config, finalize_callback, default_points=None):
        self.printer = config.get_printer()
        
        probe_config = config.getsection('probe')
        #settling_probe_config = config.getsection('settling_probe')
        #probe.ProbePointsHelper.__init__(self, probe_config, finalize_callback, default_points=None)
        probe.ProbePointsHelper.__init__(self, config, finalize_callback, default_points=None)

    def start_probe(self, gcmd):
        manual_probe.verify_no_manual_probe(self.printer)
        
        # Lookup objects
        # probe = self.printer.lookup_object('probe', None)
        probe = self.printer.lookup_object('settling_probe', None)
        
        method = gcmd.get('METHOD', 'automatic').lower()
        self.results = []
        if probe is None or method != 'automatic':
            # Manual probe
            self.lift_speed = self.speed
            self.probe_offsets = (0., 0., 0.)
            self._manual_probe_start()
            return
        # Perform automatic probing
        self.lift_speed = probe.get_lift_speed(gcmd)
        self.probe_offsets = probe.get_offsets()
        if self.horizontal_move_z < self.probe_offsets[2]:
            raise gcmd.error("horizontal_move_z can't be less than"
                             " probe's z_offset")
        probe.multi_probe_begin()
        while 1:
            done = self._move_next()
            if done:
                break
            pos = probe.run_probe(gcmd)
            self.results.append(pos)
        probe.multi_probe_end()

def load_config(config):
    return SettlingProbe(config)