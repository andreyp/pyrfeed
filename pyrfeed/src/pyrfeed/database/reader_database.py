import os

try :
    from SmartQuery.SQLite3Executor import QueryExecutor
except ImportError :
    from SmartQuery.SQLiteExecutor import QueryExecutor

from reader_query import queries

class ReaderDatabase ( object ) :
    def __init__( self, dbname, debug=False ) :
        self._dbname = dbname
        self._base_exist = False
        if os.path.isfile(self._dbname) :
            self._base_exist = True
        self._queries = QueryExecutor(self._dbname,queries)
        self._queries._debug = debug
        if not(self._base_exist) :
            self.create()

        self._items_categories = []

    def create(self) :
        self.begin()

        self._queries._execute_sql('BEGIN TRANSACTION')
        self._queries.create_table_item()
        self._queries.create_index_item_google_id()
        self._queries.create_index_item_published()
        self._queries.create_index_item_updated()
        self._queries.create_index_item_crawled()

        self._queries.create_table_author()
        self._queries.create_index_author_author()

        self._queries.create_table_categorie()
        self._queries.create_index_categorie_name()
        self._queries.create_index_categorie_shortname()

        self._queries.create_table_itemcategorie()
        self._queries.create_index_itemcategorie_iditem()
        self._queries.create_index_itemcategorie_idcategorie()
        self._queries.create_index_itemcategorie_iditem_idcategorie()

        self._queries.create_table_actionitemcategorie()

        self._queries.create_table__tmpitem()
        self._queries.create_index__tmpitem_google_id()
        self._queries.create_index__tmpitem_author()

        self._queries.create_table__tmpitemcategorie()
        self._queries.create_index__tmpitemcategorie_google_id()
        self._queries.create_index__tmpitemcategorie_categorie_name()
        self._queries.create_index__tmpitemcategorie_categorie_shortname()

        self._queries.create_table__tmpactionitemcategorie()
        self._queries.create_index__tmpactionitemcategorie_google_id()
        self._queries.create_index__tmpactionitemcategorie_categorie_name()
        self._queries.create_index__tmpactionitemcategorie_categorie_shortname()
        self._queries._execute_sql('COMMIT')

        self.commit()
        self._base_exist = True

    def _flush_tmp(self) :
        self.begin()
        self._queries.flush_into_author()
        self._queries.flush_into_categorie()
        self._queries.flush_action_into_categorie()
        self._queries.flush_into_item()
        self._queries.clean_itemcategorie_for_flush()
        self._queries.flush_into_itemcategorie()
        self._queries.clean_tmpitem()
        self._queries.clean_tmpitemcategorie()
        self._queries.invalidate_actionitemcategorie()
        self._queries.invalidate_tmpactionitemcategorie()
        self._queries.flush_into_actionitemcategorie()
        self._queries.clean_tmpactionitemcategorie()
        self._queries.do_action_del_on_itemcategorie()
        self._queries.do_action_add_on_itemcategorie()
        self.commit()

    def begin(self) :
        self._queries.commit()
        self._queries.begin()

    def commit(self) :
        self._queries.commit()

    def rollback(self) :
        self._queries.rollback()

    def start_add_session(self) :
        pass

    def add_item(self,**kwargs) :
        self._queries.add_tmpitem(**kwargs)

    def add_item_categorie(self,**kwargs) :
        self._queries.add_tmpitemcategorie(**kwargs)

    def add_action_item_categorie(self,**kwargs) :
        self._queries.add_tmpactionitemcategorie(**kwargs)

    def stop_add_session(self) :
        self.commit()
        self._flush_tmp()
        self.commit()

    def get_content(self,google_id) :
        for results in self._queries.get_content(google_id=google_id) :
            return { 'content':results[0], 'title':results[1], 'published':results[2] }
        return { 'content':'', 'title':'', 'published':0 }

    def get_link(self,google_id) :
        for results in self._queries.get_link(google_id=google_id) :
            return results[0]
        return None

    def get_categories_shortname(self,google_id=None) :
        if google_id is not None :
            return map(lambda line:line[0],self._queries.get_categories_shortname(google_id=google_id))
        return map(lambda line:line[0],self._queries.get_all_categories_shortname())

    def get_items_infos( self, include_categories, exclude_categories, include_search, exclude_search, sort_criterias ) :
        # print include_categories, exclude_categories, include_search, exclude_search
        def create_categorie_select(categories) :
            selectfromstatement = '''
                SELECT
                    distinct IC1.iditem
                FROM
                    Categorie as C1,
                    ItemCategorie as IC1
                '''
            fromaddon = ''',
                    Categorie as C%(n)d,
                    ItemCategorie as IC%(n)d
                '''
            wherestatement = '''
                WHERE
                '''
            wherejoinstatement = '''
                C%(n)d.idCategorie = IC%(n)d.idCategorie
                '''
            whereiditemstatement = '''
                IC1.idItem = IC%(n)d.idItem
                '''
            wherecategoriestatement = '''
                C%(n)d.shortname = '%(shortname)s'
                '''
            query = ''
            query += selectfromstatement
            for n in xrange(2,len(categories)+1) :
                query += fromaddon % { 'n' : n }
            where_clauses = []
            for n in xrange(1,len(categories)+1) :
                where_clauses.append(wherecategoriestatement % { 'n' : n, 'shortname':categories[n-1] })
                if n != 1 :
                    where_clauses.append(whereiditemstatement % { 'n' : n })
                where_clauses.append(wherejoinstatement % { 'n' : n })
            query += wherestatement
            query += ' AND '.join(where_clauses)

            # print "[%s]" % query
            return query

        where_clauses = []

        if len(include_categories) > 0 :
            subquery = create_categorie_select(include_categories)
            where_clauses.append('idItem in (%s)' % subquery)

        if len(exclude_categories) > 0 :
            for exclude_categorie in exclude_categories :
                subquery = create_categorie_select([exclude_categorie])
                where_clauses.append('idItem not in (%s)' % subquery)

        if len(include_search) > 0 :
            for pattern in include_search:
                where_clauses.append("((title LIKE '%%%s%%') or (content LIKE '%%%s%%'))" % (pattern,pattern))

        if len(exclude_search) > 0 :
            for pattern in exclude_search:
                where_clauses.append("(not((title LIKE '%%%s%%') or (content LIKE '%%%s%%')))" % (pattern,pattern))

        where_statement = ''
        if len(where_clauses) > 0 :
            where_statement="WHERE "+" AND ".join(where_clauses)
            # print where_statement

        # print sort_criterias
        sort_clauses = []
        criterias_translation = {
            'crawled' : 'crawled',
            'updated' : 'updated',
            'title' : 'title',
            'google_id' : 'google_id',
            'link' : 'link',
            }
        for criterias,asc in sort_criterias :
            if criterias in criterias_translation :
                sort_clauses.append(criterias_translation[criterias]+(asc and ' ' or ' DESC'))
        if len(sort_clauses)==0 :
            sort_clauses = ['crawled DESC']

        sort_statement = ','.join(sort_clauses)

        self._queries.create__tmpfiltereditem()
        self._queries.create_index__tmpfiltereditem_iditem()
        self._queries.insert__tmpfiltereditems(where=where_statement)
        items_infos = self._queries.get_filtereditems_infos(sort=sort_statement)
        self._items_categories = self._queries.get_filtereditems_categories()
        self._queries.drop__tmpfiltereditems()

        # items_infos = self._queries.get_items_infos(where=where_statement,sort=sort_statement)
        return items_infos

    def get_items_categories( self ) :
        return map( lambda line:line[0], self._items_categories )

    def get_actions(self) :
        return map( lambda line:{'google_id':line[0],'action_type':line[1],'categorie':line[2]}, self._queries.get_actions() )

    def clean_actions(self) :
        self.begin()
        self._queries.clean_actionitemcategorie()
        self.commit()

def test() :
    rd=ReaderDatabase('test.sqlite3')

    rd.start_add_session()
    rd.add_item(
        google_id='poide',
        original_id='praf',
        link='pido',
        content='panf',
        title='muk',
        author='glut',
        published=784512125454,
        updated=784512125454,
        crawled=784512125454003,
        )
    rd.add_item_categorie(
        google_id='poide',
        categorie_name='RUUU',
        categorie_shortname='R',
        )
    rd.add_item_categorie(
        google_id='poide',
        categorie_name='mof',
        categorie_shortname='m',
        )
    rd.add_action_item_categorie(
        google_id='poide',
        action_type='add',
        categorie_name='mof',
        categorie_shortname='m',
        )
    rd.add_action_item_categorie(
        google_id='poide',
        action_type='add',
        categorie_name='faa',
        categorie_shortname='f',
        )
    rd.add_action_item_categorie(
        google_id='poide',
        action_type='del',
        categorie_name='faa',
        categorie_shortname='f',
        )
    rd.stop_add_session()

if __name__ == '__main__' :
    test()
