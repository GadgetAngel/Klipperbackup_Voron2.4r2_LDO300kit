# Custom Z-Probe object that allow for a single settling probe
# prior to sampling.
#
# Copyright (C) 2023 Mitko Haralanov <voidtrance@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import probe
import pins
# import logging
# import z_calibration

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
        # logging.info("Gcode param: %s" % gcmd.get_int("SETTLING_SAMPLE"))
        # logging.info("Default param: %s" % self.settling_sample)
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
    return SettlingProbe(config)
    
# class SettlingZCalibrationHelper(z_calibration.ZCalibrationHelper):
    # def __init__(self, config):
        # z_calibration_config = config.getsection('z_calibration')
        # self.printer = config.get_printer()
        
        # # Unregister any pre-existing z_calibration commands first.
        # gcode = self.printer.lookup_object('gcode')
        # gcode.register_command('CALIBRATE_Z', None)
        # gcode.register_command('PROBE_Z_ACCURACY', None)

        # z_calibration.ZCalibrationHelper.__init__(self, z_calibration_config)
        # self.printer.register_event_handler("klippy:ready", self.handle_ready)
        # self.state_machine = 0
        
    # def get_status(self, eventtime):
        # return {
                # 'last_query': self.last_state,
                # 'last_z_offset': self.last_z_offset,
                # 'settling_sample': self.settling_sample
                # }
                
    # def _inc_state(self):
        # return self.state_machine += 1
        
    # def _dec_state(self):
        # return self.state_machine -= 1
        
    # def _reset_state(self):
        # return self.state_machine = 0  
        
    # def _state_machine(self):
        # self.state_machine = 0
        
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
        
    # def _probe_on_site(self, endstop, site, check_probe=False):
        # self._inc_state()
        # pos = self.toolhead.get_position()
        # if pos[2] < self.clearance:
            # # no clearance, better to move up
            # self._move([None, None, pos[2] + self.clearance],
                              # self.lift_speed)
        # # move to position
        # self._move(list(site), self.speed)
        # if check_probe:
            # # check if probe is attached and switch is closed
            # time = self.toolhead.get_last_move_time()
            # if self.probe.mcu_probe.query_endstop(time):
                # raise self.helper.printer.command_error("Probe switch not"
                                                        # " closed - Probe not"
                                                        # " attached?")  
        # pos = self._settling_probe(endstop, self.position_min, self.probing_speed) 
        # self._dec_state() 
        # return z_calibration.CalibrationState._probe_on_site(self, endstop, self.position_min, self.probing_speed)
                   
        
    # def cmd_CALIBRATE_Z(self, gcmd):
        # self._inc_state()
        
        # self.start_gcode.run_gcode_from_command()
        # #probe the nozzle (twice the first time)
        # self._probe_on_site(self.z_endstop, self.nozzle_site) 
        # self._reset_state()
        
        # # probe the probe-switch
        # self.switch_gcode.run_gcode_from_command()    
            
        # # # probe the probe-switch
        # # self.helper.switch_gcode.run_gcode_from_command()
        # # # probe the body of the switch
        # # switch_zero = self._probe_on_site(self.z_endstop,
                                          # # self.helper.switch_site,
                                          # # True)        
        # # # probe position on bed
        # # probe_zero = self._probe_on_site(self.probe.mcu_probe,
                                         # # probe_site,
                                         # # True)
        # return z_calibration.ZCalibrationHelper.cmd_CALIBRATE_Z(self, gcmd)
    
    # def cmd_PROBE_Z_ACCURACY(self, gcmd):
        # self._inc_state()
        # speed = gcmd.get_float("PROBE_SPEED", self.second_speed, above=0.)
        # lift_speed = gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)        
        # sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             # self.retract_dist, above=0.) 
        # pos = self._settling_probe(self.z_endstop, self.position_min, speed)  
        # # Retract
        # liftpos = [None, None, pos[2] + sample_retract_dist]
        # self._move(liftpos, lift_speed)  
        # self._reset_state()
        # return z_calibration.ZCalibrationHelper.cmd_PROBE_Z_ACCURACY(self, gcmd)        
        
    # def _settling_probe(self, mcu_endstop, z_position, speed):
        # if self.state_machine == 1:       
            # settling_sample = gcmd.get_int("SETTLING_SAMPLE", self.settling_sample)
            # if settling_sample:
                # gcmd.respond_info("Settling sample (ignored)...") 
                # global_settling_sample = self.settling_sample  
                # self.settling_sample = settling_sample 
                # pos = z_calibration.ZCalibrationHelper._probe(self, mcu_endstop, z_position, speed)   
                # self.settling_sample = global_settling_sample
                # self._inc_state()
        # else:
            
        # return pos 
        
# def load_config(config):
    # return SettlingZCalibrationHelper(config)