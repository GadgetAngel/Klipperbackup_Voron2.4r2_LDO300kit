import json
  
def string_to_dict(dic_string): 
    """
    Custom Jinja2 filter - str_todict

    :param dic_string: string to be converted to dictionary structure
    :return: dict_out - python dictionary data type
    """

    # remove the curly braces from the string
    dic_string = dic_string.strip('{}')

    # split the string into key-value pairs
    pairs = dic_string.split(', ')
    
    #define a blank dict obj
    dict_out = {}

    # use a dictionary comprehension to create the dictionary,
    # converting the value to float or integer depending if a '.' is present in value
    for key,value in (pair.split(': ') for pair in pairs):
        if '"' in key:
            key = key.replace('"','',2)
        elif "'" in key:
            key = key.replace("'","",2)

        if '.' in value:
            val = float(value)
            dict_out.update({key: val})
        else:
            val = int(value)
            dict_out.update({key: val})

    return dict_out
