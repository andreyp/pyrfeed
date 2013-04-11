from pyrfeed.rss_reader.info import RssReaderInfo
from pyrfeed.tools.info_list import ElementInfoList
from pyrfeed.config import register_key

class _RssReaderInfoList(ElementInfoList) :
    BaseClass = RssReaderInfo

    def get_rss_reader(self,config) :
        self._auto_register()

        name = config['rssreader']

        if name is None :
            name = self.get_default_info_name()

        if (name is not None) and (name in self) :
            rss_reader = self[name](config).get_rss_reader()
        else :
            raise ValueError("Don't know RssReader type [%s]" % name)

        return rss_reader


rssreader_info_list = _RssReaderInfoList()

register_key( 'rssreader', str, doc='The RssReader to use', default=None, advanced=True )
