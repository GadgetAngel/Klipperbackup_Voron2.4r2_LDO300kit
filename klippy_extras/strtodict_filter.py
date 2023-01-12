# strtodict_filter.py
# place this file in ~/klipper directory
#
# To make this file executable:
#  sudo chmod +x strtodict_filter.py
#

#!/usr/bin/env python2
import jinja2
from string_to_dict_filter import string_to_dict

env = jinja2.Environment()
env.filters["strtodict"] = string_to_dict

# to test if the filter is working
tmpl_string = """{{ "{'x': 250, 'y': 50, 'z': 70, 'f': 4000.0}"|strtodict   }}"""
tmpl = env.from_string(tmpl_string)
print(tmpl.render())

