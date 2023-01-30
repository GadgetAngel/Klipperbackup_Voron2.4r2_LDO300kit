# Copyright (C) 2017-2021  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
#
# URL Resource: https://github.com/droans/klipper_extras/tree/v0.2/extended_macro
#
#
# add [j2filter_template] section to your printer.cfg file
#      path: <full path to>filname.yaml
#      jinja2_function: <True, False>   -- use the python function code as a function call with the Gcode macro --> G0 X{func_name(params)}
#      jinja2_filter: <True, False>     -- use the python function code as a jinja2 filter within the JINJA2 template  -> variable | filter_name
#
## example:
#  [j2filter_template]
#  path: /home/pi/klipper_config/ACTIVE/CONFIG/KLIPPER_FILTERS/filters_config.yaml
#  jinja2_function: False
#  jinja2_filter: True 
#
# additinal contributions by:
#
# Discord List:
#  droans#3926
#  GadgetAngel#8701


# Necessary modules for configuration
import os, yaml, imp

# Additional defaults for G-Code
import math, pandas, numpy, datetime, itertools, collections

# DEFAULTS
# The default imports to be loaded by j2filter_template. 
# These do not need to be defined by the user in their config file
# If there is a name collision, the default imports will be given priority
# while the user defined Filters are renamed with an underscore.
# 
# For example, if the user were to define their own filter named `list` (the same name as a default below),
# the user defined `list` will be renamed to `_list`.
DEFAULTS = {
    'math': math,
    'pandas': pandas,
    'numpy': numpy,
    'datetime': datetime,
    'itertools': itertools,
    'collections': collections,
    'dir': dir,
    'getattr': getattr,
    'setattr': setattr,
    'locals': locals,
    'globals': globals,
    'list': list,
    'dict': dict,
    'set': set,
    'tuple': tuple,
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'type': type,
}

class Logger():
    def __init__(self, config):
        self.Error = config.error

# Load YAML config to self.Filters so the template loader can be created
class YamlLoader():
    def __init__(self, yaml_path, config):
        self.DefaultsLoaded = False
        self.path = yaml_path
        self.Log = Logger(config)

        with open(yaml_path, 'r') as f:
            self.yaml = yaml.load(f, Loader=yaml.Loader)
        
        filter_yaml = self.yaml.get('filters',None)
        self._filter = self._import_filter_dict(filter_yaml)

    # Loops through each item in the config, passes
    # the data off to _import_filter which will return
    # the actual filter if it exists, and then adds
    # each filter to the filter dictionary so they can 
    # be added by gcode_j2filtr_macro to the Jinja2 environment

    def GetFilters(self):
        return self._filter

    def _import_filter_dict(self, filters):
        return_filter = {}
        for key, val in filters.items():
            filtr = self._import_filter(val['path'], val['filter'])
            return_filter[key] = filtr
        return return_filter

    def _import_filter(self, filtr_path, filter_name):
        module = imp.load_source('script', filtr_path)
        if filter_name not in dir(module):
            raise self.Log.Error('j2filter_template: Filter %s not found in file %s' % (filter_name, filtr_path))
        else:
            filtr = getattr(module, filter_name)
            return filtr

class DefaultLoader:
    def __init__(self, yaml_path, config):
        self.DefaultsLoaded = True
        self.path = yaml_path
        self.Log = Logger(config)
        self._filter = self._load_defaults()

    def _load_defaults(self):
        def_filter = {}
        for name, filtr in DEFAULTS.items():
            def_filter[name] = filtr
        return def_filter

    def GetFilters(self):
        return self._filter


# Grabs the Klipper config for j2filter_template,
# uses the path variable to determine the extension,
# determines the proper loader for that extension,
# and returns the value from that loader which received
# the path and the Klipper config object.

class CustomJinja2Filters:
    def __init__(self, config):
        # CustomJinja2Filters._load_filters need self.config
        self.config = config       
        # self.printer = self.config.get_printer()
        # self.gcode = self.printer.lookup_object('gcode')
        self.Log = Logger(config)
        
        self.config_path = config.get('path', None)
        
        # #setup flags so user has a choice to how they want to use the python functions
        jfunction = config.getboolean('jinja2_function', True)
        jfilter = config.getboolean('jinja2_filter', True)
        
        self.Filters = self._import()
        
        self.J2func = jfunction
        self.J2filter = jfilter

    def _import(self):
        defaults_loaded = False
        if self.config_path is not None:
            user_filters, defaults_loaded = self._import_user_filters()
        else:
            user_filters = []
            defaults_loaded = False

        if not defaults_loaded:
            default_filters, defaults_loaded = self._load_defaults()

        all_filters = {}
        all_filters = default_filters.copy()

        for key, val in user_filters.items():
            if key in all_filters:
                u_key = '_%s' % key
            else:
                u_key = key

            all_filters[u_key] = val

        print('All Filters:')
        print(all_filters)
        return all_filters
        
    def _get_loader(self, ext):
        loader = None
        for l in LOADERS:
            c_ext = l['extensions']

            if type(c_ext) is str:
                c_ext = [c_ext]

            if ext in l['extensions']:
                loader = l['filter_loader']
                return loader

        if loader is None:
            raise self.Log.Error('j2filter_template: No loader found for extension %s' % ext)

    def _import_user_filters(self):
        ext = self.config_path.split('.')[-1]
        loader = self._get_loader(ext)
        filters, defaults_loaded = self._load_filters(loader, self.config_path)
        return filters, defaults_loaded

    def _load_defaults(self):
        loader = self._get_loader('default')
        return self._load_filters(loader)
        
    def _load_filters(self, loader, config_path = None):
        result = loader(config_path, self.config)
        filters = result.GetFilters()
        defaults_loaded = result.DefaultsLoaded

        return filters, defaults_loaded

    def _insert_filter(self, filter_name, filtr):
        if filter_name in self.Filters: 
            filter_name = '_%s' % filter_name

def load_config(config):
    return CustomJinja2Filters(config)

# LOADERS
# The definitions in this list will be used to determine the proper loader for the extensions given
# 
# Since different loaders might need or want different methods of parsing the file, 
# the script expects that the loader is a function, not a class. The function should
# process the config file and return a dictionary with the jinja filter name as the key
# and the actual Python function as the value
# 
# The loader for DEFAULTS should be defined with an extension of ['default']
# This loader will be ignored if the property loader.DefaultsLoaded property is true (see below)
# 
# Definition: {'extensions': <collection_or_string>, 'loader': <class>}
# 
# Arguments received: 
#   * config_path: Path to config set in [j2filter_template]
#   * config: Config object received from Klipper
#
# Required Properties and Filters:
#   * loader.DefaultsLoaded <property>: <bool>
#       - If True, it is assumed the loader has loaded the defaults listed below. 
#       - If False, assumes the loader has not loaded the defaults listed below.
#       - It is suggested that the Loader should never process defaults unless:
#           * The user defines the defaults in the config file
#           * The loader defines it's own defaults
#           * Any other scenario where it's better to load the defaults by the loader instead of separately
#   * loader.GetFilters(self) <filter> = <dict> 
#       - Loads user-defined Filters.
#           * Optionally, 
#       - Returns schema: {defined_filter_name_for_jinja <str>: filter <callable>}
# 
# 
LOADERS = [
    {
        'extensions': ['yaml','yml'],
        'filter_loader': YamlLoader
    }
    ,
    {
        'extensions': ['default'],
        'filter_loader': DefaultLoader
    }
]

