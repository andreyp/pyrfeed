from pyrfeed.gui.info import GuiInfo
from pyrfeed.tools.info_list import ElementInfoList
from pyrfeed.config import register_key

class _GuiInfoList(ElementInfoList) :
    BaseClass = GuiInfo

    def mainloop(self,config,rss_reader) :
        self._auto_register()

        name = config['gui']

        if name is None :
            name = self.get_default_info_name()

        while (name is not None) and (name in self) :
            # by default, there is no next gui.
            del config['gui/next']

            gui_info = self[name](config)
            gui_info.set_rss_reader(rss_reader)
            gui_info.start_application()
            gui_info = None

            name = config['gui/next']

        if name is not None :
            raise ValueError("Don't know Gui type [%s]" % name)

gui_info_list = _GuiInfoList()

register_key( 'gui', str, doc='The Gui name to use', default=None, advanced=True )
register_key( 'gui/next', str, doc='Next gui to launch when exiting', default=None, internal=True, advanced=True )

