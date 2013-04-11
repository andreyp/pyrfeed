#!/usr/bin/env python

import sqlite3
import Executor

class sql_str(str) :
    def __repr__(self) :
        return "'%s'" % self.replace("'","''")

class sql_unicode(unicode) :
    def __repr__(self) :
        return "'%s'" % self.replace("'","''")

class QueryExecutor( Executor.QueryExecutor ) :
    def __init__(self,dbname,queries) :
        Executor.QueryExecutor.__init__(self,queries,dbname)
        self.__in_transaction = False

    def _get_connection(self,dbname):
        return sqlite3.connect(dbname)
    def _use_seq(self) : return False
    def _use_dict(self) : return False
    def _parse_in_dict(self,kwargs) :
        result = {}
        for key in kwargs :
            if type(kwargs[key])==str :
                result[key] = sql_str(kwargs[key])
            elif type(kwargs[key])==unicode :
                result[key] = sql_unicode(kwargs[key])
            else :
                result[key] = kwargs[key]
        return result
