#!/usr/bin/env python
# coding: iso-8859-1

from SmartQuery.Handler import QueryHandler
from sys import argv

def main(dirname) :
    handler = QueryHandler(dir=dirname)
    handler.makemodule()
    handler.write_debug()
    
if __name__=='__main__' :
    if len(argv) >= 2 :
        main(argv[1])
