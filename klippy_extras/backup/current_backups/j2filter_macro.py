# Utilize Python Code in your GCode Macros as Jinja2 Filters
#
# Copyright (C) 2022  Michael Carroll <mc999984@gmail.com>
# Some of this code may have been used, sourced, or referenced from Klipper source code
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# URL Resource: https://github.com/droans/klipper_extras/tree/v0.2/extended_macro
#
# add [j2filter_macro <macro_name>] sections to your printer.cfg file; 
# 
# you use this the same way you use [gcode_macro <macro_name>] but you
# will use [j2filter_macro <macro_name>] if your macro contains one of 
# your custom jinja2 filters in the macro definition area (i.e. after gcode:)
#     
#
# additinal contributions by:
#
# Discord List:
#  droans#3926
#  GadgetAngel#8701
#

import traceback, logging, ast, copy
import jinja2
import imp
import os, sys
import gcode_macro

######################################################################
# J2Filter Template handling
######################################################################
#
# Wrapper around a Jinja2 template
# Inherits TemplateWrapper from gcode_macro.py
# Only Change is the template context to utilize j2filter_macro
class J2FiltrTemplateWrapper(gcode_macro.TemplateWrapper):
    def __init__(self, printer, env, name, script):
        self.printer = printer
        self.name = name
        self.gcode = self.printer.lookup_object('gcode')
        gcode_macro = printer.lookup_object('j2filter_macro')        
        self.create_template_context = gcode_macro.create_template_context
        try:
            self.template = env.from_string(script)
        except Exception as e:
            msg = "Error loading template '%s': %s" % (
                 name, traceback.format_exception_only(type(e), e)[-1])
            logging.exception(msg)
            raise printer.config_error(msg)
            
######################################################################
# J2Filter PrinterGCodeMacro (Template handling contiued)
######################################################################
#
# Inherits PrinterGCodeMacro from gcode_macro.py
# Code added to utilize 
class J2FiltrPrinterGCodeMacro(gcode_macro.PrinterGCodeMacro):     
    def __init__(self, config):        
        gcode_macro.PrinterGCodeMacro.__init__(self, config)       
        j2filter_template_obj = self.printer.load_object(config, 'j2filter_template')   #load object from j2filter_template.py file
        jinja2func = j2filter_template_obj.J2func
        jinja2filter = j2filter_template_obj.J2filter
        for name, filtr in j2filter_template_obj.Filters.items():
            if jinja2func == True:
                jinja_func = {name:filtr}
                self.env.globals.update(**jinja_func)
            if jinja2filter == True:
                # enxtend jinja2 with a custom filter called "name" from python function called "filtr" 
                self.env.filters[name] = filtr

def load_config(config):
    return J2FiltrPrinterGCodeMacro(config)

######################################################################
# J2Filter GCode macro
######################################################################
#
# Inherits GCodeMacro from gcode_macro.py
# Only changes the template objects
class J2FiltrGCodeMacro(gcode_macro.GCodeMacro):
    def __init__(self, config):
        if len(config.get_name().split()) > 2:
            raise config.error(
                    "Name of section '%s' contains illegal whitespace"
                    % (config.get_name()))
        name = config.get_name().split()[1]
        self.alias = name.upper()
        self.printer = printer = config.get_printer()
        gcode_macro = printer.load_object(config, 'j2filter_macro')
        self.template = gcode_macro.load_template(config, 'gcode')
        self.gcode = printer.lookup_object('gcode')
        self.rename_existing = config.get("rename_existing", None)
        self.cmd_desc = config.get("description", "G-Code macro")
        if self.rename_existing is not None:
            if (self.gcode.is_traditional_gcode(self.alias)
                != self.gcode.is_traditional_gcode(self.rename_existing)):
                raise config.error(
                    "G-Code macro rename of different types ('%s' vs '%s')"
                    % (self.alias, self.rename_existing))
            printer.register_event_handler("klippy:connect",
                                           self.handle_connect)
        else:
            self.gcode.register_command(self.alias, self.cmd,
                                        desc=self.cmd_desc)
        self.gcode.register_mux_command("SET_GCODE_VARIABLE", "MACRO",
                                        name, self.cmd_SET_GCODE_VARIABLE,
                                        desc=self.cmd_SET_GCODE_VARIABLE_help)
        self.in_script = False
        self.variables = {}
        prefix = 'variable_'
        for option in config.get_prefix_options(prefix):
            try:
                self.variables[option[len(prefix):]] = ast.literal_eval(
                    config.get(option))
            except ValueError as e:
                raise config.error(
                    "Option '%s' in section '%s' is not a valid literal" % (
                        option, config.get_name()))

def load_config_prefix(config):
    return J2FiltrGCodeMacro(config)
