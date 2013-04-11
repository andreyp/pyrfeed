import wx.aui
from pyrfeed.gui.wx.reader_frame import RSSReaderFrame
from pyrfeed.gui.wx.reader_frame import GuiInfoWx

class RSSReaderFrameAui(RSSReaderFrame):
    def _create_components(self):
        self._create_tool_bar()
        self._create_combo_filter( self )
        self._create_listbox_title( self )
        self._create_window_html( self )
        self._create_listbox_categories( self )
        self._create_status_bar( self )

    def _do_layout(self):
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        sashposition = self._config['wx/sashposition']

        self._mgr.AddPane(
            self._window_html,
            wx.aui.AuiPaneInfo().Name("_window_html").Caption("Content").CenterPane().CloseButton(False).MaximizeButton(True),
            )

        self._mgr.AddPane(
            self._listbox_categories,
            wx.aui.AuiPaneInfo().Name("_listbox_categories").Caption("Categories").Bottom().CloseButton(False).MaximizeButton(True),
            )

        self._mgr.AddPane(
            self._listbox_title,
            wx.aui.AuiPaneInfo().Name("_listbox_title").Caption("Item list").Left().CloseButton(False).MaximizeButton(True).BestSize(wx.Size(sashposition,200)).MinSize(wx.Size(sashposition,200)),
            )

        self._mgr.AddPane(
            self._combo_filter,
            wx.aui.AuiPaneInfo().Name("_combo_filter").Caption("Filters").Top().CloseButton(False).MaximizeButton(False),
            )

        flags = self._mgr.GetFlags()
        self._mgr.Update()
        flags |= wx.aui.AUI_MGR_TRANSPARENT_HINT
        flags &= ~wx.aui.AUI_MGR_HINT_FADE
        flags &= ~wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT
        flags &= ~wx.aui.AUI_MGR_RECTANGLE_HINT
        self._mgr.SetFlags(flags)

        self._mgr.GetArtProvider().SetColor(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR, wx.Colour(0xff,0xff,0xff))
        self._mgr.GetArtProvider().SetColor(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR, wx.Colour(0xaa,0xaa,0xaa))


class GuiInfoWxAui(GuiInfoWx) :
    names = ['aui','wxaui']
    priority = 80
    ui_name = 'Aui wx interface'
    RSSReaderFrameClass = RSSReaderFrameAui

