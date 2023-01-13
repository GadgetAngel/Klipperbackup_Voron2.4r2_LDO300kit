# Z-Probe support
#
# Copyright (C) 2017-2021  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

# Utilize Python Code in your GCode Macros
#
# Copyright (C) 2022  Michael Carroll <mc999984@gmail.com>
# Some of this code may have been used, sourced, or referenced from Klipper source code
#
# This file may be distributed under the terms of the GNU GPLv3 license.

# Additional contribution are done by the following people:
# 
# URL Resource: https://github.com/voidtrance/voron/blob/master/printer/klipper/extras/probe.py
#
# Discord List:
#    voidtrance#5003
#    yak#0417
#    GadgetAngel#8701

import logging
import pins
from probe import PrinterProbe as ClassPrinterProbe
from . import manual_probe

HINT_TIMEOUT = """
If the probe did not move far enough to trigger, then
consider reducing the Z axis minimum position so the probe
can travel further (the Z minimum position can be negative).
"""
        
class extended_probe_helper(PrinterGCodeMacro, object):     #Dummy `object` required due to the Python 2 requirement for using super()
    def __init__(self, config):
        #super(extended_probe_helper, self).__init__(config)
        self.config = config
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')   
        self.Log = Logger(config)
        discard_first_config = config.getboolean("discard_first", False)   # add discard_first config from [extended_probe] section
        #self.discard_first_config = discard_first_config
        self.discard_first_config = False
        

############################################################
#
# Extend the parent class PrinterProbe class with this class
#
class PrinterProbe(ClassPrinterProbe, object):                       #Dummy `object` required due to the Python 2 requirement for using super()
  def __init__(self, config, mcu_probe):
    super(PrinterProbe, self).__init__(config, mcu_probe)
    self.discard_first = self.discard_first_config                    #grab discard_first from extended_probe_helper
    
  def _probe(self, speed, discarded=False):
    toolhead = self.printer.lookup_object('toolhead')
    curtime = self.printer.get_reactor().monotonic()
    if 'z' not in toolhead.get_status(curtime)['homed_axes']:
        raise self.printer.command_error("Must home before probe")
    phoming = self.printer.lookup_object('homing')
    pos = toolhead.get_position()
    pos[2] = self.z_position
    try:
        epos = phoming.probing_move(self.mcu_probe, pos, speed)
    except self.printer.command_error as e:
        reason = str(e)
        if "Timeout during endstop homing" in reason:
            reason += HINT_TIMEOUT
        raise self.printer.command_error(reason)
    self.gcode.respond_info("probe at %.3f,%.3f is z=%.6f%s"
                           % (epos[0], epos[1], epos[2], " [discarded]" if discarded else ""))
    return epos[:3]
    def _calc_mean(self, positions):
        count = float(len(positions))
        return [sum([pos[i] for pos in positions]) / count
                for i in range(3)]
    def _calc_median(self, positions):
        z_sorted = sorted(positions, key=(lambda p: p[2]))
        middle = len(positions) // 2
        if (len(positions) & 1) == 1:
            # odd number of samples
            return z_sorted[middle]
        # even number of samples
        return self._calc_mean(z_sorted[middle-1:middle+1])
    def run_probe(self, gcmd):
        speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = self.get_lift_speed(gcmd)
        sample_count = gcmd.get_int("SAMPLES", self.sample_count, minval=1)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
        samples_tolerance = gcmd.get_float("SAMPLES_TOLERANCE",
                                           self.samples_tolerance, minval=0.)
        samples_retries = gcmd.get_int("SAMPLES_TOLERANCE_RETRIES",
                                       self.samples_retries, minval=0)
        samples_result = gcmd.get("SAMPLES_RESULT", self.samples_result)
        must_notify_multi_probe = not self.multi_probe_pending
        if must_notify_multi_probe:
            self.multi_probe_begin()
        probexy = self.printer.lookup_object('toolhead').get_position()[:2]
        retries = 0
        positions = []
        first_sample_discarded = False
        while len(positions) < sample_count:
            # Discard first reading if we need to
            if self.discard_first and not first_sample_discarded:
                # Take first sample and ignore it
                first_sample_discarded = True
                pos = self._probe(speed, first_sample_discarded)
            else:
                # Probe position
                pos = self._probe(speed)
                positions.append(pos)
                # Check samples tolerance
                z_positions = [p[2] for p in positions]
                if max(z_positions) - min(z_positions) > samples_tolerance:
                    if retries >= samples_retries:
                        raise gcmd.error("Probe samples exceed samples_tolerance")
                    gcmd.respond_info("Probe samples exceed tolerance. Retrying...")
                    retries += 1
                    positions = []

            # Retract
            if len(positions) < sample_count:
                self._move(probexy + [pos[2] + sample_retract_dist], lift_speed)
        if must_notify_multi_probe:
            self.multi_probe_end()
        # Calculate and return result
        if samples_result == 'median':
            return self._calc_median(positions)
        return self._calc_mean(positions)
    cmd_PROBE_help = "Probe Z-height at current XY position" 
    def cmd_PROBE_ACCURACY(self, gcmd):
        speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = self.get_lift_speed(gcmd)
        sample_count = gcmd.get_int("SAMPLES", 10, minval=1)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
        discard_first = gcmd.get_int("DISCARD_FIRST", 0)
        toolhead = self.printer.lookup_object('toolhead')
        pos = toolhead.get_position()
        gcmd.respond_info("PROBE_ACCURACY at X:%.3f Y:%.3f Z:%.3f"
                          " (samples=%d retract=%.3f"
                          " speed=%.1f lift_speed=%.1f)\n"
                          % (pos[0], pos[1], pos[2],
                             sample_count, sample_retract_dist,
                             speed, lift_speed))
        # Probe bed sample_count times
        self.multi_probe_begin()
        positions = []
        first_sample_discarded = False
        while len(positions) < sample_count:
            # Discard first reading if we're asked to
            if discard_first and not first_sample_discarded:
                # Probe position
                first_sample_discarded = True
                pos = self._probe(speed, first_sample_discarded)
            else:
                # Probe position
                pos = self._probe(speed)
                positions.append(pos)
            # Retract
            liftpos = [None, None, pos[2] + sample_retract_dist]
            self._move(liftpos, lift_speed)
        self.multi_probe_end()
        # Calculate maximum, minimum and average values
        max_value = max([p[2] for p in positions])
        min_value = min([p[2] for p in positions])
        range_value = max_value - min_value
        avg_value = self._calc_mean(positions)[2]
        median = self._calc_median(positions)[2]
        # calculate the standard deviation
        deviation_sum = 0
        for i in range(len(positions)):
            deviation_sum += pow(positions[i][2] - avg_value, 2.)
        sigma = (deviation_sum / len(positions)) ** 0.5
        # Show information
        gcmd.respond_info(
            "probe accuracy results: maximum %.6f, minimum %.6f, range %.6f, "
            "average %.6f, median %.6f, standard deviation %.6f" % (
            max_value, min_value, range_value, avg_value, median, sigma))    

def load_config(config):
  return PrinterProbe(config, extended_probe_helper(config), ClassPrinterProbe.ProbeEndstopWrapper(config))