# Tracking of PWM controlled heaters and their temperature control
#
# Copyright (C) 2016-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from .heaters import ControlPID as ControlPID_OBJ

######################################################################
# NO_OVERSHOOT_HEATER_BED extension inherits from heaters.ControlPID
######################################################################

PID_PARAM_BASE = 255.000

class NoOvershootControlPID(ControlPID_OBJ):
    def __init__(self, heater, config):
        heater_bed_config = config.getsection('heater_bed')
        ControlPID_OBJ.__init__(self, heater, heater_bed_config)
        
        self.heater = heater
        printer = config.get_printer()
        pheaters = printer.lookup_object('heaters')
        heater_bed_obj = pheaters.lookup_heater('heater_bed')
        self.no_overshoot = config.getboolean('no_overshoot', False)
        logging.info("no_overshoot_heater_bed ::INFO:: Printer has the following additional setting for [no_overshoot_heater_bed]: no_overshoot = %s" % (self.no_overshoot)) 
        if ((self.no_overshoot == True) and (self.heater.name == heater_bed_obj.name)):
            myKp = self.Kp * PID_PARAM_BASE      #get the value back from configfile config section
            myKi = self.Ki * PID_PARAM_BASE      #get the value back from configfile config section
            myKd = self.Kd * PID_PARAM_BASE      #get the value back from configfile config section
            myKp = round((myKp / 3.000),3)       #convert to no_overshoot value
            myKi = round((myKi / 3.000),3)       #convert to no_overshoot value
            myKd = round((myKd * 0.880),3)       #convert to no_overshoot value
            logging.info("no_overshoot_heater_bed ::INFO:: [heater_bed] no_overshoot value: pid_Kp = %3.3f" % (myKp)) 
            logging.info("no_overshoot_heater_bed ::INFO:: [heater_bed] no_overshoot value: pid_Ki = %3.3f" % (myKi)) 
            logging.info("no_overshoot_heater_bed ::INFO:: [heater_bed] no_overshoot value: pid_Kd = %3.3f" % (myKd)) 
            # heaters.ControlPID after __init__ divides all values by PID_PARAM_BASE
            self.Kp = myKp / PID_PARAM_BASE      #leave the value the way heaters.ControlPID.__init__ does
            self.Ki = myKi / PID_PARAM_BASE      #leave the value the way heaters.ControlPID.__init__ does
            self.Kd = myKd / PID_PARAM_BASE      #leave the value the way heaters.ControlPID.__init__ does
            self.temp_integ_max = 0.
            if self.Ki:
                self.temp_integ_max = self.heater_max_power / self.Ki
    def _build_config(self):
        pass

def load_config(config):
    printer = config.get_printer()
    pheaters = printer.lookup_object('heaters')
    heater = pheaters.lookup_heater('heater_bed')
    return NoOvershootControlPID(heater, config)
