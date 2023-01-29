class myConfigParser(object):     
    def __init__(self, origobj):         
        self.myobj = origobj    
        
    def getFormula(self, section, option):         
        retString = self.get(section, option)
        return eval(retString)     
        
    def __getattr__(self, attr):         
        return getattr(self.myobj, attr)
        
# looks pretty good, my only suggestion would be that it is possibly dangerous 
# to be evaling code from a config file, but it really depends on how this code 
# will be used. If it is just for you to use, it probably doesn't matter. 
# If you will be releasing it for others to use, you might want to add a bit of 
# verification to the retString before you eval it