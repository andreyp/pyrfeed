#!/usr/bin/env python

PYTHONLINE = '/usr/bin/env python'
ENCODING = 'iso-8859-1'

import os

class Generator(object) :
    def __init__(self,*args) :
        self._handle = None
        if len(args)>0 :
            self.set_filename(*args)

    def set_filename(self,*args) :
        if self._handle :
            self.close()
        handle = file(os.path.join(*args), 'wt' )

        self._handle = handle
        self += '#!' + PYTHONLINE
        self += '# coding : ' + ENCODING + ''
        self += ''

    def close(self) :
        if self._handle :
            self._handle.close()
            self._handle = None

    def add_line(self,line) :
        self._handle.write(line)
        self._handle.write("\n")

    def __iadd__(self,line):
        self.add_line(line)
        return self


def test() :
    Generator('poide.py')

if __name__ == '__main__' :
    test()