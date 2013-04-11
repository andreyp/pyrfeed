import wx
from pyrfeed.gui.wx.reader_frame import RSSReaderFrame
from pyrfeed.gui.wx.reader_frame import GuiInfoWx

class RSSReaderFrameClassic(RSSReaderFrame) :
    def _create_components(self):
        self._create_tool_bar()
        self._splitter_window = wx.SplitterWindow(self, style=wx.SP_3D|wx.SP_NOBORDER|wx.SP_ARROW_KEYS|wx.SP_WRAP)
        self._create_combo_filter( self )
        self._create_listbox_title( self._splitter_window )
        self._panel_html = wx.Panel( self._splitter_window )
        self._create_window_html( self._panel_html )
        self._create_listbox_categories( self._panel_html )
        self._create_status_bar( self )

    def _do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._combo_filter, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self._splitter_window.SplitVertically(self._listbox_title, self._panel_html)
        main_sizer.Add(self._splitter_window, 1, wx.EXPAND, 0)
        main_sizer.SetSizeHints(self)
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)

        detail_sizer = wx.BoxSizer(wx.VERTICAL)
        detail_sizer.Add(self._window_html, 4, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        detail_sizer.Add(self._listbox_categories, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        detail_sizer.Fit(self._panel_html)
        detail_sizer.SetSizeHints(self._panel_html)
        self._panel_html.SetAutoLayout(True)
        self._panel_html.SetSizer(detail_sizer)

        self.Layout()

        self._splitter_window.SetMinimumPaneSize(60)
        # self.SetSize((800,600))

        self._splitter_window.SetSashPosition(self._config['wx/sashposition'])

class GuiInfoWxClassic(GuiInfoWx) :
    names = ['wx','wxclassic']
    priority = 70
    ui_name = None
    ui_name = 'Classical wx interface'
    RSSReaderFrameClass = RSSReaderFrameClassic

