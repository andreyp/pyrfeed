""" This package's goal is to provide a way to pyrfeed's rssreader to
register themself to rest of the world with a consistent interface """

from pyrfeed.tools.info import ElementInfo

class RssReaderInfo(ElementInfo) :
    name = 'RssReader'

    def __init__(self,config) :
        self._config = config

    def get_rss_reader(self) :
        ''' This method need to be overloaded '''
        raise Exception('This method never been called. You must overload it.')
