# Custom Z-Probe object that allow for a single settling probe
# prior to sampling.
#
# Copyright (C) 2023 Mitko Haralanov <voidtrance@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import probe
import pins
# import z_calibration
import logging

class V2SettlingProbe(probe.PrinterProbe):
    def __init__(self, config):
        self.printer = config.get_printer()
        probe_config = config.getsection('probe')
        probe_obj = self.printer.lookup_object('probe')

        if probe_obj:
            mcu_probe = probe_obj.mcu_probe
        else:
            mcu_probe = probe.ProbeEndstopWrapper(config)
            
        #figure out a way of deteching if this extension
        #is being used on a Voron2 (flying Gantry) type of printer
        #only __init__ settling_probe extension for Voron2 printers
        # if self.printer != None:
            # pass


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
        # This is the hacky bit:
        # The "klippy:ready" event is sent after all configuration has been
        # read and all objects created. So, we are sure that the 'probe'
        # object already exists.
        # So, we can reach into the printer objects and replace the existing 'probe'
        # object with this one.
        probe_obj = self.printer.objects.pop('probe', None)
        self.printer.objects['probe'] = self
        del probe_obj
        
    def _run_settling_probe(self, gcmd):
        gcmd.respond_info("Settling sample (ignored)...")
        speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = self.get_lift_speed(gcmd)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, minval=0.)
        pos = self._probe(speed)
        pos[2] += sample_retract_dist
        self._move(pos, lift_speed)

    def run_probe(self, gcmd):                 
    # The following use self.run_probe : probe.PrinterProbe.cmd_PROBE; probe.PrinterProbe.cmd_PROBE_CALIBRATE;
    # and probe.ProbePointsHelper.start_probe
        if gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            self._run_settling_probe(gcmd)
        return probe.PrinterProbe.run_probe(self, gcmd)
        
    def get_status(self, eventtime):
        return {'last_query': self.last_state,
                'last_z_result': self.last_z_result,
                'settling_sample': self.settling_sample
                }   
        
    def cmd_PROBE_ACCURACY(self, gcmd):
    # the probe.PrinterProbe.cmd_PROBE_ACCURACY calls self._probe(speed) not self.run_probe(gcmd)
        if gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            self._run_settling_probe(gcmd)
        return probe.PrinterProbe.cmd_PROBE_ACCURACY(self, gcmd)
        
def load_config(config):
    return V2SettlingProbe(config)
    
# class V2SettlingZCalibrationHelper(z_calibration.ZCalibrationHelper):
    # def __init__(self, config):
        # logging.info("v2settling_probe ::WARNING:: HELLO JOANN ")
        # z_calibration_config = config.getsection('z_calibration')
        # self.printer = config.get_printer()
        
        # #if [z_calibration] does not exist do not __init__ the z_calibration obj
        # if z_calibration_config:
            # # Unregister any pre-existing z_calibration commands first.
            # gcode = self.printer.lookup_object('gcode')
            # gcode.register_command('CALIBRATE_Z', None)
            # gcode.register_command('PROBE_Z_ACCURACY', None)

            # z_calibration.ZCalibrationHelper.__init__(self, z_calibration_config)
            # self.printer.register_event_handler("klippy:ready", self.handle_ready)
        # #log a warning
        # else:
            # logging.info("v2settling_probe ::WARNING:: PROBE_Z_ACCURACY "
                         # "command will not be available!\n"
                         # "This printer does not use the Klipper plugin for "
                         # "the self calibrating Z offset!\n")        
        
    # def get_status(self, eventtime):
        # return {
                # 'last_query': self.last_state,
                # 'last_z_offset': self.last_z_offset,
                # 'settling_sample': self.settling_sample
                # }
        
    # def handle_ready(self):
        # time = self.printer.lookup_object('toolhead').get_last_move_time()
        # self.probe = self.printer.lookup_object('probe')
        # self.settling_sample = self.probe.get_status(time)['settling_sample']
        # # This is the hacky bit:
        # # The "klippy:ready" event is sent after all configuration has been
        # # read and all objects created. So, we are sure that the 'z_calibration'
        # # object already exists.
        # # So, we can reach into the printer objects and replace the existing 'z_calibration'
        # # object with this one.
        # z_calibration_obj = self.printer.objects.pop('z_calibration', None)
        # self.printer.objects['z_calibration'] = self
        # del z_calibration_obj
                   
    # def cmd_PROBE_Z_ACCURACY(self, gcmd):
        # speed = gcmd.get_float("PROBE_SPEED", self.second_speed, above=0.)
        # lift_speed = gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)        
        # sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             # self.retract_dist, above=0.) 
        # if self.gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            # gcmd.respond_info("Settling sample (ignored)...") 
            # #._probe() does a probe and a retract
            # pos = z_calibration.ZCalibrationHelper._probe(self.z_endstop, self.position_min, speed)  
        # return z_calibration.ZCalibrationHelper.cmd_PROBE_Z_ACCURACY(self, gcmd)        
        
# class V2SettlingCalibrationState(z_calibration.CalibrationState):
    # def __init__(self, helper, gcmd):
        # z_calibration_config = config.getsection('z_calibration')
        # if z_calibration_config:
            # z_calibration.CalibrationState.__init__(self, helper, gcmd)
        # else:
            # logging.info("v2settling_probe ::WARNING:: "
                         # "CALIBRATE_Z command will not be available!\n"
                         # "This printer does not use the Klipper plugin for "
                         # "the self calibrating Z offset!\n")        
    
    # def _prepare(self, endstop, site, check_probe=False):
        # pos = self.toolhead.get_position()
        # if pos[2] < self.helper.clearance:
            # # no clearance, better to move up
            # pos[2] += self.helper.clearance
            # self.helper._move([pos[2]], self.helper.lift_speed)
        # # move to position
        # self.helper._move(list(site), self.helper.speed)
        # if check_probe:
            # # check if probe is attached and switch is closed
            # time = self.toolhead.get_last_move_time()
            # if self.probe.mcu_probe.query_endstop(time):
                # raise self.helper.printer.command_error("Probe switch not"
                                                        # " closed - Probe not"
                                                        # " attached?")
 
    # def _probe_on_site(self, endstop, site, check_probe=False):                                                    
        # if self.gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            # global_first_fast = self.helper.first_fast
            # # move the probe to the correct area
            # self._prepare(endstop, site, check_probe)
            # self.gcmd.respond_info("Settling sample (ignored)...")
            # if self.helper.first_fast:
                # # perform the settling_sample at probing_speed
                # probe_speed = self.helper.probing_speed
            # else:
                # # perform the settling_sample at second_speed
                # probe_speed = self.helper.second_speed
            # #._probe() does a probe and a retract
            # pos = self.helper._probe(endstop, self.helper.position_min, self.helper.second_speed)
        # return z_calibration.CalibrationState._probe_on_site(self, endstop, site, check_probe)
        
# # def load_config(config):
    # # return V2SettlingZCalibrationHelper(config)
    
# def load_config(config):
    # return V2SettlingProbe(config)