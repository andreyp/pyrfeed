""" This package's goal is to provide a way to pyrfeed's gui to
register themself to rest of the world with a consistent interface """
from pyrfeed.tools.info import ElementInfo

class GuiInfo(ElementInfo) :
    name = 'Gui'

    def __init__(self,config) :
        self._rss_reader = None
        self._config = config

    def set_rss_reader(self, rss_reader) :
        self._rss_reader = rss_reader

    def start_application(self) :
        self._start_application()

    def _start_application(self) :
        ''' This method need to be overloaded '''
        raise Exception('This method never been called. You must overload it.')
