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

class SettlingProbe(probe.PrinterProbe):
    def __init__(self, config):
        self.printer = config.get_printer()
        probe_config = config.getsection('probe')
        probe_obj = self.printer.lookup_object('probe')

        if probe_obj:
            mcu_probe = probe_obj.mcu_probe
        else:
            mcu_probe = probe.ProbeEndstopWrapper(config)

        # Unregister any pre-existing probe commands first.
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('PROBE', None)
        gcode.register_command('QUERY_PROBE', None)
        gcode.register_command('PROBE_CALIBRATE', None)
        gcode.register_command('PROBE_ACCURACY', None)
        gcode.register_command('Z_OFFSET_APPLY_PROBE', None)

        pins = self.printer.lookup_object('pins')
        if 'probe' in pins.chips:
            pins.chips.pop('probe')
            pins.pin_resolvers.pop('probe')

        probe.PrinterProbe.__init__(self, probe_config, mcu_probe)
        self.settling_sample = config.getboolean('settling_sample', False)
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
    
    def handle_ready(self):
        probe_obj = self.printer.objects.pop('probe', None)
        self.printer.objects['probe'] = self
        del probe_obj

    def _run_settling_probe(self, gcmd):
        gcmd.respond_info("Settling sample (ignored)...")
        speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = self.get_lift_speed(gcmd)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
        pos = self._probe(speed)
        pos[2] += sample_retract_dist
        self._move([None, None, pos[2]], lift_speed)
        return

    def run_probe(self, gcmd):
        if self.settling_sample:
            self._run_settling_probe(gcmd)
        return probe.PrinterProbe.run_probe(self, gcmd)

    def cmd_PROBE_ACCURACY(self, gcmd):
        if self.settling_sample:
            self._run_settling_probe(gcmd)
        return probe.PrinterProbe.cmd_PROBE_ACCURACY(self, gcmd)


def load_config(config):
    return SettlingProbe(config)