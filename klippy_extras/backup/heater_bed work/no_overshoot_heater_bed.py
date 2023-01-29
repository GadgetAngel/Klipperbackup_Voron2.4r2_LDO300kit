# Tracking of PWM controlled heaters and their temperature control
#
# Copyright (C) 2016-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import heaters

######################################################################
# NO_OVERSHOOT_HEATER_BED extension inherits from heaters.ControlPID
######################################################################

class NoOvershootControlPID(heaters.ControlPID):
    def __init__(self, heater, config):
        heaters.ControlPID.__init__(self, heater, config)
        
        printer = config.get_printer()
        pheaters = printer.lookup_object('heaters')
        heater_bed_obj = pheaters.lookup_heater('heater_bed')
        self.no_overshoot = config.getboolean('no_overshoot', False)
        logging.info("no_overshoot_heater_bed ::INFO:: Printer has the following additional setting for no_overshoot_heater_bed: no_overshoot = %s" % (self.no_overshoot)) 
        if ((self.no_overshoot == True) and (heater.name == heater_bed_obj.name)):
            self.Kp = round((self.Kp / 3.000),3)
            self.Ki = round((self.Ki / 3.000),3)
            self.Kd = round((self.Kd * 0.880),3)
            logging.info("no_overshoot_heater_bed ::INFO:: pid_kp = %s" % (self.Kp)) 
            logging.info("no_overshoot_heater_bed ::INFO:: pid_ki = %s" % (self.Ki)) 
            logging.info("no_overshoot_heater_bed ::INFO:: pid_kd = %s" % (self.Kd)) 

def load_config(config):
    return NoOvershootControlPID(config)
