# Tracking of PWM controlled heaters and their temperature control
#
# Copyright (C) 2016-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from .heaters import (
     ControlPID as ControlPID_OBJ,
     Heater as Heater_OBJ
)
    
######################################################################
# ZERO_OVERSHOOT_HEATER_BED extension inherits from heaters.ControlPID
######################################################################

PID_PARAM_BASE = 255.000

class ZeroOvershootHeaterBedControlPID(ControlPID_OBJ):
    def __init__(self, heater, config):
        heater_bed_config = config.getsection('heater_bed')
        ControlPID_OBJ.__init__(self, heater, heater_bed_config)
        self.printer = config.get_printer()

        self.heater = heater
        const_one_third = 1./3.
        const_88 = 88./100.
        
        pheaters = self.printer.lookup_object('heaters')
        heater_bed_obj = pheaters.lookup_heater('heater_bed')
        
        self.zero_overshoot = config.getboolean('zero_overshoot', False)
        self.Kp_multiplier = config.getfloat('Kp_multiplier',None)
        self.Ki_multiplier = config.getfloat('Ki_multiplier',None)
        self.Kd_multiplier = config.getfloat('Kd_multiplier',None)
        
        
        if self.heater.name == heater_bed_obj.name:
            logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: zero_overshoot = %s" % (self.heater.name, self.zero_overshoot)) 
        
        # heater_bed section
        if ((self.zero_overshoot == True) and (self.heater.name == heater_bed_obj.name)):
            logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Kp_multiplier = %s" % (self.heater.name, self.Kp_multiplier)) 
            logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Ki_multiplier = %s" % (self.heater.name, self.Ki_multiplier)) 
            logging.info("zero_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [zero_overshoot_%s]: Kd_multiplier = %s" % (self.heater.name, self.Kd_multiplier)) 
            if self.Kp_multiplier is None:
                self.Kp_multiplier = const_one_third
            if self.Ki_multiplier is None:
                self.Ki_multiplier = const_one_third
            if self.Kd_multiplier is None:
                self.Kd_multiplier = const_88
            myKp = self.Kp * PID_PARAM_BASE                                          
            myKi = self.Ki * PID_PARAM_BASE                                          
            myKd = self.Kd * PID_PARAM_BASE                                         
            myKp = round((myKp * self.Kp_multiplier),3)       
            myKi = round((myKi * self.Ki_multiplier),3)       
            myKd = round((myKd * self.Kd_multiplier),3)       
            logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kp = %3.3f" % (self.heater.name, myKp)) 
            logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Ki = %3.3f" % (self.heater.name, myKi)) 
            logging.info("zero_overshoot_heater_bed ::INFO:: [%s] zero_overshoot_heater_bed value: pid_Kd = %3.3f" % (self.heater.name, myKd)) 
            self.Kp = myKp / PID_PARAM_BASE                                          
            self.Ki = myKi / PID_PARAM_BASE                                          
            self.Kd = myKd / PID_PARAM_BASE                                          
            self.temp_integ_max = 0.
            if self.Ki:
                self.temp_integ_max = self.heater_max_power / self.Ki
                
def load_config(config):
    printer = config.get_printer()
    pheaters = printer.lookup_object('heaters')
    heater_dict = pheaters.get_all_heaters()
    logging.info("zero_overshoot_heater_bed ::INFO:: all_heaters = %s" % (heater_dict)) 
    heater = pheaters.lookup_heater('heater_bed')
    return ZeroOvershootHeaterBedControlPID(heater, config)
