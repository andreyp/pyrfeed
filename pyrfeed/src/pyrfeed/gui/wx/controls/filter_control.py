import wx

class GenericFilterControl(object) :
    def AppendValue(self,string) :
        self.SetValue(self.GetValue()+' '+string)

class FilterControlCombo(wx.ComboBox,GenericFilterControl) :
    def __init__(self,parent) :
        wx.ComboBox.__init__(self, parent, choices=[], style=wx.CB_DROPDOWN)

    def BindChange(self,action) :
        self.Bind(wx.EVT_COMBOBOX,action)
        self.Bind(wx.EVT_TEXT_ENTER,action)

    def ChangeDefaultFilter(self,filters) :
        filter_command = self.GetValue()
        self.Clear()
        for combo_filter_item in filters :
            self.Append(combo_filter_item)
        self.SetValue(filter_command)

    def ChangeDiffFilter(self,filters) :
        pass

class FilterControlSearch(wx.SearchCtrl,GenericFilterControl) :
    def __init__(self,parent) :
        wx.SearchCtrl.__init__( self, parent, style=wx.TE_PROCESS_ENTER )
        self.ChangeDefaultFilter([])
        self._action = None

    def BindChange(self,action) :
        self.Bind(wx.EVT_TEXT_ENTER,action)
        self._action = action

    def ChangeDefaultFilter(self,filters) :
        menu = wx.Menu()
        for combo_filter_item in filters :
            item_id = wx.NewId()
            menu.Append( item_id, combo_filter_item )
            self.Bind( wx.EVT_MENU, self.OnDefaultFilterSelected, id=item_id )
        self.SetMenu(menu)

    def OnDefaultFilterSelected(self,event) :
        self.SetValue(event.GetEventObject().GetLabel(event.GetId()))
        if self._action is not None :
            self._action()

    def ChangeDiffFilter(self,filters) :
        pass

class FilterControlPanelAbstract(wx.Panel,GenericFilterControl) :
    FilterClass = None
    def __init__(self,parent) :
        wx.Panel.__init__(self,parent)
        self._button_plus = wx.Button(self,label='+',style=wx.BU_EXACTFIT|wx.NO_BORDER)
        self._button_minus = wx.Button(self,label='-',style=wx.BU_EXACTFIT|wx.NO_BORDER)
        self._filter = self.FilterClass(self)

        self._diff_filters = []
        self._diff_modifier = ''

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self._button_plus, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        main_sizer.Add(self._button_minus, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        main_sizer.Add(self._filter, 1, wx.EXPAND, 0)
        main_sizer.SetSizeHints(self)
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)

        self.Layout()

        self._button_plus.Bind(wx.EVT_BUTTON,self.OnButtonPlusMinus)
        self._button_minus.Bind(wx.EVT_BUTTON,self.OnButtonPlusMinus)


    def ChangeDiffFilter(self,filters) :
        self._diff_filters = filters

    def OnButtonPlusMinus(self,event) :
        self._diff_modifier = ''
        if event.GetId() == self._button_minus.GetId() :
            self._diff_modifier = '-'
        menu = wx.Menu()
        for filter_item in self._diff_filters :
            item_id = wx.NewId()
            menu.Append( item_id, filter_item )
            self.Bind( wx.EVT_MENU, self.OnDiffFilterSelected, id=item_id )
        self.PopupMenu(menu)

    def OnDiffFilterSelected(self,event) :
        filter_value = self._filter.GetValue()
        menu_selected_value = event.GetEventObject().GetLabel(event.GetId())
        filter_value = filter_value + ' ' + self._diff_modifier + menu_selected_value
        self._filter.SetValue(filter_value)

        if self._action is not None :
            self._action()

    def BindChange(self,action) :
        self._filter.BindChange(action)
        self._action = action

    def ChangeDefaultFilter(self,filters) :
        self._filter.ChangeDefaultFilter(filters)

    def SetValue(self,string) :
        self._filter.SetValue(string)

    def GetValue(self) :
        return self._filter.GetValue()

    def SetFocus(self) :
        return self._filter.SetFocus()

class FilterControlPanelCombo(FilterControlPanelAbstract) :
    FilterClass = FilterControlCombo

class FilterControlPanelSearch(FilterControlPanelAbstract) :
    FilterClass = FilterControlSearch

FilterControl = FilterControlSearch
FilterControl = FilterControlCombo
FilterControl = FilterControlPanelCombo
FilterControl = FilterControlPanelSearch
