from GoogleReader import CONST

from pyrfeed.rss_reader.google_base import GoogleBase
from pyrfeed.rss_reader.info import RssReaderInfo
from pyrfeed.rss_reader.page_selector import PageSelector
from pyrfeed.config import register_key

class GoogleDirect(PageSelector,GoogleBase) :
    def __init__(self,config) :
        GoogleBase.__init__(self,config)
        PageSelector.__init__(self,config)

    def synchro(self) :
        self.reload()

    def reload(self) :
        get_feed_args = self.get_feed_args_default()

        xmlfeed = self._get_googlereader().get_feed(**get_feed_args)
        self._items = list(xmlfeed.get_entries())
        self._filtered_items = self._items

        self._categorie_by_name = {}
        self._categorie_by_name_with_current_filter = {}
        self._name_by_categorie = {}
        self._google_id_by_categorie = {}
        for item in self._items :
            for categorie in item['sources'].keys()+item['categories'].keys() :
                name = self.get_shortname(categorie)
                self._categorie_by_name[name] = categorie
                self._name_by_categorie[categorie] = name
                if categorie not in self._google_id_by_categorie :
                    self._google_id_by_categorie[categorie] = []
                self._google_id_by_categorie[categorie].append(item['google_id'])
        self.reload_titles()
        self._is_loaded = True

    def load(self) :
        if not(self._is_loaded) :
            self.reload()

    def reload_titles(self) :
        filter_command = self._filter
        if filter_command and filter_command!='' :
            filter_list = filter(len,filter_command.lower().split(' '))
            def simple_filter(item) :
                need_item = True
                for filter_element in filter_list :
                    need_item_with_this_filter = False
                    need_mode = True
                    if filter_element.startswith('-') :
                        need_mode = False
                        filter_element = filter_element[1:]
                    if filter_element.startswith('+') :
                        filter_element = filter_element[1:]
                    if filter_element in self._categorie_by_name :
                        need_item_with_this_filter |= item['google_id'] in self._google_id_by_categorie[self._categorie_by_name[filter_element]]
                    else :
                        if not(need_item_with_this_filter) :
                            need_item_with_this_filter = filter_element in item['title'].lower()
                        if not(need_item_with_this_filter) :
                            need_item_with_this_filter = filter_element in item['content'].lower()

                    if need_mode :
                        need_item &= need_item_with_this_filter
                    else :
                        need_item &= not(need_item_with_this_filter)
                return need_item
            self._filtered_items = filter(simple_filter,self._items)
        else :
            self._filtered_items = self._items
        self._categorie_by_name_with_current_filter = {}
        for item in self._filtered_items :
            for categorie in item['sources'].keys()+item['categories'].keys() :
                self._categorie_by_name_with_current_filter[ self._name_by_categorie[categorie] ] = categorie
        self.set_items(lambda x:x['title'],self._filtered_items)

    def set_filter(self,filter_command) :
        GoogleBase.set_filter(self,filter_command)
        self.reload_titles()

    def get_title(self, position) :
        if position < 0 or position >= len(self._filtered_items) :
            return ''
        return self._filtered_items[position]['title']

    def get_content(self, position) :
        if position < 0 or position >= len(self._filtered_items) :
            return ''
        return self._format_content( self._filtered_items[position]['content'], self._filtered_items[position]['title'], self._filtered_items[position]['published'] )

    def get_link(self, position) :
        if position < 0 or position >= len(self._filtered_items) :
            return None
        return self._filtered_items[position]['link']

    def get_categories(self, position) :
        if position < 0 or position >= len(self._filtered_items) :
            return []
        categories = map(self._name_by_categorie.__getitem__,self._filtered_items[position]['sources'].keys()+self._filtered_items[position]['categories'].keys())
        categories.sort()
        return categories

    def get_filters(self) :
        filters = self._categorie_by_name.keys()
        filters.sort()
        return filters

    def get_filters_diff(self) :
        filters = self._categorie_by_name_with_current_filter.keys()
        filters.sort()
        return filters

    def mark_as_read( self, positions ) :
        for position in positions :
            self._get_googlereader().set_read(self._filtered_items[position]['google_id'])

    def mark_as_unread( self, positions ) :
        for position in positions :
            self._get_googlereader().set_unread(self._filtered_items[position]['google_id'])

    def add_star( self, positions ) :
        for position in positions :
            self._get_googlereader().add_star(self._filtered_items[position]['google_id'])

    def del_star( self, positions ) :
        for position in positions :
            self._get_googlereader().del_star(self._filtered_items[position]['google_id'])

    def add_public( self, positions ) :
        for position in positions :
            self._get_googlereader().add_public(self._filtered_items[position]['google_id'])

    def del_public( self, positions ) :
        for position in positions :
            self._get_googlereader().del_public(self._filtered_items[position]['google_id'])

    def add_label( self, positions, label ) :
        if label.startswith('label:') :
            label = label[len('label:'):]
        for position in positions :
            self._get_googlereader().add_label(self._filtered_items[position]['google_id'],labelname=label)

    def del_label( self, positions, label ) :
        if label.startswith('label:') :
            label = label[len('label:'):]
        for position in positions :
            self._get_googlereader().del_label(self._filtered_items[position]['google_id'],labelname=label)

class RssReaderInfoGoogleDirect(RssReaderInfo) :
    names = ['Google','direct']
    priority = 60
    def get_rss_reader(self) :
        return GoogleDirect(self._config)
