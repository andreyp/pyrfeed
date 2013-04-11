#!/usr/bin/env python

import sqlite
import Executor

class QueryExecutor( Executor.QueryExecutor ) :
    def __init__(self,dbname,queries) :
        Executor.QueryExecutor.__init__(self,queries,dbname)
    def begin( self ):
        pass
    def _get_connection(self,dbname):
        return sqlite.connect(dbname,autocommit=1)
    def _use_seq(self) : return False
    def _use_dict(self) : return True
