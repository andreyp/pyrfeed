from GoogleReader import CONST
from GoogleReader import GoogleReader

from pyrfeed import __version__ as pyrfeed_version
from pyrfeed.config import register_key

import time

class GoogleBase(object) :
    _SORT_PREFIXE = 'sort:'

    def __init__(self,config) :
        self._config = config
        self._filter = self._config['filter']
        self.__googlereader = None

    def _get_googlereader(self) :
        if self.__googlereader is None :
            login_info = { 'login' : self._config['login'], 'passwd' : self._config['passwd'] }
            http_proxy = None

            proxy_host = self._config['proxy_host']
            if (proxy_host is not None) and (proxy_host!='') :
                http_proxy = (proxy_host,"%s" % self._config['proxy_port'])

            self.__googlereader = GoogleReader(agent='pyrfeed-framework-contact:pyrfeed_at_gmail/%s' % pyrfeed_version,http_proxy=http_proxy)
            self.__googlereader.identify(**login_info)
            if not(self.__googlereader.login()) :
                raise Exception("Can't login")
        return self.__googlereader

    def get_shortname(self,longname) :
        if longname.startswith(CONST.ATOM_PREFIXE_LABEL) :
            shortname = 'label:' + longname[len(CONST.ATOM_PREFIXE_LABEL):]
        elif longname.startswith(CONST.ATOM_PREFIXE_STATE_GOOGLE) :
            shortname = 'state:' + longname[len(CONST.ATOM_PREFIXE_STATE_GOOGLE):]
        elif longname.startswith(CONST.ATOM_GET_FEED) :
            shortname = 'feed:' + longname[len(CONST.ATOM_GET_FEED):]
        else :
            shortname = longname
        return shortname

    def get_longname(self,shortname) :
        if shortname.startswith('label:') :
            longname = CONST.ATOM_PREFIXE_LABEL + shortname[len('label:'):]
        elif shortname.startswith('state:') :
            longname = CONST.ATOM_PREFIXE_STATE_GOOGLE + shortname[len('state:'):]
        elif longname.startswith('feed:') :
            shortname = CONST.ATOM_GET_FEED + longname[len('feed:'):]
        else :
            longname = shortname
        return longname

    def get_filter(self) :
        return self._filter

    def set_filter(self,filter_command) :
        self._filter = filter_command

    def _format_content(self,content,title,date) :
        fdate = time.strftime(self._config['datefmt'],time.gmtime( date ))
        return "<h1>%s</h1><p align='right'><font size='-1'>%s</font></p><br align='left'>%s" % (title,fdate,content)

    def get_feed_args_default(self) :
        """Get the default arguments for get_feed, based on current configuration"""

        get_feed_args = {}
        max_count = self._config['google/max_count']

        if not(self._config['google/include_read']) :
            get_feed_args['exclude_target'] = CONST.ATOM_STATE_READ
        if self._config['url'] :
            get_feed_args['url'] = self._config['url']
        if self._config['label'] :
            get_feed_args['feed'] = CONST.ATOM_PREFIXE_LABEL + self._config['label']
        elif self._config['feed'] :
            get_feed_args['feed'] = self._config['feed']

        get_feed_args['count'] = max_count

        return get_feed_args

register_key( 'google/max_count', int, doc='The size of the feed to fetch from google', default=200 )
register_key( 'google/include_read', bool, doc='If true, will fetch all items, otherwise will fetch only unread ones', default=True, advanced=True )
register_key( 'url', str, doc='The url of the google feed to fetch', default=None, advanced=True )
register_key( 'label', str, doc='The label of google reader to fetch', default=None, advanced=True )
register_key( 'feed', str, doc='The feed to fetch on google', default=None, advanced=True )

register_key( 'filter', str, doc='the filter at start to search items', default='', advanced=True )
register_key( 'login', str, doc='Google login', default=None )
register_key( 'passwd', str, doc='Google password', default=None )

register_key( 'datefmt', str, doc='the strftime format for date', default='%Y-%m-%d %H:%M:%S', advanced=True )
register_key( 'proxy_host', str, doc='Host for proxy', default='' )
register_key( 'proxy_port', int, doc='Port for proxy', default=3128 )
