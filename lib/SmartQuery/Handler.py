#!/usr/bin/env python
import os
from ScriptGenerator import Generator

class QueryHandler( object ) :
    _prefix = ' ' * 4 * 4
    _classfullpath = 'SmartQuery.Handler'
    _classfullname = 'QueryHandler'

    def __init__(self, queries={}, dir='queries') :
        self._internal_dir = dir
        self._internal_queries = queries

    def _get_dirname( self, dirname=None ) :
        if dirname == None :
            dirname = self._internal_dir
        return dirname.replace('.',os.path.sep)

    def _get_modname( self, dirname=None ) :
        if dirname == None :
            dirname = self._internal_dir
        return dirname.replace(os.path.sep,'.')

    def _get_lastmodname( self, dirname=None ) :
        modname = self._get_modname(dirname)
        return modname[modname.rfind('.')+1:]

    def write_debug( self, dirname=None ) :
        dirname = self._get_dirname(dirname)
        modname = self._get_modname(dirname)
        lastmodname = self._get_lastmodname(dirname)

        filename = modname + "-optimize" + ".py"
        
        script = Generator(filename)
        script += 'from '+self._classfullpath+' import '+self._classfullname
        script += ''
        script += 'import '+modname+' as '+lastmodname
        script += 'q = '+self._classfullname+'( queries='+lastmodname+'.queries )'
        script += 'q.writeo( \''+modname+'\' )'
        script.close()

        filename = modname + "-split" + ".py"

        script = Generator(filename)
        script += 'from '+self._classfullpath+' import '+self._classfullname
        script += ''
        script += 'import '+modname+'_o as '+lastmodname
        script += 'q = '+self._classfullname+'( queries='+lastmodname+'.queries )'
        script += 'q.write( \''+modname+'\' )'
        script.close()
        
    def write_all( self, dirname=None ) :
        modname = self._get_modname(dirname)

        self.write( modname )
        self.writeo( modname, normalized=True )

    def write( self, dirname=None ) :
        dirname = self._get_dirname(dirname)
        modname = self._get_modname(dirname)

        self._normalize()

        for name in self._internal_queries :

            xdirname = os.path.join( dirname, os.path.join(*self._internal_queries[name]['path']) )
            try :
                os.makedirs( xdirname )
            except OSError :
                pass
            handle = file(os.path.join( xdirname, name+".sql" ), 'wt' )
            for line in self._internal_queries[name]['query'].split('\n') :
                if line[:len(self._prefix)] == self._prefix :
                    line = line[len(self._prefix):]
                if len(line) > 0 :
                    handle.write( line )
                    handle.write( "\n" )
            handle.close()

        self.makemodule( dirname )

    def makemodule( self, dirname=None ) :
        dirname = self._get_dirname(dirname)

        script = Generator(os.path.join(dirname,"__init__.py"))
        script += 'from '+self._classfullpath+' import '+self._classfullname
        script += ''
        script += "handler = "+self._classfullname+"(dir=__name__)"
        script += "queries = handler.read()"
        script.close()


    def writeo( self, dirname=None, normalized=False ) :
        dirname = self._get_dirname(dirname)

        if not(normalized) :
            self._normalize()

        filename = dirname + "_o" + ".py"
        script = Generator(filename)
        script += ''
        script += 'queries = {'
        
        queries_names = self._internal_queries.keys()
        queries_names.sort( lambda k1,k2 : cmp(tuple(self._internal_queries[k1]["path"] + [k1]),tuple(self._internal_queries[k2]['path']+[k2])) )
        for name in queries_names :
            script += (' '*4*1) + "'%s' :" % (name,)
            script += (' '*4*2) + '{ "path" : '+repr(self._internal_queries[name]["path"])+','
            script += (' '*4*2) + '  "query" : '
            script += (' '*4*3) + '"""'
            script += self._internal_queries[name]["query"]+(' '*4*3)+'""" } ,'
        script += ' '*4*1 + '}'
        script += ''

        script.close()

    def read( self, dirname=None ) :
        dirname = self._get_dirname(dirname)

        self._internal_queries = {}

        def update_with_files( args, path, files ):
            dirname = args[0]
            internal_queries = args[1]
            xpath = path[len(dirname):].split(os.path.sep)

            if len(xpath)>0 and xpath[0]=="" :
                xpath = xpath[1:]

            if len(xpath) == 0 :
                xpath = ['.']

            for filename in files:
                filename = filename.lower()
                if (len(filename) > 4) and (filename[-4:] == '.sql') :
                    name = filename[:-4]
                    handle = file( os.path.join( path, filename ), 'rt' )
                    internal_queries[name] = { "path" : xpath, "query" : "" }
                    for line in handle.read().split('\n') :
                        if line.strip() != '' :
                            internal_queries[name]["query"] += self._prefix
                            internal_queries[name]["query"] += line
                            internal_queries[name]["query"] += '\n'
                    handle.close()

        os.path.walk( dirname, update_with_files , (dirname, self._internal_queries) )

        self._normalize()

        return self._internal_queries

    def _normalize(self) :
        for name in self._internal_queries :
            if type(self._internal_queries[name]) == dict :
                query = self._internal_queries[name]['query']
            else :
                query = self._internal_queries[name]
                self._internal_queries[name] = { 'path' : ['.'], 'query' : '' }
            self._internal_queries[name]['query'] = ''
            for line in query.split('\n') :
                if line.strip() != '' :
                    self._internal_queries[name]['query'] += line
                    self._internal_queries[name]['query'] += '\n'

def test1() :
    q = QueryHandler()
    q.read( 'torrents_s' )
    q.write_all( 'torrents_q' )

def test2() :
    from torrents_q import queries
    q = QueryHandler( queries=queries )
    q.write_all( 'torrents_qq' )

def test3() :
    from torrents_qo import queries
    q = QueryHandler( queries=queries )
    q.write_all( 'torrents_qoq' )

def longtest() :
    test1()
    test2()
    test3()

def optimize() :
    from query_torrents import queries
    q = QueryHandler( queries=queries )
    q.writeo( 'query_torrents' )

def qsplit() :
    from query_torrents_o import queries
    q = QueryHandler( queries=queries )
    q.write( 'query_torrents' )

if __name__ == '__main__' :
    optimize()

