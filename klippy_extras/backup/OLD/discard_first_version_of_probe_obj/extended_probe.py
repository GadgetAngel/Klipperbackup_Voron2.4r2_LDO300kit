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
# Discord List:
#    voidtrance#5003
#    yak#0417
#    GadgetAngel#8701
#

import logging
import pins
from mcu import MCU_endstop
from . import manual_probe

HINT_TIMEOUT = """
If the probe did not move far enough to trigger, then
consider reducing the Z axis minimum position so the probe
can travel further (the Z minimum position can be negative).
"""

class ExtendedPrinterProbe:
    def __init__(self, config):
        self.config = config
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.z_endstop = None
        self.mcu_probe = None
        # self.probe is the obj set in handle_connect method; this obj points to the class PrinterProbe in probe.py file
        # self.mcu_probe is the obj set in handle_connect method; this obj points to the class ProbeEndstopWrapper in probe.py file    ###ExtendedProbeEndstopWrapper
        # self.mcu_probe.mcu_endstop is the obj that points to the "Z probe endstop object" or class memeber "mcu_endstop" of class ProbeEndstopWrapper in probe.py file
        self.discard_first = config.getboolean('discard_first', False)
        if config.has_section('probe'):
            pconfig = config.getsection('probe')
            self.speed = pconfig.getfloat('speed', 5.0, above=0.)
            self.lift_speed = pconfig.getfloat('lift_speed', self.speed, above=0.)
            self.x_offset = pconfig.getfloat('x_offset', 0.)
            self.y_offset = pconfig.getfloat('y_offset', 0.)
            self.z_offset = pconfig.getfloat('z_offset')
            self.clearance = (self.z_offset * 2) + 2
            if self.clearance == 0:
                 self.clearance = 20 # defaults to 20mm
            self.probe_calibrate_z = 0.
            self.multi_probe_pending = False
            self.last_state = False
            self.last_z_result = 0.
            self.gcode_move = self.printer.load_object(config, "gcode_move")
            # Infer Z position to move to during a probe
            if config.has_section('stepper_z'):
                zconfig = config.getsection('stepper_z')
                self.z_position = zconfig.getfloat('position_min', 0.,
                                                    note_valid=False)
            else:
                pconfig = config.getsection('printer')
                self.z_position = pconfig.getfloat('minimum_z_position', 0.,
                                                    note_valid=False)
            self.query_endstops = self.printer.load_object(config,
                                                            'query_endstops')            
            # Multi-sample support (for improved accuracy)
            self.sample_count = pconfig.getint('samples', 1, minval=1)
            self.sample_retract_dist = pconfig.getfloat('sample_retract_dist', 2.,
                                                   above=0.)
            atypes = {'median': 'median', 'average': 'average'}
            self.samples_result = pconfig.getchoice('samples_result', atypes,
                                               'average')
            self.samples_tolerance = pconfig.getfloat('samples_tolerance', 0.100,
                                                 minval=0.)
            self.samples_retries = pconfig.getint('samples_tolerance_retries', 0,
                                             minval=0)
            self.pin = pconfig.get('pin')
            self.ppins = self.printer.lookup_object('pins')
            self.stow_on_each_sample = pconfig.getboolean('deactivate_on_each_sample', True)
        else:
            raise self.printer.config_error("ExtendedPrinterProbe.__init__: A probe is needed for %s"
                                                  % (self.config.get_name())) 
        self.printer.register_event_handler("klippy:connect",
                                            self.handle_connect)
        self.printer.register_event_handler("homing:homing_move_begin",
                                            self._handle_homing_move_begin)
        self.printer.register_event_handler("homing:homing_move_end",
                                            self._handle_homing_move_end)
        self.printer.register_event_handler("homing:home_rails_begin",
                                            self._handle_home_rails_begin)
        self.printer.register_event_handler("homing:home_rails_end",
                                            self._handle_home_rails_end)
        self.printer.register_event_handler("gcode:command_error",
                                            self._handle_command_error)
        # Register PROBE/QUERY_PROBE commands
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('EXT_PROBE', self.cmd_EXT_PROBE,
                                    desc=self.cmd_EXT_PROBE_help)
        self.gcode.register_command('EXT_QUERY_PROBE', self.cmd_EXT_QUERY_PROBE,
                                    desc=self.cmd_EXT_QUERY_PROBE_help)
        self.gcode.register_command('EXT_PROBE_CALIBRATE', self.cmd_EXT_PROBE_CALIBRATE,
                                    desc=self.cmd_EXT_PROBE_CALIBRATE_help)
        self.gcode.register_command('EXT_PROBE_ACCURACY', self.cmd_EXT_PROBE_ACCURACY,
                                    desc=self.cmd_EXT_PROBE_ACCURACY_help)
        self.gcode.register_command('EXT_Z_OFFSET_APPLY_PROBE',
                                    self.cmd_EXT_Z_OFFSET_APPLY_PROBE,
                                    desc=self.cmd_EXT_Z_OFFSET_APPLY_PROBE_help)         
    def _handle_homing_move_begin(self, hmove): 
        if self.mcu_probe in hmove.get_mcu_endstops():
            self.mcu_probe.probe_prepare(hmove)
    def _handle_homing_move_end(self, hmove):
        if self.mcu_probe in hmove.get_mcu_endstops():
            self.mcu_probe.probe_finish(hmove)
    def _handle_home_rails_begin(self, homing_state, rails):
        endstops = [es for rail in rails for es, name in rail.get_endstops()]
        if self.mcu_probe in endstops:
            self.multi_probe_begin()
    def _handle_home_rails_end(self, homing_state, rails):
        endstops = [es for rail in rails for es, name in rail.get_endstops()]
        if self.mcu_probe in endstops:
            self.multi_probe_end()
            self.gcode.respond_info("Calling from _handle_home_rails_end:\n ")
    def handle_connect(self):
        # get probing settings
        probe = self.printer.lookup_object('probe', default=None)
        if probe is None:
            raise self.printer.config_error("ExtendedPrinterProbe.handle_connect: A probe is needed for %s"
                                            % (self.config.get_name()))
        self.probe = probe
        self.mcu_probe = probe.mcu_probe
        self._log_config()
    def _handle_command_error(self):
        try:
            self.multi_probe_end()
        except:
            logging.exception("Multi-probe end")
    def _log_config(self):
        logging.debug(
                        "ExtendedPrinterProbe"
                        "\nvariables are as follows:"
                        "\ndiscard_first = %s;"
                        "\nspeed = %s;"
                        "\nlift_speed = %s;"
                        "\nx_offset = %s;"
                        "\ny_offset = %s;"
                        "\nz_offset = %s;"
                        "\nclearance = %s;"
                        "\nprobe_calibrate_z = %s;" 
                        "\nmulti_probe_pending = %s;" 
                        "\nlast_state = %s;"  
                        "\nlast_z_result = %s;" 
                        "\nself.gcode_move = %s;"                         
                        "\nz_position = %s;"
                        "\nsample_count = %s;"
                        "\nsample_retract_dist = %s;"
                        "\nsamples_result = %s;"
                        "\nsamples_tolerance = %s;"
                        "\nsamples_retries = %s;"
                        "\npin = %s;"
                        "\nself.stow_on_each_sample = %s;"
                        "\nself.probe = %s;"
                        "\nself.mcu_probe (probe.mcu_probe) = %s;"
                        "\nprobe.py Class ProbeEndstopWrapper"
                        "\nvariables are as follows:"
                        "\nself.mcu_probe.position_endstop (z_offset) = %s;"
                        "\nself.mcu_probe.stow_on_each_sample = %s;"                        
                        "\nself.mcu_probe.activate_gcode = %s;"
                        "\nself.mcu_probe.deactivate_gcode = %s;"
                        "\nself.mcu_probe.mcu_endstop = %s;"
                        "\nself.mcu_probe.get_mcu = %s;"
                        "\nself.mcu_probe.add_stepper = %s;"
                        "\nself.mcu_probe.get_steppers = %s;"
                        "\nself.mcu_probe.home_start = %s;"
                        "\nself.mcu_probe.home_wait = %s;"
                        "\nself.mcu_probe.query_endstop = %s;"
                    % (
                        self.discard_first,
                        self.speed,
                        self.lift_speed,
                        self.x_offset,
                        self.y_offset,
                        self.z_offset,
                        self.clearance,
                        self.probe_calibrate_z,
                        self.multi_probe_pending,
                        self.last_state,
                        self.last_z_result,
                        self.gcode_move,
                        self.z_position,
                        self.sample_count,
                        self.sample_retract_dist,
                        self.samples_result,
                        self.samples_tolerance,
                        self.samples_retries,
                        self.pin,
                        self.stow_on_each_sample,
                        self.probe,
                        self.mcu_probe,
                        self.mcu_probe.position_endstop,
                        self.mcu_probe.stow_on_each_sample,
                        self.mcu_probe.activate_gcode,
                        self.mcu_probe.deactivate_gcode,
                        self.mcu_probe.mcu_endstop,
                        self.mcu_probe.get_mcu,
                        self.mcu_probe.add_stepper,
                        self.mcu_probe.get_steppers,
                        self.mcu_probe.home_start,   
                        self.mcu_probe.home_wait,
                        self.mcu_probe.query_endstop 
                      ))            
    def multi_probe_begin(self):
        self.mcu_probe.multi_probe_begin()
        self.multi_probe_pending = True
    def multi_probe_end(self):
        if self.multi_probe_pending:
            self.multi_probe_pending = False
            self.mcu_probe.multi_probe_end()
    def get_lift_speed(self, gcmd=None):
        if gcmd is not None:
            return gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)
        return self.lift_speed
    def get_offsets(self):
        return self.x_offset, self.y_offset, self.z_offset 
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
        self.gcode.respond_info("EXT_PROBE: probe at %.3f,%.3f is z=%.6f%s"
                           % (epos[0], epos[1], epos[2], " [discarded]" if discarded else ""))
        return epos[:3]
    def _move(self, coord, speed):
        self.printer.lookup_object('toolhead').manual_move(coord, speed)
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
                        raise gcmd.error("EXT_PROBE: Probe samples exceed samples_tolerance")
                    gcmd.respond_info("EXT_PROBE: Probe samples exceed tolerance. Retrying...")
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
    cmd_EXT_PROBE_help = "EXT_PROBE: Z-height at current XY position"
    def cmd_EXT_PROBE(self, gcmd):
        pos = self.run_probe(gcmd)
        gcmd.respond_info("EXT_PROBE: Result is z=%.6f" % (pos[2],))
        self.last_z_result = pos[2]
        #update the probe object
        self.probe.last_z_result = pos[2]
    cmd_EXT_QUERY_PROBE_help = "Return the status of the z-probe"
    def cmd_EXT_QUERY_PROBE(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        print_time = toolhead.get_last_move_time()
        res = self.mcu_probe.query_endstop(print_time)
        self.last_state = res
        #update the probe object
        self.probe.last_state = res
        gcmd.respond_info("EXT_QUERY_PROBE: probe: %s" % (["open", "TRIGGERED"][not not res],))
    def get_status(self, eventtime):
        return {'last_query': self.last_state,
                'last_z_result': self.last_z_result}
    cmd_EXT_PROBE_ACCURACY_help = "EXT_PROBE: Z-height accuracy at current XY position"
    def cmd_EXT_PROBE_ACCURACY(self, gcmd):
        speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = self.get_lift_speed(gcmd)
        sample_count = gcmd.get_int("SAMPLES", 10, minval=1)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
        discard_first = gcmd.get_int("DISCARD_FIRST", 0)
        toolhead = self.printer.lookup_object('toolhead')
        pos = toolhead.get_position()
        gcmd.respond_info("EXT_PROBE_ACCURACY at X:%.3f Y:%.3f Z:%.3f"
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
            "EXT_PROBE_ACCURACY : probe accuracy results: maximum %.6f, minimum %.6f, range %.6f, "
            "average %.6f, median %.6f, standard deviation %.6f" % (
            max_value, min_value, range_value, avg_value, median, sigma))
    def probe_calibrate_finalize(self, kin_pos):
        if kin_pos is None:
            return
        z_offset = self.probe_calibrate_z - kin_pos[2]
        self.gcode.respond_info(
            "%s: z_offset: %.3f\n"
            "EXT_PROBE_CALIBRATE: The SAVE_CONFIG command will update the printer config file\n"
            "with the above and restart the printer." % ('probe', z_offset))
        configfile = self.printer.lookup_object('configfile')
        configfile.set('probe', 'z_offset', "%.3f" % (z_offset,))
    cmd_EXT_PROBE_CALIBRATE_help = "EXT_PROBE: Calibrate the probe's z_offset"
    def cmd_EXT_PROBE_CALIBRATE(self, gcmd):
        manual_probe.verify_no_manual_probe(self.printer)
        # Perform initial probe
        lift_speed = self.get_lift_speed(gcmd)
        curpos = self.run_probe(gcmd)
        # Move away from the bed
        self.probe_calibrate_z = curpos[2]
        curpos[2] += 5.
        self._move(curpos, lift_speed)
        # Move the nozzle over the probe point
        curpos[0] += self.x_offset
        curpos[1] += self.y_offset
        self._move(curpos, self.speed)
        # Start manual probe
        manual_probe.ManualProbeHelper(self.printer, gcmd,
                                       self.probe_calibrate_finalize)
    def cmd_EXT_Z_OFFSET_APPLY_PROBE(self,gcmd):
        offset = self.gcode_move.get_status()['homing_origin'].z
        configfile = self.printer.lookup_object('configfile')
        if offset == 0:
            self.gcode.respond_info("EXT_Z_OFFSET_APPLY_PROBE: Nothing to do: Z Offset is 0")
        else:
            new_calibrate = self.z_offset - offset
            self.gcode.respond_info(
                "%s: z_offset: %.3f\n"
                "EXT_Z_OFFSET_APPLY_PROBE: The SAVE_CONFIG command will update the printer config file\n"
                "with the above and restart the printer."
                % ('probe', new_calibrate))
            configfile.set('probe', 'z_offset', "%.3f" % (new_calibrate,))
    cmd_EXT_Z_OFFSET_APPLY_PROBE_help = "EXT_PROBE: Adjust the probe's z_offset"

        
def load_config(config):
    return ExtendedPrinterProbe(config)