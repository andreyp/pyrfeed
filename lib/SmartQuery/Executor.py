#!/usr/bin/env python

class QueryExecutor( object ) :
    def __init__(self,queries,*args,**kwargs) :
        self._queries = queries
        local_method_constructor = lambda element,method,_name : lambda **kwargs : getattr(element,method)(_name,**kwargs)
        for query_name in self._queries.keys() :
            setattr( self, query_name, local_method_constructor( self, '_execute_query', query_name ) )
        self._conn = self._get_connection(*args,**kwargs)
        self._cursor = None

        self._debug = False

    def _get_connection(self,*args,**kwargs):
        raise(UserWarning('_get_connection must be overloaded'))
        return None

    def __del__(self) :
        self.close()

    def _execute_query(self,_name,*args,**kwargs) :
        return self._execute_sql(self._queries[_name]['query'],*args,**kwargs)

    def _execute_sql(self,sql,*args,**kwargs) :
        if self._debug :
            import time
            debug_filename = 'executor-calls'
            handle = open(debug_filename,'at')
            handle.write('sql = %r\n' % sql)
            handle.write('args = %r\n' % (args,))
            handle.write('kwargs = %r\n' % (kwargs,))
            start_time = time.time()
            handle.write('timestamp (start) = %d\n' % start_time)
            handle.write('#----------------\n')
            handle.close()

        # print '[QUERY(%s):%s]' % (name,self._internal_queries[name] % kwargs,)
        if self._cursor :
            self._cursor.close()
            self._cursor = None
        self._cursor = self._conn.cursor()
        if self._use_seq() :
            self._cursor.execute(sql,self._parse_in_seq(args))
        elif self._use_dict() :
            self._cursor.execute(sql,self._parse_in_dict(kwargs))
        elif self._sim_dict() :
            self._cursor.execute(sql % self._parse_in_dict(kwargs))
        if self._debug :
            stop_time = time.time()
            handle = open(debug_filename,'at')
            handle.write('timestamp (stop) = %d\n' % stop_time)
            handle.write('duration = %d\n' % (stop_time-start_time))
            handle.write('#================\n')
            handle.close()

        return self._cursor.fetchall()

    def _use_seq(self) : return False
    def _use_dict(self) : return True
    def _sim_dict(self) : return not(self._use_seq() or self._use_dict())
    def _parse_in_seq(self,args) : return args
    def _parse_in_dict(self,kwargs) : return kwargs
    def _parse_out(self,args) : return args

    def begin( self ):
        pass

    def commit( self ):
        self._conn.commit()

    def rollback( self ):
        self._conn.rollback()

    def close( self ):
        if self._cursor :
            self._cursor.close()
            self._cursor = None
        if hasattr(self,'_conn') and self._conn :
            if hasattr(self._conn,'inTransaction') and self._conn.inTransaction :
                self._conn.commit()
            self._conn.close()
            self._conn = None

