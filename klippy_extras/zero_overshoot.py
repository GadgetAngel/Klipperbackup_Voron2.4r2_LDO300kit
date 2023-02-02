# Tracking of PWM controlled heaters and their temperature control
#
# Copyright (C) 2016-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import configparser
from .heaters import (
     ControlPID as ControlPID,
     Heater as Heater,
     PrinterHeaters as PrinterHeaters
)
message_ready = "Printer is ready"

# class ZeroOvershootHeater(Heater):
    # def __init__(self, config, sensor):
        # # self.printer = config.get_printer()
        # # name = config.get_name()
        # # heater_bed_config = config.getsection('heater_bed')
        # # extruder_config = config.getsection('extruder')
        # # if ((name == 'heater_bed') or (name == 'extruder')):
            # # # self.name = config.get_name().split()[-1]
        
            # # # Unregister any pre-existing probe commands first.
            # # gcode = self.printer.lookup_object('gcode') 
            # # # remove mux_command
            # # prev = gcode.mux_commands.get('SET_HEATER_TEMPERATURE')
            # # key, values = prev
            # # if ((key == "HEATER") and (name in values)):
                # # values[name] = None
            # # # gcode.mux_commands.pop('SET_HEATER_TEMPERATURE')          
            # # #def register_mux_command(cmd, key, value, func, desc=None)  
            # # gcode.register_command('SET_HEATER_TEMPERATURE', None)            
            # # # gcode.register_mux_command("SET_HEATER_TEMPERATURE", "HEATER",
                                       # # # self.name, self.cmd_SET_HEATER_TEMPERATURE,
                                       # # # desc=self.cmd_SET_HEATER_TEMPERATURE_help)  
                                   
            # # # Remove the already-registered 'heater_pin' pin. It will be
            # # # replaced by this instance.
            # # pins = self.printer.lookup_object('pins')
            # # pins.chips.pop(name)
            # # pins.pin_resolvers.pop(name)
                
            # Heater.__init__(self, config, sensor)
            # # setup own setting
            # logging.info("ZeroOvershootHeater on behalf of zero_overshoot_heater_bed ::INFO:: I am past the Heater.__init__(self, config, sensor) call!") 

# # def load_config_prefix(config):
    # # heater_name = config.get_name().split()[-1]
    # # printer = config.get_printer()
    # # pheaters = printer.lookup_object('heaters')
    # # heater = pheaters.lookup_heater(heater_name)
    # # return NoOvershootControlPID(heater, config)
    
    
######################################################################
# Proportional Integral Derivative (PID) control algo
######################################################################

######################################################################
# ZERO_OVERSHOOT_HEATER_BED extension inherits from heaters.ControlPID
######################################################################

PID_PARAM_BASE = 255.000

# class ZeroOvershootControlPID2(ControlPID):
    # def __init__(self, heater, config):
        # name = config.get_name().split()[-1]
        # hconfig = config.getsection(name)
        # printer = config.get_printer()
        # pheaters = printer.lookup_object('heaters')
        # heater_dict = pheaters.get_all_heaters()
        # logging.info("ZeroOvershootControlPID on behalf of zero_overshoot_heater_bed ::INFO:: all_heaters = %s" % (heater_dict)) 
        # if name == 'extruder':
            # if printer.get_state_message()[0] == message_ready:
                # heater = pheaters.lookup_heater(name)
        # else:
            # heater = pheaters.lookup_heater(name)
        
        # # ControlPID.__init__(self, heater, heater_bed_config)
        # ControlPID.__init__(self, heater, hconfig)
        # # setup own setting
        # logging.info("ZeroOvershootControlPID on behalf of zero_overshoot_heater_bed ::INFO:: I am past the ControlPID.__init__(self, heater, config) call!!") 
        
        # self.heater = heater
        # const_one_third = 1./3.
        # const_88 = 88./100.
        
        # logging.info("zero_overshoot_heater_bed ::INFO:: self.heater.name = %s" % (self.heater.name)) 
        # logging.info("zero_overshoot_heater_bed ::INFO:: heater.name = %s; printer.get_state_message()[0] = %s" % (self.heater.name, printer.get_state_message()[0])) 
        # if ((self.heater.name == 'extruder' and printer.get_state_message()[0] == message_ready) or (self.heater.name == 'heater_bed')):
            # logging.info("zero_overshoot_heater_bed ::INFO:: heater.name = %s; hconfig = %s" % (self.heater.name, hconfig)) 
            # self.zero_overshoot = hconfig.getboolean('zero_overshoot')
            # self.Kp_multiplier = hconfig.getfloat('Kp_multiplier')
            # self.Ki_multiplier = hconfig.getfloat('Ki_multiplier')
            # self.Kd_multiplier = hconfig.getfloat('Kd_multiplier')
            # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_heater_bed %s]: zero_overshoot = %s" % (self.heater.name, self.zero_overshoot)) 
        
        # if (((self.heater.name == 'extruder' and printer.get_state_message()[0] == message_ready) or (self.heater.name == 'heater_bed')) and self.zero_overshoot == True):
            # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_heater_bed %s]: Kp_multiplier = %s" % (self.heater.name, self.Kp_multiplier)) 
            # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_heater_bed %s]: Ki_multiplier = %s" % (self.heater.name, self.Ki_multiplier)) 
            # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_heater_bed %s]: Kd_multiplier = %s" % (self.heater.name, self.Kd_multiplier)) 
            # if self.Kp_multiplier is None:
                # self.Kp_multiplier = const_one_third
            # if self.Ki_multiplier is None:
                # self.Ki_multiplier = const_one_third
            # if self.Kd_multiplier is None:
                # self.Kd_multiplier = const_88
            # myKp = self.Kp * PID_PARAM_BASE                                          
            # myKi = self.Ki * PID_PARAM_BASE                                          
            # myKd = self.Kd * PID_PARAM_BASE                                         
            # myKp = round((myKp * self.Kp_multiplier),3)       
            # myKi = round((myKi * self.Ki_multiplier),3)       
            # myKd = round((myKd * self.Kd_multiplier),3)       
            # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kp = %3.3f" % (self.heater.name, myKp)) 
            # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Ki = %3.3f" % (self.heater.name, myKi)) 
            # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kd = %3.3f" % (self.heater.name, myKd)) 
            # self.Kp = myKp / PID_PARAM_BASE                                          
            # self.Ki = myKi / PID_PARAM_BASE                                          
            # self.Kd = myKd / PID_PARAM_BASE                                          
            # self.temp_integ_max = 0.
            # if self.Ki:
                # self.temp_integ_max = self.heater_max_power / self.Ki

# class ZeroOvershootExtruderControlPID(ControlPID):
    # def __init__(self, heater, config):
        # # heater_bed_config = config.getsection('heater_bed')
        # # ControlPID.__init__(self, heater, heater_bed_config)
        # self.printer = config.get_printer()
        # ControlPID.__init__(self, heater, config)
        # # setup own setting
        # logging.info("ZeroOvershootHeaterBedControlPID on behalf of zero_overshoot_heater_bed ::INFO:: I am past the ControlPID.__init__(self, heater, config) call!!") 
        # heater_bed_config = config.getsection('heater_bed')
        # extruder_config = config.getsection('extruder')
        
        # self.heater = heater
        # const_one_third = 1./3.
        # const_88 = 88./100.
        
        # pheaters = self.printer.lookup_object('heaters')
        # heater_bed_obj = pheaters.lookup_heater('heater_bed')
        
        # if config.get_name() == 'heater_bed' or config.get_name() == 'extruder':
            # self.zero_overshoot = config.getboolean('zero_overshoot', False)
            # self.Kp_multiplier = config.getfloat('Kp_multiplier',None)
            # self.Ki_multiplier = config.getfloat('Ki_multiplier',None)
            # self.Kd_multiplier = config.getfloat('Kd_multiplier',None)
        
        
        # # if self.heater.name == heater_bed_obj.name:
            # # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: zero_overshoot = %s" % (self.heater.name, self.zero_overshoot)) 
        
        # # # heater_bed section
        # # if ((self.zero_overshoot == True) and (self.heater.name == heater_bed_obj.name)):
            # # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Kp_multiplier = %s" % (self.heater.name, self.Kp_multiplier)) 
            # # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Ki_multiplier = %s" % (self.heater.name, self.Ki_multiplier)) 
            # # logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Kd_multiplier = %s" % (self.heater.name, self.Kd_multiplier)) 
            # # if self.Kp_multiplier is None:
                # # self.Kp_multiplier = const_one_third
            # # if self.Ki_multiplier is None:
                # # self.Ki_multiplier = const_one_third
            # # if self.Kd_multiplier is None:
                # # self.Kd_multiplier = const_88
            # # myKp = self.Kp * PID_PARAM_BASE                                          
            # # myKi = self.Ki * PID_PARAM_BASE                                          
            # # myKd = self.Kd * PID_PARAM_BASE                                         
            # # myKp = round((myKp * self.Kp_multiplier),3)       
            # # myKi = round((myKi * self.Ki_multiplier),3)       
            # # myKd = round((myKd * self.Kd_multiplier),3)       
            # # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kp = %3.3f" % (self.heater.name, myKp)) 
            # # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Ki = %3.3f" % (self.heater.name, myKi)) 
            # # logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kd = %3.3f" % (self.heater.name, myKd)) 
            # # self.Kp = myKp / PID_PARAM_BASE                                          
            # # self.Ki = myKi / PID_PARAM_BASE                                          
            # # self.Kd = myKd / PID_PARAM_BASE                                          
            # # self.temp_integ_max = 0.
            # # if self.Ki:
                # # self.temp_integ_max = self.heater_max_power / self.Ki

# def load_config_prefix(config):
    # printer = config.get_printer()
    # pheaters = printer.lookup_object('heaters')
    # heater_dict = pheaters.get_all_heaters()
    # logging.info("zero_overshoot_heater_bed ::INFO:: all_heaters = %s" % (heater_dict)) 
    # heater = pheaters.lookup_heater('heater_bed')
    # return ZeroOvershootExtruderControlPID(heater, config)
    
######################################################################
# Sensor and heater lookup
######################################################################
   
# class ZeroOvershootPrinterHeaters2(PrinterHeaters):
    # def __init__(self, config):
        # self.printer = config.get_printer()
    
        # # Unregister any pre-existing probe commands first.
        # gcode = self.printer.lookup_object('gcode')
        # gcode.register_command('TURN_OFF_HEATERS', None)
        # gcode.register_command('M105', None)
        # gcode.register_command('TEMPERATURE_WAIT', None)
        
        # PrinterHeaters.__init__(self, config)
        # # setup own setting
        # self.config = config
        # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO:: I am past the PrinterHeaters.__init__(self, config)!!") 

        
    # def _handle_ready(self):
        # self.has_started = True
        # pheaters = self.printer.lookup_object('heaters')
        # heater_dict = pheaters.get_all_heaters()
        # logging.info("ZeroOvershootPrinterHeaters on behave of zero_overshoot_heater_bed ::INFO:: "
                                                # "all_heaters = %s" % (heater_dict)) 
        # extruder_obj = self.printer.lookup_object('extruder', None)
        # logging.info("ZeroOvershootPrinterHeaters on behave of zero_overshoot_heater_bed ::INFO:: "
                                                # "self.printer.lookup_object('extruder', None) = %s" 
                                                # % (extruder_obj))
        # #setup
        # heater_bed_config = self.config.getsection('heater_bed')
        # hbheater = pheaters.lookup_heater('heater_bed')        
        # extruder_config = self.config.getsection('extruder')
        # eheater = pheaters.lookup_heater('extruder')
        # state_flag = self.printer.get_state_message()[0] == message_ready
        # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO::  state_flag = %s" % (state_flag)) 
        # if state_flag: 
            # hb_ZeroOvershootControlPID = ZeroOvershootControlPID(hbheater,heater_bed_config)
            # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO:: hb_ZeroOvershootControlPID = %s" % (hb_ZeroOvershootControlPID)) 
            # e_ZeroOvershootControlPID = ZeroOvershootControlPID(eheater,extruder_config)
            # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO:: e_ZeroOvershootControlPID = %s" % (e_ZeroOvershootControlPID)) 

# def load_config(config):
    # return ZeroOvershootPrinterHeaters(config)
    
# def load_config_prefix(config):
    # name = config.get_name().split()[-1]
    # printer = config.get_printer()
    # pheaters = printer.lookup_object('heaters')
    # heater_dict = pheaters.get_all_heaters()
    # logging.info("ZeroOvershootControlPID on behalf of zero_overshoot_heater_bed ::INFO:: all_heaters = %s" % (heater_dict)) 
    # if name == 'extruder':
        # if printer.get_state_message()[0] == message_ready:
            # heater = pheaters.lookup_heater(name)
    # else:
        # heater = pheaters.lookup_heater(name)
        # return ZeroOvershootControlPID(heater, config)
        
        
class ZeroOvershootControlPID:
    def __init__(self, heater, config):
        self.heater = heater
        self.heater_max_power = heater.get_max_power()
        logging.info("ZeroOvershootControlPID.__init__ on behalf of zero_overshoot ::INFO:: heater.name = %s" % (heater.name)) 
        logging.info("ZeroOvershootControlPID.__init__ on behalf of zero_overshoot ::INFO:: config = %s" % (config)) 
        self.Kp = config.getfloat('pid_Kp')
        self.Kp_config = self.Kp        
        logging.info("ZeroOvershootControlPID.__init__ on behalf of zero_overshoot ::INFO:: self.Kp_config = %s" % (self.Kp_config)) 
        self.Kp = self.Kp / PID_PARAM_BASE
        self.Ki = config.getfloat('pid_Ki')
        self.Ki_config = self.Ki  
        logging.info("ZeroOvershootControlPID.__init__ on behalf of zero_overshoot ::INFO:: self.Ki_config = %s" % (self.Ki_config))         
        self.Ki = self.Ki / PID_PARAM_BASE
        self.Kd = config.getfloat('pid_Kd')
        self.Kd_config = self.Kd
        logging.info("ZeroOvershootControlPID.__init__ on behalf of zero_overshoot ::INFO:: self.Kd_config = %s" % (self.Kd_config))  
        self.Kd = self.Kd / PID_PARAM_BASE
        
        self.min_deriv_time = heater.get_smooth_time()
        self.temp_integ_max = 0.
        if self.Ki:
            self.temp_integ_max = self.heater_max_power / self.Ki
        self.prev_temp = AMBIENT_TEMP
        self.prev_temp_time = 0.
        self.prev_temp_deriv = 0.
        self.prev_temp_integ = 0.
    def temperature_update(self, read_time, temp, target_temp):
        time_diff = read_time - self.prev_temp_time
        # Calculate change of temperature
        temp_diff = temp - self.prev_temp
        if time_diff >= self.min_deriv_time:
            temp_deriv = temp_diff / time_diff
        else:
            temp_deriv = (self.prev_temp_deriv * (self.min_deriv_time-time_diff)
                          + temp_diff) / self.min_deriv_time
        # Calculate accumulated temperature "error"
        temp_err = target_temp - temp
        temp_integ = self.prev_temp_integ + temp_err * time_diff
        temp_integ = max(0., min(self.temp_integ_max, temp_integ))
        # Calculate output
        co = self.Kp*temp_err + self.Ki*temp_integ - self.Kd*temp_deriv
        #logging.debug("pid: %f@%.3f -> diff=%f deriv=%f err=%f integ=%f co=%d",
        #    temp, read_time, temp_diff, temp_deriv, temp_err, temp_integ, co)
        bounded_co = max(0., min(self.heater_max_power, co))
        self.heater.set_pwm(read_time, bounded_co)
        # Store state for next measurement
        self.prev_temp = temp
        self.prev_temp_time = read_time
        self.prev_temp_deriv = temp_deriv
        if co == bounded_co:
            self.prev_temp_integ = temp_integ
    def get_Kvalues(self):
        return self.Kp, self.Ki, self.Kd
    def get_Kvalues_config(self):
        return self.Kp_config, self.Ki_config, self.Kd_config
    def check_busy(self, eventtime, smoothed_temp, target_temp):
        temp_diff = target_temp - smoothed_temp
        return (abs(temp_diff) > PID_SETTLE_DELTA
                or abs(self.prev_temp_deriv) > PID_SETTLE_SLOPE)
        
        
class ZeroOvershoot:
    def __init__(self, config):
        if len(config.get_name().split()) > 2:
            raise config.error(
                    "Name of section '%s' contains illegal whitespace"
                    % (config.get_name()))
        self.name = config.get_name().split()[1]
        if not self.name in ['extruder','heater_bed']:
            raise configparser.Error(
                "Invalid name of '%s' name zero_overshoot section" % (self.name))    
        self.alias = name.upper()
        self.config = config
        self.printer = printer = config.get_printer()
        self.toolhead = helper.printer.lookup_object('toolhead')
        zero_overshoot = printer.load_object(config, 'zero_overshoot')
        #= config.get("rename_existing", None)
        self.zero_overshoot = config.getboolean('zero_overshoot', False)
        self.Kp_multiplier = config.getfloat('Kp_multiplier', None)
        self.Ki_multiplier = config.getfloat('Ki_multiplier', None)
        self.Kd_multiplier = config.getfloat('Kd_multiplier', None)
        # let Log file know this extension is active
        logging.info("zero_overshoot ::INFO:: Printer has the following additional setting for [zero_overshoot %s]: zero_overshoot = %s" % (self.name, self.zero_overshoot)) 
        logging.info("zero_overshoot ::INFO:: Printer has the following additional setting for [zero_overshoot %s]: Kp_multiplier = %s" % (self.name, self.Kp_multiplier)) 
        logging.info("zero_overshoot ::INFO:: Printer has the following additional setting for [zero_overshoot %s]: Ki_multiplier = %s" % (self.name, self.Ki_multiplier)) 
        logging.info("zero_overshoot ::INFO:: Printer has the following additional setting for [zero_overshoot %s]: Kd_multiplier = %s" % (self.name, self.Kd_multiplier)) 
        
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
        
        # Register commands
        gcode = printer.lookup_object('gcode')
        gcode.register_command('ZERO_OVERSHOOT', self.cmd_ZERO_OVERSHOOT,
                               desc=self.cmd_ZERO_OVERSHOOT_help)
                               
    def handle_ready(self):
        self.state_flag = self.printer.get_state_message()[0] == message_ready
        pheaters = self.printer.lookup_object('heaters')
        heater_dict = pheaters.get_all_heaters()
        self.heater_bed_config = self.config.getsection('heater_bed')
        self.extruder_config = self.config.getsection('extruder')
        logging.info("ZeroOvershoot.handle_ready on behalf of zero_overshoot ::INFO:: self.heater_bed_config = %s" % (self.heater_bed_config)) 
        logging.info("ZeroOvershoot.handle_ready on behalf of zero_overshoot ::INFO:: self.extruder_config = %s" % (self.extruder_config)) 
        logging.info("ZeroOvershoot.handle_ready ::INFO:: all_heaters = %s" % (heater_dict)) 
        extruder_obj = self.printer.lookup_object('extruder', None)
        logging.info("ZeroOvershoot.handle_ready ::INFO:: self.printer.lookup_object('extruder', None) = %s" % (extruder_obj))
        #setup
        # heater_bed_config = self.config.getsection('heater_bed')
        # hbheater = pheaters.lookup_heater('heater_bed')        
        # extruder_config = self.config.getsection('extruder')
        # eheater = pheaters.lookup_heater('extruder')
        logging.info("ZeroOvershoot ::INFO::  state_flag = %s" % (state_flag)) 
        # if state_flag: 
            # hb_ZeroOvershootControlPID = ZeroOvershootControlPID(hbheater,heater_bed_config)
            # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO:: hb_ZeroOvershootControlPID = %s" % (hb_ZeroOvershootControlPID)) 
            # e_ZeroOvershootControlPID = ZeroOvershootControlPID(eheater,extruder_config)
            # logging.info("ZeroOvershootPrinterHeaters on behalf of zero_overshoot_heater_bed ::INFO:: e_ZeroOvershootControlPID = %s" % (e_ZeroOvershootControlPID)) 
            
    cmd_ZERO_OVERSHOOT_help = "Update PID value in config file to reduce overshoot"
        #ZERO_OVERSHOOT HEATER=heater_bed 
        #ZERO_OVERSHOOT HEATER=extruder
    def cmd_ZERO_OVERSHOOT(self, gcmd):
        heater_name = gcmd.get('HEATER')
        # write_file = gcmd.get_int('WRITE_FILE', 0)
        pheaters = self.printer.lookup_object('heaters')
        try:
            heater = pheaters.lookup_heater(heater_name)
        except self.printer.config_error as e:
            raise gcmd.error(str(e))
        self.printer.lookup_object('toolhead').get_last_move_time()
        if heater_name == 'extruder':
            control_algo = ZeroOvershootControlPID(heater, self.extruder_config)
        elif heater_name == 'heater_bed':
            control_algo = ZeroOvershootControlPID(heater, self.heater_bed_config)
        else:
            raise gcmd.error("ZERO_OVERSHOOT command does not support %s heater." % (heater_name))
        old_control = heater.set_control(control_algo)
        time = self.toolhead.get_last_move_time()
        if heater.get_temp(time) <= 40:
            try:
                pheaters.set_temperature(heater, 40, False)
            except self.printer.command_error as e:
                heater.set_control(old_control)
                raise
            else:
                pheaters.set_temperature(heater, 0, False)
        else:
            raise gcmd.error("ZERO_OVERSHOOT can not be run while the %s temp is above 40 degree C" % (heater_name))
        # heater.set_control(old_control)
        # if write_file:
            # control_algo.write_file('/tmp/heattest.txt')
        # if control_algo.check_busy(0., 0., 0.):
            # raise gcmd.error("pid_calibrate interrupted")
        # Log and report results
        self.Kp, self.Ki, self.Kd = control_algo.get_Kvalues()
        self.Kp_config, self.Ki_config, self.Kd_config = control_algo.get_Kvalues_config()
        Kp, Ki, Kd = self.final_calc(heater_name)
        logging.info("zero_overshot: %s: pid_Kp=%f pid_Ki=%f pid_Kd=%f", heater_name, Kp, Ki, Kd)
        gcmd.respond_info(
            "Zero Overshoot Calulated PID parameters: pid_Kp=%.3f pid_Ki=%.3f pid_Kd=%.3f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer." % (Kp, Ki, Kd))
        # Store results for SAVE_CONFIG
        configfile = self.printer.lookup_object('configfile')
        configfile.set(heater_name, 'control', 'pid')
        configfile.set(heater_name, 'pid_Kp', "%.3f" % (Kp,))
        configfile.set(heater_name, 'pid_Ki', "%.3f" % (Ki,))
        configfile.set(heater_name, 'pid_Kd', "%.3f" % (Kd,))
        
    def final_calc(self, heater_name):
        const_one_third = 1./3.
        const_88 = 88./100. 
        if self.zero_overshoot == False:
            return self.Kp_config, self.Ki_config, self.Kd_config
        if self.Kp_multiplier is None:
            self.Kp_multiplier = const_one_third
        if self.Ki_multiplier is None:
            self.Ki_multiplier = const_one_third
        if self.Kd_multiplier is None:
            self.Kd_multiplier = const_88        
        # myKp = self.Kp * PID_PARAM_BASE                                          
        # myKi = self.Ki * PID_PARAM_BASE                                          
        # myKd = self.Kd * PID_PARAM_BASE                                         
        # myKp = round((myKp * self.Kp_multiplier),3)       
        # myKi = round((myKi * self.Ki_multiplier),3)       
        # myKd = round((myKd * self.Kd_multiplier),3)   
        myKp = round((self.Kp_config * self.Kp_multiplier),3)       
        myKi = round((self.Ki_config * self.Ki_multiplier),3)       
        myKd = round((self.Kd_config * self.Kd_multiplier),3)             
        logging.info("zero_overshoot ::INFO:: [%s] zero_overshoot value: pid_Kp = %3.3f" % (heater_name, myKp)) 
        logging.info("zero_overshoot ::INFO:: [%s] zero_overshoot value: pid_Ki = %3.3f" % (heater_name, myKi)) 
        logging.info("zero_overshoot ::INFO:: [%s] zero_overshoot value: pid_Kd = %3.3f" % (heater_name, myKd)) 
        return myKp, myKi, myKd
            
def load_config(config):
    return ZeroOvershoot(config)
        
# def load_config_prefix(config):
    # name = config.get_name().split()[-1]
    # printer = config.get_printer()
    # pheaters = printer.lookup_object('heaters')
    # heater_dict = pheaters.get_all_heaters()
    # logging.info("ZeroOvershootControlPID on behalf of zero_overshoot_heater_bed ::INFO:: all_heaters = %s" % (heater_dict)) 
    # if name == 'extruder':
        # if printer.get_state_message()[0] == message_ready:
            # heater = pheaters.lookup_heater(name)
    # else:
        # heater = pheaters.lookup_heater(name)
        # return ZeroOvershootControlPID(heater, config)