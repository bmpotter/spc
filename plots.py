import json
import re

class plot(object):

    def get_data(self,fn,col1,col2):
        y = ''
        for line in open(fn, 'rU'):
            # don't parse comments
            if re.search(r'#',line): continue
            x = line.split()
            if not re.search(r'[A-Za-z]{2,}\s+[A-Za-z]{2,}',line):
                y += '[ ' + x[col1] + ', ' + x[col2] + '], ' 
        str = "[ %s ]" % y
        return str