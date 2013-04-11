import wx

class MenuProvider(object) :
    """This class should be used as mother class of child of wx.Frame.

        Typical usage is :
        class MyFrame (wx.Frame, MenuProvider) :
            pass

        This will provide 'MenuContent' to the wx.Frame

        It can be used to extend any class as long as it provide
        'SetMenuBar' and 'SetAcceleratorTable'.
        """
    def SetMenuContent( self, handler, menu_content ) :
        """Create a MenuBar and populate it with 'menu_content'.

            This method also Bind actions on the 'handler'.

            'menu_content' should look like a list of tuple.
            Each tuple define a menu_item.
            tuple contain :
            - A path separated by '/', with menu names (it can contain '&' char)
            - An action (which is a callable that take a wx Event)
            - A help string
            - A list of accels. Each 'accel' is a pair of flags and KeyCodes
              (see help for wx.AcceleratorEntry)

            you can specify 1,2,3 or 4 elements of the tuple.

            Using a '-' in a menu path mean that you want to use the same
            path from last line, except if the '-' is the last position, in
            which case, the menu item is a separator.

            Exemple :

                menu_content = [
                    ('&File',),
                    ('&File/&Preference', self.ChangePreference, 'Change preferences', [(wx.ACCEL_ALT, ord('P'))]),
                    ('-/&Quit', self.Quit, 'Exit', [(wx.ACCEL_CTRL, ord('Q'))]), # Same as ('&File/&Quit', ...
                    ('&Edit',),
                    ('-/&Copy', self.Copy, 'Copy', [(wx.ACCEL_CTRL|wx.ACCEL_ALT, ord('C'))]),

                    ]

                self.SetMenuContent(self,menu_content)
            """
        submenus = {}
        accels = []
        new_menu_content = []
        current_path = []

        self.__menubar = wx.MenuBar()

        for menu_tuple in menu_content :
            menu_item = self.__get_menu_item(menu_tuple,current_path)
            new_menu_content.append(menu_item)

            for index in range(1,len(menu_item['list'])) :
                submenu = '/'.join(menu_item['list'][:index])
                if submenu not in submenus :
                    submenus[submenu] = wx.Menu()

        for menu_item in new_menu_content :
            if (menu_item['parent'] in submenus) and (menu_item['parent'] != '') :
                if menu_item['id'] == -1 :
                    menu_item['id'] = wx.NewId()

                wxmenuitem = None

                # menu structure
                if menu_item['path'] in submenus :
                    wxmenuitem = wx.MenuItem(submenus[menu_item['parent']], menu_item['id'], menu_item['name'], menu_item['help'], subMenu=submenus[menu_item['path']] )
                else :
                    if menu_item['name'] == '-' :
                        wxmenuitem = wx.MenuItem(submenus[menu_item['parent']], wx.ID_SEPARATOR, menu_item['name'], menu_item['help'])
                    else :
                        wxmenuitem = wx.MenuItem(submenus[menu_item['parent']], menu_item['id'], menu_item['name'], menu_item['help'])

                if wxmenuitem is not None :
                    if menu_item['bitmap'] is not None :
                        wxmenuitem.SetBitmap(menu_item['bitmap'])
                    submenus[menu_item['parent']].AppendItem(wxmenuitem)

                # Bind action
                if menu_item['action'] != None :
                    handler.Bind(wx.EVT_MENU, menu_item['action'], id=menu_item['id'] )

                # add accels support
                for accel in menu_item['accels'] :
                    accels.append((accel[0], accel[1], menu_item['id']))

            if (menu_item['parent'] == '') and (menu_item['path'] in submenus) :
                self.__menubar.Append(submenus[menu_item['path']],menu_item['name'])

        self.SetMenuBar(self.__menubar)
        self.SetAcceleratorTable(wx.AcceleratorTable( accels ))

    def GetMenuByPath( self, path, menubar=None ) :
        if menubar is None :
            menubar = self.__menubar

        path_list = path.split( "/" )

        menu = None
        if len(path_list) > 0 :
            for topmenu,menulabel in menubar.GetMenus() :
                #print "        %s" % [topmenu,menulabel]
                if menulabel.replace('&','')  == path_list[0].replace('&','') :
                    path_list.pop(0)
                    menu = topmenu
                    while (len(path_list) > 0) and (menu is not None) and (menu.GetMenuItems() is not None) :
                        #print "        Need to find [%s]" % "/".join(path_list)
                        found = False
                        for item in list(menu.GetMenuItems()) :
                            #print "        %s" % [path_list[0].replace('&','') , item.GetLabel().replace('&','') ]
                            if path_list[0].replace('&','') == item.GetLabel().replace('&','') :
                                #print "        Found %s" % path_list[0]
                                path_list.pop(0)
                                menu = item.GetSubMenu()
                                found = True
                                #print menu
                                break
                        if not(found) :
                            break
                    break

        if len(path_list) > 0 :
            menu = None
        return menu


    def __get_menu_item(self, menu, current_path=[]) :
        menu_item = {}
        menu_item['path'] = menu[0]
        menu_item['list'] = []
        menu_list = menu_item['path'].split('/')

        for index_path in xrange(len(menu_list)) :
            if menu_list[index_path] == '-' and index_path<len(current_path) and index_path != len(menu_list)-1:
                menu_item['list'].append(current_path[index_path])
            else :
                menu_item['list'].append(menu_list[index_path])

        menu_item['path'] = '/'.join(menu_item['list'])
        menu_item['parent'] = '/'.join(menu_item['list'][:-1])
        menu_item['name'] = menu_item['list'][-1]

        menu_item['action'] = None
        if len(menu) > 1 :
            menu_item['action'] = menu[1]

        menu_item['help'] = ''
        if len(menu) > 2 :
            menu_item['help'] = menu[2]

        menu_item['accels'] = []
        if len(menu) > 3 :
            menu_item['accels'] = menu[3]

        menu_item['id'] = -1
        if len(menu) > 4 :
            menu_item['id'] = menu[4]

        menu_item['bitmap'] = None
        if len(menu) > 5 :
            menu_item['bitmap'] = menu[5]

        current_path[:] = menu_item['list']

        return menu_item

def test() :
    class MyFrame(wx.Frame,MenuProvider) :
        def __init__(self) :
            wx.Frame.__init__(self,None)
            menu_content = [
                ('&File',),
                ('&File/&Preference', lambda event:self.AddLog('Preference'), 'Change preferences', [(wx.ACCEL_ALT, ord('P'))]),
                ('-/&Quit', lambda event:self.Close(), 'Exit', [(wx.ACCEL_CTRL, ord('Q'))]), # Same as ('&File/&Quit', ...
                ('&Edit',),
                ('-/&Copy', lambda event:self.AddLog('Copy'), 'Copy', [(wx.ACCEL_CTRL|wx.ACCEL_ALT, ord('C'))]),
                ('-/&Paste', lambda event:self.AddLog('Paste'), 'Paste', [(wx.ACCEL_CTRL|wx.ACCEL_ALT, ord('V'))]),

                # You can add new item in File
                ('&File/-',), # Sep.
                ('&File/Test', lambda event:self.AddLog('Test'), 'Test'),
                ('-/-',), # Last dir + Sep.
                ('-/Subdir',),
                ('-/-/Item1',),
                ('-/-/Item2',),
                ('-/-/Item3',),
                ('-/-/Item3/Item31',),
                ('-/-/Item3/Item32',),
                ('-/-/Item4',),
                ('-/Item5',),
                ]
            self.SetMenuContent(self,menu_content)

            self._log = wx.TextCtrl( parent=self, style=wx.TE_MULTILINE, value='' )

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(self._log, 1, wx.ALL|wx.EXPAND, 0)
            self.SetSizer(sizer)

            print self.GetMenuByPath('&File')
            print self.GetMenuByPath('&Filo')
            print self.GetMenuByPath('&Filu')
            print self.GetMenuByPath('&File/&Preference')
            print self.GetMenuByPath('&Filo/&Preference')
            print self.GetMenuByPath('&Filu/&Preference')
            print self.GetMenuByPath('&File/&Preference/&Test')
            print self.GetMenuByPath('&Filo/&Preference/&Test')
            print self.GetMenuByPath('&Filu/&Preference/&Test')
            print self.GetMenuByPath('&Test')
            print self.GetMenuByPath('&Tost')
            print self.GetMenuByPath('&Tust')
            print self.GetMenuByPath('Edut')
            print self.GetMenuByPath('Edit')
            print self.GetMenuByPath('Edot')
            print self.GetMenuByPath('Edit/Paste')
            print self.GetMenuByPath('Edit/Subdir')
            print self.GetMenuByPath('File/Subdir')

        def AddLog(self,info) :
            self._log.SetValue(self._log.GetValue()+"\n"+info)

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    myframe = MyFrame()
    app.SetTopWindow(myframe)
    myframe.Show()
    app.MainLoop()

if __name__=='__main__' :
    test()
