from GoogleReader import CONST
from pyrfeed.database.reader_database import ReaderDatabase
from pyrfeed.rss_reader.info import RssReaderInfo
from pyrfeed.rss_reader.google_base import GoogleBase
from pyrfeed.rss_reader.page_selector import PageSelector
from pyrfeed.config import register_key

class GoogleCache(PageSelector,GoogleBase) :
    def __init__(self,config) :
        GoogleBase.__init__(self,config)
        PageSelector.__init__(self,config)

        database_name = self._config['database']
        self._is_loaded = False
        self._google_id_by_position = {}
        self._database = ReaderDatabase(database_name,debug=self._config['database-debug'])

    def synchro(self) :
        # First, we synchronize categories
        for action in self._database.get_actions() :
            # print action
            if action['action_type'] == 'add' :
                result = self._get_googlereader().edit_tag( entry=action['google_id'], add=action['categorie'] )
            if action['action_type'] == 'del' :
                result = self._get_googlereader().edit_tag( entry=action['google_id'], remove=action['categorie'] )
            if result != 'OK' :
                return 'There was a problem when sending changes to Google Reader.'

        # Here, all changes has been commited to Google Reader. Let's clean up a bit..
        self._database.clean_actions()

        continue_synchro = True
        get_feed_args = self.get_feed_args_default()
        max_count = get_feed_args['count']

        while continue_synchro and ('continuation' not in get_feed_args or get_feed_args['continuation'] is not None) and max_count>0:
            get_feed_args['count'] = min(max_count,1000)

            xmlfeed = self._get_googlereader().get_feed(**get_feed_args)

            continue_synchro = False
            self._database.start_add_session()
            for item in xmlfeed.get_entries() :
                continue_synchro = True
                # print "--[%s]--" % item['title'].encode('ascii','replace')
                self._database.add_item(
                    google_id=item['google_id'].encode('utf-8'),
                    original_id=item['original_id'].encode('utf-8'),
                    link=item['link'].encode('utf-8'),
                    content=item['content'].encode('utf-8'),
                    title=item['title'].encode('utf-8'),
                    author=item['author'].encode('utf-8'),
                    published=item['published'],
                    updated=item['updated'],
                    crawled=item['crawled'],
                    )
                for source in item['sources'] :
                    shortname = self.get_shortname(source)
                    self._database.add_item_categorie(
                        google_id=item['google_id'].encode('utf-8'),
                        categorie_name=source.encode('utf-8'),
                        categorie_shortname=shortname.encode('utf-8'),
                        )
                for categorie in item['categories'] :
                    shortname = self.get_shortname(categorie)
                    self._database.add_item_categorie(
                        google_id=item['google_id'].encode('utf-8'),
                        categorie_name=categorie.encode('utf-8'),
                        categorie_shortname=shortname.encode('utf-8'),
                        )
                max_count -= 1
            self._database.stop_add_session()
            # print "(%s)" % xmlfeed.get_continuation()
            get_feed_args['continuation'] = xmlfeed.get_continuation()
        self.reload_titles()
        self._is_loaded = True

    def reload(self) :
        self.reload_titles()
        self._is_loaded = True

    def load(self) :
        if not(self._is_loaded) :
            self.reload()

    def reload_titles(self) :
        filter_command = self._filter

        self._google_id_by_position = {}

        if filter_command is None :
            filter_command = ''

        filter_list = filter(len,filter_command.split(' '))
        include_categories = []
        exclude_categories = []
        include_search = []
        exclude_search = []
        sort_criterias = []
        filters_shortname = self._database.get_categories_shortname()
        for filter_element in filter_list :
            include = True
            if filter_element.startswith('-') :
                include = False
                filter_element = filter_element[1:]
            if filter_element.startswith('+') :
                filter_element = filter_element[1:]
            if filter_element in filters_shortname :
                if include :
                    include_categories.append(filter_element)
                else :
                    exclude_categories.append(filter_element)
            elif filter_element.startswith(self._SORT_PREFIXE) :
                # if include != True, sort desc
                sort_criterias.append( (filter_element[len(self._SORT_PREFIXE):], include) )
            else :
                if include :
                    include_search.append(filter_element)
                else :
                    exclude_search.append(filter_element)

        position = 0
        titles = []
        for items_info in self._database.get_items_infos(include_categories,exclude_categories,include_search,exclude_search,sort_criterias) :
            self._google_id_by_position[position] = items_info[0]
            titles.append(items_info[1])
            position += 1

        self.set_items(titles)

    def set_filter(self,filter_command) :
        GoogleBase.set_filter(self,filter_command)
        self.reload_titles()

    def get_title(self, position) :
        if position not in self._google_id_by_position :
            return ''
        content = self._database.get_content(google_id=self._google_id_by_position[position])
        return content['title']

    def get_content(self, position) :
        if position not in self._google_id_by_position :
            return ''
        content = self._database.get_content(google_id=self._google_id_by_position[position])
        return self._format_content( content['content'], content['title'], content['published'] )

    def get_link(self, position) :
        if position not in self._google_id_by_position :
            return ''
        return self._database.get_link(google_id=self._google_id_by_position[position])

    def get_categories(self, position) :
        if position not in self._google_id_by_position :
            return ''
        return self._database.get_categories_shortname(google_id=self._google_id_by_position[position])

    def get_filters(self) :
        filters = self._database.get_categories_shortname()
        filters.sort()
        return filters

    def get_filters_diff(self) :
        filters = self._database.get_items_categories()
        filters.sort()
        return filters

    def mark_as_read( self, positions ) :
        self.edit_tag( positions=positions, add=CONST.ATOM_STATE_READ, remove=CONST.ATOM_STATE_UNREAD )

    def mark_as_unread( self, positions ) :
        self.edit_tag( positions=positions, add=CONST.ATOM_STATE_UNREAD, remove=CONST.ATOM_STATE_READ )

    def add_star( self, positions ) :
        self.edit_tag( positions=positions, add=CONST.ATOM_STATE_STARRED )

    def del_star( self, positions ) :
        self.edit_tag( positions=positions, remove=CONST.ATOM_STATE_STARRED )

    def add_public( self, positions ) :
        self.edit_tag( positions=positions, add=CONST.ATOM_STATE_BROADCAST )

    def del_public( self, positions ) :
        self.edit_tag( positions=positions, remove=CONST.ATOM_STATE_BROADCAST )

    def add_label( self, positions, labelname ) :
        self.edit_tag( positions=positions, add=CONST.ATOM_PREFIXE_LABEL+labelname )

    def del_label( self, positions, labelname ) :
        self.edit_tag( positions=positions, remove=CONST.ATOM_PREFIXE_LABEL+labelname )

    def edit_tag( self, positions, add=None, remove=None ) :
        self._database.start_add_session()
        for position in positions :
            if position in self._google_id_by_position :
                if add is not None :
                    self._database.add_action_item_categorie(
                        google_id=self._google_id_by_position[position],
                        action_type='add',
                        categorie_name=add,
                        categorie_shortname=self.get_shortname(add),
                        )
                if remove is not None :
                    self._database.add_action_item_categorie(
                        google_id=self._google_id_by_position[position],
                        action_type='del',
                        categorie_name=remove,
                        categorie_shortname=self.get_shortname(remove),
                        )
        self._database.stop_add_session()

class RssReaderInfoGoogleCache(RssReaderInfo) :
    names = ['GoogleCache','db']
    priority = 70
    def get_rss_reader(self) :
        return GoogleCache(self._config)
    def get_doc(self) :
        return ""

register_key( 'database', str, doc='The database name for GoogleCache mode', default='reader.sqlite3' )
register_key( 'database-debug', bool, doc='Database will log every sql query if true. Developers only.', default=0, advanced=True )

