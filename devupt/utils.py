# just a couple utilities to make debugging and printing messages easier

from scrapy import log

# custom logger with colors
def devlog(msg, lvl=''):
    ll = log.INFO
    if lvl == 'd':
        ll = log.DEBUG
    elif lvl == 'w':
        ll = log.WARNING
    elif lvl == 'e':
        ll = log.ERROR
    log.msg(bcolors.WARNING + msg + bcolors.ENDC, level=ll)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
    
