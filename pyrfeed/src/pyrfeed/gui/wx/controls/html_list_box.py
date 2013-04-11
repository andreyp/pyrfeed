import wx
from pyrfeed.config import register_key

class RSSHtmlListBox(wx.HtmlListBox) :
    def __init__(self, parent, frame, config, *args, **kwargs) :
        self._choices=[]
        self._selected_items = set()
        kwargs['style'] = wx.WANTS_CHARS
        wx.HtmlListBox.__init__(self, parent, *args, **kwargs)
        self.SetItemCount(0)

        self._frame = frame

        self._config = config

        self._checked_pattern = '%s'
        self._unchecked_pattern = '%s'

        self._checked_pattern = "<font color='red'><font size='-1'>%s</font></font>"
        if self._config['wx/htmllistbox/usebold'] :
            self._checked_pattern = "<b>" + self._checked_pattern + "</b>"
        self._unchecked_pattern = "<font size='-1'>%s</font>"

        if self._config['wx/htmllistbox/useimage'] :
            self._checked_pattern = "<img src='../res/checked.png'>&nbsp;" + self._checked_pattern
            self._unchecked_pattern = "<img src='../res/unchecked.png'>&nbsp;" + self._unchecked_pattern
            
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.OnDClick)

    def Create(self, *args, **kwargs) :
        self.SetChoices()

    def ClearChoices(self) :
        self.SetChoices()

    def SetChoices(self, choices=None, selected_choices=None) :
        self.Clear()
        self.Refresh()

        if choices == None :
            self._choices = []
        else :
            self._choices = list(choices)

        self._selected_items = set()
        if selected_choices != None :
            for index in xrange(len(self._choices)) :
                if selected_choices[index] :
                    self._selected_items.add(index)

        self.SetItemCount(len(self._choices))

    def Append(self, string, selected=False) :
        if selected :
            self._selected_items.add(len(self._choices))
        self._choices.append(string)
        self.SetItemCount(len(self._choices))

    def GetSelectedTextColour(self, color) :
        pos = self.GetSelection()
        if pos in self._selected_items :
            return color.Set(0xff,0x00,0x00)
        return color.Set(0x00,0xff,0x00)

    def OnGetItem(self, n) :
        if 0 <= n < len(self._choices) :
            item_content = self._choices[n]
            if n in self._selected_items :
                item_content = self._checked_pattern % item_content
            else :
                item_content = self._unchecked_pattern % item_content
            return item_content
        return ""

    def SelectItem(self,event=None) :
        item_selected = self._frame.SelectItem(self.GetSelection())
        if item_selected :
            self._selected_items.add(self.GetSelection())
        else :
            self._selected_items.remove(self.GetSelection())
        self.RefreshAll()

    def SelectItemNext(self,event=None) :
        item_selected = self._frame.SelectItem(self.GetSelection())
        if item_selected :
            self._selected_items.add(self.GetSelection())
        else :
            self._selected_items.remove(self.GetSelection())
        self.Next(event)
        self.RefreshAll()

    def Prev(self,event=None) :
        self._frame.OnPrevItem()

    def Next(self,event=None) :
        self._frame.OnNextItem()

    def GetSelectedItems(self) :
        if len(self._selected_items) == 0 :
            self.SelectItem()
        return list(self._selected_items)
        
    def OnDClick(self,event=None) :
        self.SelectItem()


register_key( 'wx/htmllistbox/useimage', bool, doc='Use image for check/uncheck', default=True, advanced=True )
register_key( 'wx/htmllistbox/usebold', bool, doc='Use bold for check', default=True, advanced=True )

