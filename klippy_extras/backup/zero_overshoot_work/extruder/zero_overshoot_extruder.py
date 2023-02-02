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
from kinematics import extruder as EXTRUDER_OBJ

class ZeroOvershootHeater(Heater_OBJ):
    def __init__(self, config, sensor):
    

# def load_config_prefix(config):
    # heater_name = config.get_name().split()[-1]
    # printer = config.get_printer()
    # pheaters = printer.lookup_object('heaters')
    # heater = pheaters.lookup_heater(heater_name)
    # return NoOvershootControlPID(heater, config)
    
######################################################################
# NO_OVERSHOOT_EXTRUDER extension inherits from heaters.ControlPID
######################################################################

PID_PARAM_BASE = 255.000

class ZeroOvershootExtruderControlPID(ControlPID_OBJ):
    def __init__(self, heater, config):
        self.heater = heater
        # extruder_config = config.getsection('extruder')
        ControlPID_OBJ.__init__(self, heater, config)
        printer = config.get_printer()
        # ControlPID_OBJ.__init__(self, heater, config)
        
        self.const_one_third = 1./3.
        self.const_88 = 88./100.
        
        self.no_overshoot = config.getboolean('no_overshoot', False)
        self.Kp_multiplier = config.getfloat('Kp_multiplier',None)
        self.Ki_multiplier = config.getfloat('Ki_multiplier',None)
        self.Kd_multiplier = config.getfloat('Kd_multiplier',None)
        
        printer.register_event_handler("klippy:ready", self.handle_ready)
        
    def handle_ready(self):    
        self.heater = heater
        pheaters = printer.lookup_object('heaters')
        # for i in range(99):
            # section = 'extruder'
            # if i:
                # section = 'extruder%d' % (i,)
            # if not config.has_section(section):
                # break
            # pe = EXTRUDER_OBJ.PrinterExtruder(config.getsection(section), i)
            # extruder_objs[i] = pe
            # heaters[i] = pe.get_heater()
        # i -= 1
        # heater = heaters[i]
        # extruder_obj = printer.objects['extruder']
        extruder_obj = printer.lookup_object('extruder', None)
        # extruder_obj = extruder_objs[i]        
        extruder_heater = extruder_obj.get_heater()
        extruder_name = extruder_obj.get_name()
        # extruder_heater = extruder_obj.heater
        # extruder_name = extruder_obj.name
        
        if self.heater.name == extruder_name:
            logging.info("no_overshoot ::INFO:: Printer has the following additional setting for [no_overshoot %s]: no_overshoot = %s" % (self.heater.name, self.no_overshoot)) 
        
        # heater_bed section
        if ((self.no_overshoot == True) and (self.heater.name == extruder_name)):
            logging.info("no_overshoot ::INFO:: Printer has the following additional setting for [no_overshoot %s]: Kp_multiplier = %s" % (self.heater.name, self.Kp_multiplier)) 
            logging.info("no_overshoot ::INFO:: Printer has the following additional setting for [no_overshoot %s]: Ki_multiplier = %s" % (self.heater.name, self.Ki_multiplier)) 
            logging.info("no_overshoot ::INFO:: Printer has the following additional setting for [no_overshoot %s]: Kd_multiplier = %s" % (self.heater.name, self.Kd_multiplier)) 
            if self.Kp_multiplier is None:
                self.Kp_multiplier = self.const_one_third
            if self.Ki_multiplier is None:
                self.Ki_multiplier = self.const_one_third
            if self.Kd_multiplier is None:
                self.Kd_multiplier = self.const_88
            myKp = self.Kp * PID_PARAM_BASE                                          
            myKi = self.Ki * PID_PARAM_BASE                                          
            myKd = self.Kd * PID_PARAM_BASE                                         
            myKp = round((myKp * self.Kp_multiplier),3)       
            myKi = round((myKi * self.Ki_multiplier),3)       
            myKd = round((myKd * self.Kd_multiplier),3)       
            logging.info("no_overshoot ::INFO:: [%s] no_overshoot value: pid_Kp = %3.3f" % (self.heater.name, myKp)) 
            logging.info("no_overshoot ::INFO:: [%s] no_overshoot value: pid_Ki = %3.3f" % (self.heater.name, myKi)) 
            logging.info("no_overshoot ::INFO:: [%s] no_overshoot value: pid_Kd = %3.3f" % (self.heater.name, myKd)) 
            self.Kp = myKp / PID_PARAM_BASE                                          
            self.Ki = myKi / PID_PARAM_BASE                                          
            self.Kd = myKd / PID_PARAM_BASE                                          
            self.temp_integ_max = 0.
            if self.Ki:
                self.temp_integ_max = self.heater_max_power / self.Ki

# def load_config(config):
    # heater_name = config.get_name().split()[-1]
    # printer = config.get_printer()
    # pheaters = printer.lookup_object('heaters')
    # heater = pheaters.lookup_heater(heater_name)
    # return NoOvershootControlPID(heater, config)
    
# def add_printer_objects(config):
    # printer = config.get_printer()
    # for i in range(99):
        # section = 'extruder'
        # if i:
            # section = 'extruder%d' % (i,)
        # if not config.has_section(section):
            # break
        # pe = EXTRUDER_OBJ.PrinterExtruder(config.getsection(section), i)
        # printer.add_object(section, pe)
        # return printer.objects(section)

def load_config(config):
    printer = config.get_printer()
    def handle_ready(config): 
        printer = config.get_printer()
        extruder2 = printer.lookup_object('extruder', None)
        if extruder2 is None:
            return ZeroOvershootExtruderControlPID(printer.objects['T0'].heater, config)
        logging.info("no_overshoot ::INFO:: extruder2 = %s" % (extruder2)) 
        heater2 = extruder2.get_heater()
        logging.info("no_overshoot ::INFO:: heater2 = %s" % (heater2))            
        return ZeroOvershootExtruderControlPID(heater2, config)
    printer.register_event_handler("klippy:ready", handle_ready(config))
    pheaters = printer.lookup_object('heaters')
    extruder = printer.lookup_object('extruder')
    heater_dict = pheaters.get_all_heaters()
    logging.info("no_overshoot ::INFO:: all_heaters = %s" % (heater_dict)) 

    if not extruder is None:
        # extruder_obj = printer.load_object(config, 'extruder')
        # heater = extruder_obj.get_heater()
        # for i in range(99):
        # section = 'extruder'
        # if i:
            # section = 'extruder%d' % (i,)
        # if not config.has_section(section):
            # break
        # logging.info("no_overshoot ::INFO:: i = %s; section = %s" % (i,section)) 
        # pe = EXTRUDER_OBJ.PrinterExtruder(config.getsection(section), i)
        # heaters[i] = pe.get_heater()
        # i -= 1
        # heater =  heaters[i]
        # logging.info("no_overshoot ::INFO:: extruder is NONE") 
        # EXTRUDER_OBJ.PrinterExtruder(config.getsection('extruder'), 0).heater
        # PrinterExtruder(config.getsection(section), i)
        # extruder_obj = printer.objects['extruder']
        # heater = extruder_obj.heater
        logging.info("no_overshoot ::INFO:: extruder = %s" % (extruder)) 
        heater = extruder.get_heater()
        logging.info("no_overshoot ::INFO:: heater = %s" % (heater)) 
        return ZeroOvershootExtruderControlPID(heater, config)
    else:
        logging.info("no_overshoot ::INFO:: extruder is NONE") 
