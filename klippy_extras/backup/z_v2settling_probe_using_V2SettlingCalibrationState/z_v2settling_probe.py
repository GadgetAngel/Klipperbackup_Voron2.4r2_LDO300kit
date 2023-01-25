# Custom Z-Probe object that allow for a single settling probe
# prior to sampling.
#
# Copyright (C) 2023 Mitko Haralanov <voidtrance@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#

import probe
import pins
import z_calibration
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
            
        #figure out a way to determine which type of printer we are running on
        #only call __init__ for z_v2settling_probe extension for the correct type of printer
        atypes = {  'none'       : None,     'cartesian'     : 'cartesian',              'corexy' : 'corexy',
                  'corexz'       : 'corexz', 'hybrid_corexy' : 'hybrid_corexy',   'hybrid_corexz' : 'hybrid_corexz',
                  'rotary_delta' : 'rotary_delta',   'delta' : 'delta',               'deltesian' : 'deltesian',
                  'polar'        : 'polar',          'winch' : 'winch'         }
        kinematics_config = config.getsection('printer')
        kinematics_choice = kinematics_config.getchoice('kinematics', atypes, 'none')
        if kinematics_choice in ['corexy','cartesian','corexz','hybrid_corexy','hybrid_corexz']:
            logging.info("z_v2settling_probe ::INFO:: Printer has the following "
                         "kinematics: %s" % (kinematics_choice))  
        else:
            logging.info("z_v2settling_probe ::ERROR:: Printer has the following "
                         "kinematics:\n    kinematics = %s\n"
                         "This printer is not allowed to use the "
                         "z_v2settling_probe extension (plugin)" % (kinematics_choice))
            raise self.config.error("z_v2settling_probe ::ERROR::  This printer type is "
                                     "not allowed to use %s plugin (extension)"
                                    % (config.get_name()))

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
        
    def cmd_PROBE_ACCURACY(self, gcmd):
    # the probe.PrinterProbe.cmd_PROBE_ACCURACY calls self._probe(speed) not self.run_probe(gcmd)
        if gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            self._run_settling_probe(gcmd)
        return probe.PrinterProbe.cmd_PROBE_ACCURACY(self, gcmd)
        
    
class V2SettlingZCalibrationHelper(z_calibration.ZCalibrationHelper):
    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        z_calibration_config = config.getsection('z_calibration')
        # Unregister any pre-existing z_calibration commands first.
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('CALIBRATE_Z', None)
        self.gcode.register_command('PROBE_Z_ACCURACY', None)
        z_calibration.ZCalibrationHelper.__init__(self, z_calibration_config)
        self.printer.register_event_handler("klippy:ready", self.handle_ready)         
 
    def handle_ready(self):
        self.probe = self.printer.lookup_object('probe')
        self.settling_sample = self.probe.settling_sample
        # This is the hacky bit:
        # The "klippy:ready" event is sent after all configuration has been
        # read and all objects created. So, we are sure that the 'z_calibration'
        # object already exists.
        # So, we can reach into the printer objects and replace the existing 'z_calibration'
        # object with this one.
        z_calibration_obj = self.printer.objects.pop('z_calibration', None)
        self.printer.objects['z_calibration'] = self
        del z_calibration_obj
        
    def move_to_z_endstop(self, gcmd, lift_speed):
        if self.z_homing is None:
            raise gcmd.error("Must home axes first")
        toolhead = self.printer.lookup_object('toolhead')
        pos = toolhead.get_position()
        if pos[2] < self.clearance:
            # no clearance, better to move up
            pos[2] += self.clearance
            self._move(pos, lift_speed)
        # move to z-endstop position
        self._move(list(self.nozzle_site), self.speed)
        
    def cmd_CALIBRATE_Z(self, gcmd):
        if self.z_homing is None:
            raise gcmd.error("Must home axes first")
        site_attr = gcmd.get("BED_POSITION", None)
        if site_attr is not None:
            # set bed site from BED_POSITION parameter
            self.bed_site = self._parse_site("BED_POSITION", site_attr)
        elif self._get_site("bed_xy_position", "probe_bed", True) is not None:
            # set bed site from configuration
            self.bed_site = self._get_site("bed_xy_position", "probe_bed", False)
        else:
            # else get the mesh's relative reference index point
            # a round mesh/bed would not work here so far...
            try:
                mesh = self.printer.lookup_object('bed_mesh', default=None)
                rri = mesh.bmc.relative_reference_index    
                self.bed_site = mesh.bmc.points[rri]
                logging.debug("Z-CALIBRATION probe bed_x=%.3f bed_y=%.3f"
                              % (self.bed_site[0], self.bed_site[1]))
            except:
                raise gcmd.error("Either use the BED_POSITION parameter,"
                                 " configure a bed_xy_position or define"
                                 " a mesh with a relative_reference_index"
                                 " for %s" % (self.config.get_name()))
        self._log_config()
        state = V2SettlingCalibrationState(self, gcmd)
        state.calibrate_z()
        
    def cmd_PROBE_Z_ACCURACY(self, gcmd):
        speed = gcmd.get_float("PROBE_SPEED", self.second_speed, above=0.)
        lift_speed = gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)        
        if gcmd.get_int("SETTLING_SAMPLE", self.settling_sample):
            self.move_to_z_endstop(gcmd, lift_speed)
            gcmd.respond_info("Settling sample (ignored)...") 
            #self._probe() does a probe and a retract
            pos = self._probe(self.z_endstop, self.position_min, speed)  
        return z_calibration.ZCalibrationHelper.cmd_PROBE_Z_ACCURACY(self, gcmd)    
        
class V2SettlingCalibrationState(z_calibration.CalibrationState):

    def __init__(self, helper, gcmd):
        z_calibration.CalibrationState.__init__(self, helper, gcmd)
    
    def _prepare(self, site, check_probe):
        pos = self.toolhead.get_position()
        if pos[2] < self.helper.clearance:
            # no clearance, better to move up
            pos[2] += self.helper.clearance
            self.helper._move(pos, self.helper.lift_speed)
        # move to to probe the correct location (nozzle to endstop, switch body to endstop) 
        self.helper._move(list(site), self.helper.speed)
        if check_probe:
            # check if probe is attached and switch is closed
            time = self.toolhead.get_last_move_time()
            if self.probe.mcu_probe.query_endstop(time):
                raise self.helper.printer.command_error("Probe switch not"
                                                        " closed - Probe not"
                                                        " attached?")                                            
    def _message_first_fast(self):
        self.gcmd.respond_info("Option 'probing_first_fast enabled' so Settling sample (ignored)...")
        try:
            self.gcmd.get_int("SETTLING_SAMPLE")
        except:
            pass
        else:
            self.gcmd.respond_info("Ignoring parameter 'SETTLING_SAMPLE'")    
 
    def _probe_on_site(self, endstop, site, check_probe=False):
        # if first_fast is True than the first sample is already discarded!
        if self.helper.first_fast:
            self._message_first_fast()
        if self.gcmd.get_int("SETTLING_SAMPLE", self.helper.settling_sample):
            # move the probe to the correct area
            self._prepare(site, check_probe)
            if not self.helper.first_fast:
                self.gcmd.respond_info("Settling sample (ignored)...")
                #perform the settling_sample at second_speed
                #self.helper._probe() does a probe and a retract
                pos = self.helper._probe(endstop, self.helper.position_min, self.helper.second_speed)
        return z_calibration.CalibrationState._probe_on_site(self, endstop, site, check_probe)
        
    def calibrate_z(self):
        return z_calibration.CalibrationState.calibrate_z(self)
        
def load_config(config):
    try:
        z_calibration_obj = config.get_printer().lookup_object('z_calibration')
    except:
        logging.info("z_v2settling_probe ::WARNING:: PROBE_Z_ACCURACY"
                     " command will not be available!\n"
                     "CALIBRATE_Z command will not be available!\n"
                     "This printer does not use the Klipper plugin for "
                     "the self calibrating Z offset!")  
        return V2SettlingProbe(config)
    else:
        return V2SettlingProbe(config), V2SettlingZCalibrationHelper(config)
        