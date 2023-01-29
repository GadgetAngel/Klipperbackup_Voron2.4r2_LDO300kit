def degree_symbol(string1): 
    
    # Custom Jinja2 filter - str_todict
    # https://nedbatchelder.com/text/unipain.html
    #:return: string for degree symbol
    #u'\N{DEGREE SIGN}'.encode('ascii', 'ignore')
    x=u'\N{DEGREE SIGN}'
    #x.encode('utf-8')
    return x
