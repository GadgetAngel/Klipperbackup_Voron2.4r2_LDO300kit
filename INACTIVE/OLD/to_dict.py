import json
  
def string_to_dict(dic_string):    
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
  
def strjson_to_dict(dict_string):
    # using json.loads()
    # convert dictionary string to dictionary
    res = json.loads(dict_string)
    return res
