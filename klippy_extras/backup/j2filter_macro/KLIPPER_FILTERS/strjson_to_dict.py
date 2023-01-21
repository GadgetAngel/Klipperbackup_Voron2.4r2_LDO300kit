import json
  
def strjson_to_dict(dict_string):
    """
    Custom Jinja2 filter - json_todict

    :param dict_string: string to be converted to dictionary structure
    :return: res - python dictionary data type from a properly json string (must use double quotes around the key name! i.e. not sinqle quotes)
    """

    # using json.loads()
    # convert dictionary string to dictionary
    res = json.loads(dict_string)
    return res
