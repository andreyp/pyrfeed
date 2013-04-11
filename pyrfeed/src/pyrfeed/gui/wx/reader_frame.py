#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import os
import sys

import wx
import webbrowser
from wxMenuProvider import MenuProvider

from pyrfeed.gui.wx.controls.html_window import HtmlClasses, HTML_SIMPLE, HTML_COMPLEX
from pyrfeed.gui.wx.controls.html_list_box import RSSHtmlListBox
from pyrfeed.gui.wx.controls.filter_control import FilterControl

from pyrfeed.gui.info import GuiInfo
from pyrfeed.gui.info_list import gui_info_list
from pyrfeed.config import register_key

from pyrfeed import __version__ as pyrfeed_version

class RSSReaderFrame(wx.Frame,MenuProvider):
    def __init__(self, config, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._config = config

        self.Maximize(True)

        self._create_components()
        self._set_properties()
        self._do_layout()
        self._bind_events()

        self._rss_reader = None
        self._loading_page = False

        self._clipboard = wx.Clipboard()

        self._labels_in_menus = []
        self._labels_by_add_id = {}
        self._labels_by_del_id = {}

        self._interface_name_by_menu_id = {}

        self._busy = None
        self._current_status = None
        
        self.SetNextGuiMenu()

    def _create_tool_bar( self ) :
        self._tool_bar = self.CreateToolBar(style=wx.TB_HORIZONTAL|wx.TB_FLAT)

    def _create_combo_filter( self, parent ) :
        self._combo_filter = FilterControl(parent)

    def _create_listbox_title( self, parent ) :
        self._listbox_title = RSSHtmlListBox(parent, self, self._config, style=wx.LB_EXTENDED)

    def _create_window_html( self, parent ) :
        htmlwindow_name = self._config['wx/htmlwindow']
        pos = None
        if htmlwindow_name == 'simple' :
            pos = HTML_SIMPLE
        elif htmlwindow_name == 'complex' :
            pos = HTML_COMPLEX
        else :
            pos = -1
        self._window_html = HtmlClasses[pos]['class'](parent)
        self._window_html.BindChangeStatus(self.SetTemporaryStatus)

    def _create_listbox_categories( self, parent ) :
        self._listbox_categories = wx.ListBox(parent, style=wx.LB_EXTENDED|wx.LB_SORT)

    def _create_status_bar( self, parent ) :
        self._status_bar = wx.StatusBar(parent)

    def _get_bitmap( self, name ) :
        pathname = os.path.join('..','res','toolbar',name+'.png')
        if not(os.path.exists(pathname)) :
            pathname = os.path.join('..','res','toolbar','none'+'.png')
        return wx.Bitmap(pathname)

    def _set_properties(self) :
        self._status_bar.SetFieldsCount(2)
        self.SetStatusBar(self._status_bar)

        self._events = {
            'SYNCHRO' : {
                'action' : self.Synchro,
                'bitmap' : 'synchro',
                'accels' : [
                    ('Ctrl','Shift','S'),
                    ('Ctrl','S'),
                    ('Shift','F5'),
                    ],
                'help' : 'Synchronize with server',
                },
            'RELOAD' : {
                'action' : self.Reload,
                'bitmap' : 'reload',
                'accels' : [
                    ('Ctrl','Shift','R'),
                    ('Ctrl','R'),
                    ('F5',),
                    ],
                'help' : 'Reload entry list',
                },
            'QUIT' : {
                'action' : self.Quit,
                'bitmap' : 'quit',
                'help' : 'Quit',
                },
            'SELECT' : {
                'action' : self._listbox_title.SelectItem,
                'bitmap' : 'select',
                'accels' : [
                    ('Ctrl','Shift','Y'),
                    ('Ctrl','SPACE'),
                    ('Ctrl','Shift','SPACE'),
                    ],
                'help' : 'Select current item',
                },
            'SELECTNEXT' : {
                'action' : self._listbox_title.SelectItemNext,
                'bitmap' : 'selectnext',
                'accels' : [
                    ('Ctrl','Shift','I'),
                    ('INSERT',),
                    ],
                'help' : 'Select current item and go to next one',
                },
            'OPENLINK' : {
                'action' : self.OpenInWebBrowser,
                'bitmap' : 'openlink',
                'accels' : [
                    ('Ctrl','Shift','O'),
                    ('Ctrl','RETURN'),
                    ],
                'help' : 'Open current item in web browser',
                },
            'OPENLINKS' : {
                'action' : self.OpenMultiInWebBrowser,
                'bitmap' : 'openlinks',
                'accels' : [
                    ('Ctrl','Alt','Shift','O'),
                    ],
                'help' : 'Open all selected items in web browser',
                },
            'PREVIOUS' : {
                'action' : self._listbox_title.Prev,
                'bitmap' : 'previous',
                'accels' : [
                    ('Ctrl','Shift','K'),
                    ],
                'help' : 'Previous item',
                },
            'NEXT' : {
                'action' : self._listbox_title.Next,
                'bitmap' : 'next',
                'accels' : [
                    ('Ctrl','Shift','J'),
                    ],
                'help' : 'Next item',
                },
            'PREVIOUSPAGE' : {
                'action' : self.OnPreviousPage,
                'bitmap' : 'previouspage',
                'accels' : [
                    ('Ctrl','Shift','L'),
                    ],
                'help' : 'Previous page',
                },
            'NEXTPAGE' : {
                'action' : self.OnNextPage,
                'bitmap' : 'nextpage',
                'accels' : [
                    ('Ctrl','Shift','H'),
                    ],
                'help' : 'Next page',
                },
            'MARKASREAD' : {
                'action' : self.MarkAsRead,
                'bitmap' : 'markasread',
                'accels' : [
                    ('Ctrl','Shift','M'),
                    ],
                'help' : 'Mark selected items as read',
                },
            'MARKASUNREAD' : {
                'action' : self.MarkAsUnread,
                'bitmap' : 'markasunread',
                'accels' : [
                    ('Ctrl','Shift','U'),
                    ],
                'help' : 'Mark selected items as unread',
                },
            'ADDSTAR' : {
                'action' : self.AddStar,
                'bitmap' : 'addstar',
                'accels' : [
                    ],
                'help' : 'Add star to selected items',
                },
            'DELSTAR' : {
                'action' : self.DelStar,
                'bitmap' : 'delstar',
                'accels' : [
                    ],
                'help' : 'Del star to selected items',
                },
            'ADDPUBLIC'      : {
                'action' : self.AddPublic,
                'bitmap' : 'addpublic',
                'accels' : [
                    ],
                'help' : 'Add public status to selected items',
                },
            'DELPUBLIC' : {
                'action' : self.DelPublic,
                'bitmap' : 'delpublic',
                'accels' : [
                    ],
                'help' : 'Del public status to selected items',
                },
            'ADDFILTER' : {
                'action' : self.FocusFilter,
                'bitmap' : '',
                'accels' : [
                    ('Alt','SPACE'),
                    ],
                'help' : 'Set focus to filter component',
                },
            'VIEWALL' : {
                'action' : self.ViewAllItems,
                # 'bitmap' : 'viewall',
                'accels' : [
                    ],
                'help' : 'View all items (no filters at all)',
                },
            'VIEWUNREAD' : {
                'action' : self.ViewUnreadItems,
                # 'bitmap' : 'viewunread',
                'accels' : [
                    ],
                'help' : 'View all unread items (from all feeds)',
                },
            'FILTERUNREAD' : {
                'action' : self.FilterUnreadItems,
                # 'bitmap' : 'viewunread',
                'accels' : [
                    ],
                'help' : 'View all unread items (from current filters)',
                },
            'SORTBYTIME' : {
                'action' : self.SortByTime,
                # 'bitmap' : 'sortbytime',
                'accels' : [
                    ],
                'help' : 'Sort current items by crawled time (ascending)',
                },
            'SORTBYTIMEDESC' : {
                'action' : self.ViewUnreadItems,
                # 'bitmap' : 'sortbytimedesc',
                'accels' : [
                    ],
                'help' : 'Sort current items by crawled time (descending)',
                },
            'SORTBYTITLE' : {
                'action' : self.SortByTitle,
                # 'bitmap' : 'sortbytitle',
                'accels' : [
                    ],
                'help' : 'Sort current items by title (ascending)',
                },
            'SORTBYTITLEDESC' : {
                'action' : self.SortByTitleDesc,
                # 'bitmap' : 'sortbytitledesc',
                'accels' : [
                    ],
                'help' : 'Sort current items by title (descending)',
                },
            'HELPDOC' : {
                'action' : self.OnHelpDoc,
                'bitmap' : 'helpdoc',
                'accels' : [
                    ('F1',),
                    ],
                'help' : 'Read online doc (not much now)',
                },
            'HELPBUG' : {
                'action' : self.OnHelpIssues,
                'bitmap' : 'helpbug',
                'accels' : [
                    ],
                'help' : 'Submit a bug',
                },
            'HELPNEWFEATURE' : {
                'action' : self.OnHelpIssues,
                'bitmap' : 'helpfeature',
                'accels' : [
                    ],
                'help' : 'Request new feature',
                },
            'HELPSITE' : {
                'action' : self.OnHelpWebSite,
                'bitmap' : 'helpsite',
                'accels' : [
                    ],
                'help' : 'Web site',
                },
            'ABOUT' : {
                'action' : self.OnAbout,
                'bitmap' : 'about',
                'accels' : [
                    ('Ctrl','F1'),
                    ],
                'help' : 'About pyrfeed',
                },

            }

        for event_name in self._events :
            event = self._events[event_name]
            if 'action' not in event :
                event['action'] = None
            if 'bitmap' not in event :
                event['bitmap'] = 'none'
            if event['bitmap'] == '' :
                event['bitmap'] = 'none'
            if 'accels' not in event :
                event['accels'] = []
            if 'help' not in event :
                event['help'] = ''
            if 'id' not in event :
                event['id'] = wx.NewId()

        menu_order = [
            ('&File',                                       ),
            ('-/&Synchro',                                  'SYNCHRO' ),
            ('-/&Reload',                                   'RELOAD' ),
            ('-/-',                                         ),
            ('-/S&witch interface',                         ),
            ('-/-/-',                                       ),
            ('-/-',                                         ),
            ('-/&Quit',                                     'QUIT' ),
            ('&Edit',                                       ),
            ('-/&Select',                                   'SELECT' ),
            ('-/Select and goto ne&xt',                     'SELECTNEXT' ),
            ('-/-',                                         ),
            ('-/&Open link',                                'OPENLINK' ),
            ('-/&Open links',                               'OPENLINKS' ),
            ('-/-',                                         ),
            ('-/&Previous',                                 'PREVIOUS' ),
            ('-/&Next',                                     'NEXT' ),
            ('-/P&age',                                     ),
            ('-/P&age/&Previous',                           'PREVIOUSPAGE' ),
            ('-/P&age/&Next',                               'NEXTPAGE' ),
            ('-/-',                                         ),
            ('-/Mark as &Read',                             'MARKASREAD' ),
            ('-/Mark as &Unread',                           'MARKASUNREAD' ),
            ('-/-',                                         ),
            ('-/Add Star',                                  'ADDSTAR' ),
            ('-/Del Star',                                  'DELSTAR' ),
            ('-/-',                                         ),
            ('-/Add Public',                                'ADDPUBLIC' ),
            ('-/Del Public',                                'DELPUBLIC' ),
            ('-/-',                                         ),
            ('-/Add &Label',                                ),
            ('-/-/-',                                       ),
            ('-/Del La&bel',                                ),
            ('-/-/-',                                       ),
            ('-/-',                                         ),
            ('-/Add &Filter',                               'ADDFILTER' ),
            ('&View',                                       ),
            ('-/View all items',                            'VIEWALL'),
            ('-/View all unread items',                     'VIEWUNREAD'),
            ('-/-',                                         ),
            ('-/Filter unread items',                       'FILTERUNREAD'),
            ('-/-',                                         ),
            ('-/Sort by time',                              'SORTBYTIME'),
            ('-/Sort by time (desc.)',                      'SORTBYTIMEDESC'),
            ('-/Sort by title',                             'SORTBYTITLE'),
            ('-/Sort by title (desc.)',                     'SORTBYTITLEDESC'),
            ('&Help',                                       ),
            ('&Help/Online &Doc (not much now)',            'HELPDOC' ),
            ('&Help/Report a bug',                          'HELPBUG' ),
            ('&Help/Ask for new features',                  'HELPNEWFEATURE' ),
            ('&Help/Website',                               'HELPSITE' ),
            ('-/-',                                         ),
            ('&Help/About',                                 'ABOUT' ),

            ]

        toolbar_order = [
            'SYNCHRO',
            'RELOAD',
            '',
            'SELECTNEXT',
            '',
            'PREVIOUS',
            'NEXT',
            '',
            'PREVIOUSPAGE',
            'NEXTPAGE',
            '',
            'OPENLINK',
            'OPENLINKS',
            '',
            'MARKASREAD',
            'MARKASUNREAD',
            '',
            'ADDSTAR',
            'DELSTAR',
            '',
            'ADDPUBLIC',
            'DELPUBLIC',
            '',
            'HELPDOC',
            'HELPBUG',
            'HELPNEWFEATURE',
            'HELPSITE',
            '',
            'QUIT',
            ]

        menu_content = []
        for menu_order_line in menu_order :
            if len(menu_order_line) == 1 :
                menu_content.append((menu_order_line[0],))
            elif len(menu_order_line) >= 2 :
                menu_path = menu_order_line[0]
                event_name = menu_order_line[1]
                event = self._events[event_name]
                accels = []
                if len(event['accels']) >= 1 :
                    accel_main = event['accels'][0]
                    for accel in event['accels'][1:] :
                        accels.append(self.ConvertStringsToAccels(accel))
                    menu_path+='\t'+'+'.join(accel_main)
                menu_content.append((menu_path,event['action'],event['help'],accels,event['id'],self._get_bitmap(event['bitmap'])))

        self.SetMenuContent(self,menu_content)


        self.SetTitle("RSS Reader")

        self._icon = None

        if len(sys.argv) >= 1 and os.path.exists(sys.argv[0]) and sys.argv[0][-4:] == '.exe':
            self._icon = wx.Icon(sys.argv[0], wx.BITMAP_TYPE_ICO)
        else :
            icon_name = os.path.join('..','res','pyrfeed.ico')
            if os.path.exists(icon_name):
                self._icon = wx.Icon(icon_name, wx.BITMAP_TYPE_ICO)

        if self._icon :
            self.SetIcon(self._icon)

        self._combo_filter.SetValue('')

        for event_name in toolbar_order :
            if event_name in self._events :
                event = self._events[event_name]
                self._tool_bar.AddTool(event['id'],self._get_bitmap(event['bitmap']),shortHelpString=event['help'])
            else :
                self._tool_bar.AddSeparator()

        self._tool_bar.Realize()

    def _bind_events(self) :
        self._listbox_title.Bind(wx.EVT_LISTBOX, self.OnTitleSelected)
        self._combo_filter.BindChange(self.OnComboChange)
        self._listbox_categories.Bind(wx.EVT_LISTBOX, self.OnCategoriesSelected)

    def Quit(self,event=None) :
        self.Close()

    def SetRssReader(self,rss_reader) :
        self._rss_reader = rss_reader
        self._combo_filter.SetValue(self._rss_reader.get_filter())

    def Populate(self,is_reload=False) :
        self._listbox_title.ClearChoices()

        if self._rss_reader :
            for index,selected,title in self._rss_reader.get_page() :
                self._listbox_title.Append("%d - %s" % (index+1,title),selected=selected)

            if is_reload :
                filters = self._rss_reader.get_filters()
                self._combo_filter.ChangeDefaultFilter( filters )
                self.ChangeLabels( filter(lambda x:x.startswith('label:'),filters) )

            self._combo_filter.ChangeDiffFilter( self._rss_reader.get_filters_diff() )

            item_count = '%d items.' % self._rss_reader.get_item_count()
            if self._rss_reader.get_page_count() > 1 :
                item_count += ' (page %d/%d)' % (self._rss_reader.get_page_number()+1,self._rss_reader.get_page_count())

            cursor_position = self._rss_reader.get_local_cursor_position()
            if 0 <= cursor_position < self._rss_reader.get_item_count() :
                self._listbox_title.SetSelection(cursor_position)

            self.SetCurrentStatus(item_count)
            self.UpdateSelectedItemStatus()
        self.OnTitleSelected()

    def OnTitleSelected (self, event=None) :
        if not(self._loading_page) :
            self._busy = wx.BusyCursor()
            try :
                self._loading_page = True
                if self._rss_reader :
                    self._rss_reader.set_local_cursor_position(self._listbox_title.GetSelection())
                
                    position = self._rss_reader.get_cursor_position()
                    self._window_html.ChangePage(self._rss_reader.get_content(position))
                
                    categories = self._rss_reader.get_categories(position)
                    self._listbox_categories.Clear()
                    if categories is not None :
                        for categorie in categories :
                            self._listbox_categories.Append(categorie)
                    self._listbox_title.SetFocus()
                self._loading_page = False
            finally :
                self._busy = None

    def Synchro (self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Synchronizing...")
            if self._rss_reader :
                synchro_result = self._rss_reader.synchro()
                if synchro_result is not None :
                    self.SetCurrentStatus(synchro_result)
                else :
                    self.Populate(is_reload=True)
            self._listbox_title.SetFocus()
        finally :
            self._busy = None

    def Reload (self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Reloading...")
            if self._rss_reader :
                self._rss_reader.reload()
                self.Populate(is_reload=True)
            self._listbox_title.SetFocus()
        finally :
            self._busy = None

    def Load (self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Loading...")
            if self._rss_reader :
                self._rss_reader.load()
                self.Populate(is_reload=True)
            self._listbox_title.SetFocus()
        finally :
            self._busy = None

    def _ProcessOnItems (self, action, status) :
        self._busy = wx.BusyCursor()
        try :
            if self._rss_reader :
                def update_status(position, count, total) :
                    self.SetCurrentStatus(status % {'position':position+1,'count':count,'total':total})
            
                self._rss_reader.process_selected_items(action=action, callback=update_status)
                self.Reload()
        finally :
            self._busy = None

    def MarkAsRead (self, event=None) :
        self._ProcessOnItems( self._rss_reader.mark_as_read, 'Marking item %(position)d as read (%(count)d/%(total)d)...' )

    def MarkAsUnread(self, event=None) :
        self._ProcessOnItems( self._rss_reader.mark_as_unread, 'Marking item %(position)d as unread (%(count)d/%(total)d)...' )

    def AddStar(self, event=None) :
        self._ProcessOnItems( self._rss_reader.add_star, 'Adding star on item %(position)d (%(count)d/%(total)d)...' )

    def DelStar(self, event=None) :
        self._ProcessOnItems( self._rss_reader.del_star, 'Removing star on item %(position)d (%(count)d/%(total)d)...' )

    def AddPublic(self, event=None) :
        self._ProcessOnItems( self._rss_reader.add_public, 'Adding public status on item %(position)d (%(count)d/%(total)d)...' )

    def DelPublic(self, event=None) :
        self._ProcessOnItems( self._rss_reader.del_public, 'Removing public status on item %(position)d (%(count)d/%(total)d)...' )

    def AddLabel(self, event) :
        menu_id = event.GetId()
        if menu_id in self._labels_by_add_id :
            label = self._labels_by_add_id[menu_id]
            self._ProcessOnItems( lambda positions : self._rss_reader.add_label(positions,label), 'Adding label "%s" on item %%(position)d (%%(count)d/%%(total)d)...' % label )

    def DelLabel(self, event) :
        menu_id = event.GetId()
        if menu_id in self._labels_by_del_id :
            label = self._labels_by_del_id[menu_id]
            self._ProcessOnItems( lambda positions : self._rss_reader.del_label(positions,label), 'Removing label "%s" on item %%(position)d (%%(count)d/%%(total)d)...' % label )

    def ChangeLabels(self,labels) :
        if self._labels_in_menus != labels :
            self._labels_in_menus = labels
            self._labels_by_add_id = {}
            self._labels_by_del_id = {}

            actions_infos = [
                {
                    'menu_label' : 'Edit/Add Label',
                    'menu_ids' : self._labels_by_add_id,
                    'menu_action' : self.AddLabel,
                    },
                {
                    'menu_label' : 'Edit/Del Label',
                    'menu_ids' : self._labels_by_del_id,
                    'menu_action' : self.DelLabel,
                    },
                ]

            for action_infos in actions_infos :
                menu = self.GetMenuByPath(action_infos['menu_label'])

                if menu is not None :
                    for old_id in map(lambda x:x.GetId(),menu.GetMenuItems()) :
                        self.Unbind(wx.EVT_MENU, id=old_id )
                        menu.Delete(old_id)

                    for label in labels :
                        label_id = wx.NewId()
                        label_name = label.split(':',1)[1]
                        action_infos['menu_ids'][label_id] = label_name
                        menu.AppendMenu( label_id, label_name, None )
                        self.Bind(wx.EVT_MENU, action_infos['menu_action'], id=label_id )

    def SetNextGuiMenu(self) :
        menu = self.GetMenuByPath('File/Switch interface')

        if menu is not None :
            for old_id in map(lambda x:x.GetId(),menu.GetMenuItems()) :
                self.Unbind(wx.EVT_MENU, id=old_id )
                menu.Delete(old_id)

            for ui_name,name in gui_info_list.get_ui_names() :
                menu_id = wx.NewId()
                menu_name = ui_name
                self._interface_name_by_menu_id[menu_id] = name
                menu.AppendMenu( menu_id, menu_name, None )
                self.Bind(wx.EVT_MENU, self.SetNextGui, id=menu_id )

    def SetNextGui(self,event) :
        menu_id = event.GetId()
        if menu_id in self._interface_name_by_menu_id :
            self._busy = wx.BusyCursor()
            try :
                self._config['gui/next'] = self._interface_name_by_menu_id[menu_id]
                self.Close()
            finally :
                self._busy = None

    def OpenItemInWebBrowser(self, positions) :
        for position in positions :
            link = self._rss_reader.get_link(position)
            if link and link != '' :
                webbrowser.open(link)

    def OpenInWebBrowser(self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            if self._rss_reader :
                self._rss_reader.process_current_item(action=self.OpenItemInWebBrowser)
        finally :
            self._busy = None

    def OpenMultiInWebBrowser(self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            if self._rss_reader :
                def update_status(position, count, total) :
                    self.SetCurrentStatus("Open link for item %(position)d (%(count)d/%(total)d)..." % {'position':position+1,'count':count,'total':total})
            
                self._rss_reader.process_selected_items(action=self.OpenItemInWebBrowser,callback=update_status)
        finally :
            self._busy = None

    def OnComboChange(self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Filtering...")
            if self._rss_reader :
                self._rss_reader.set_filter(self._combo_filter.GetValue())
                self.Populate()
        finally :
            self._busy = None

    def OnCategoriesSelected(self, event=None) :
        self._busy = wx.BusyCursor()
        try :
            categories_selected = ""
            for categorie_position in self._listbox_categories.GetSelections() :
                categories_selected += self._listbox_categories.GetString(categorie_position) + ' '
            categories_selected.strip(' ')

            text_data_object = wx.TextDataObject()
            text_data_object.SetText(categories_selected)
            if self._clipboard.Open() :
                self._clipboard.SetData(text_data_object)
                self._clipboard.Close()
        finally :
            self._busy = None

    def SelectItem(self, local_position) :
        self._rss_reader.set_local_cursor_position(local_position)
        item_selected = self._rss_reader.select_item(self._rss_reader.get_cursor_position())

        self.UpdateSelectedItemStatus()
        
        return item_selected

    def UpdateSelectedItemStatus(self) :
        selected_count = self._rss_reader.get_selected_item_count()
        self._status_bar.SetStatusText("%d selected item"%selected_count+(selected_count>1 and "s" or ""),1)
        
        
    def OnNextItem(self) :
        page_number = self._rss_reader.get_page_number()
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()+1)
        if page_number != self._rss_reader.get_page_number() :
            self.Populate()
        else :
            self._rss_reader.get_local_cursor_position()
            self._listbox_title.SetSelection(self._rss_reader.get_local_cursor_position())
        self.OnTitleSelected(None)
        
    def OnPrevItem(self) :
        page_number = self._rss_reader.get_page_number()
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()-1)
        if page_number != self._rss_reader.get_page_number() :
            self.Populate()
        else :
            self._rss_reader.get_local_cursor_position()
            self._listbox_title.SetSelection(self._rss_reader.get_local_cursor_position())
        self.OnTitleSelected(None)
        
    def SetCurrentStatus(self, text) :
        self._current_status = text
        self._status_bar.SetStatusText(text,0)

    def SetTemporaryStatus(self, text) :
        if text is None :
            self.UnsetTemporaryStatus()
        else :
            self._status_bar.SetStatusText(text,0)

    def UnsetTemporaryStatus(self) :
        text = self._current_status
        if text is None :
            text = ''
        self.SetCurrentStatus(text)

    def FocusFilter(self, event=None) :
        self._combo_filter.SetFocus()

    def OnNextPage(self, event) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Changing page...")
            
            page_number = self._rss_reader.get_page_number()
            page_count = self._rss_reader.get_page_count()
            if page_number < page_count-1:
                self._rss_reader.set_page_number(page_number+1)
                self.Populate()
        finally :
            self._busy = None

    def OnPreviousPage(self, event) :
        self._busy = wx.BusyCursor()
        try :
            self.SetCurrentStatus("Changing page...")
            
            page_number = self._rss_reader.get_page_number()
            if 0 < page_number :
                self._rss_reader.set_page_number(page_number-1)
                self.Populate()
        finally :
            self._busy = None

    def ViewAllItems(self, event=None) :
        self._combo_filter.SetValue('')
        self.OnComboChange()

    def ViewUnreadItems(self, event=None) :
        self._combo_filter.SetValue('-state:read')
        self.OnComboChange()
        
    def FilterUnreadItems(self, event=None) :
        self._combo_filter.AppendValue('-state:read')
        self.OnComboChange()

    def SortByTime(self, event=None) :
        self._combo_filter.AppendValue('sort:crawled')
        self.OnComboChange()

    def SortByTimeDesc(self, event=None) :
        self._combo_filter.AppendValue('-sort:crawled')
        self.OnComboChange()

    def SortByTitle(self, event=None) :
        self._combo_filter.AppendValue('sort:title')
        self.OnComboChange()

    def SortByTitleDesc(self, event=None) :
        self._combo_filter.AppendValue('-sort:title')
        self.OnComboChange()

    def OnHelpDoc(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed/wiki/pyrfeed')

    def OnHelpIssues(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed/issues/list')

    def OnHelpWebSite(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed')

    def OnAbout(self, event=None) :
        adi = wx.AboutDialogInfo()
        adi.SetCopyright('GPL')
        adi.SetDevelopers(['Gissehel'])
        adi.SetName('pyrfeed')
        adi.SetVersion(pyrfeed_version)
        adi.SetWebSite('http://code.google.com/p/pyrfeed')
        adi.SetIcon(wx.Icon(os.path.join('..','res','pyrfeed-64x64.png'),wx.BITMAP_TYPE_ANY))
        wx.AboutBox(adi)

    _strings_to_accels = {
        'ADD':wx.WXK_ADD, 'ALT':wx.WXK_ALT, 'BACK':wx.WXK_BACK,
        'CANCEL':wx.WXK_CANCEL, 'CAPITAL':wx.WXK_CAPITAL, 'CLEAR':wx.WXK_CLEAR,
        'COMMAND':wx.WXK_COMMAND, 'CONTROL':wx.WXK_CONTROL,
        'DECIMAL':wx.WXK_DECIMAL, 'DELETE':wx.WXK_DELETE,
        'DIVIDE':wx.WXK_DIVIDE, 'DOWN':wx.WXK_DOWN, 'END':wx.WXK_END,
        'ESCAPE':wx.WXK_ESCAPE, 'EXECUTE':wx.WXK_EXECUTE, 'F1':wx.WXK_F1,
        'F10':wx.WXK_F10, 'F11':wx.WXK_F11, 'F12':wx.WXK_F12, 'F13':wx.WXK_F13,
        'F14':wx.WXK_F14, 'F15':wx.WXK_F15, 'F16':wx.WXK_F16, 'F17':wx.WXK_F17,
        'F18':wx.WXK_F18, 'F19':wx.WXK_F19, 'F2':wx.WXK_F2, 'F20':wx.WXK_F20,
        'F21':wx.WXK_F21, 'F22':wx.WXK_F22, 'F23':wx.WXK_F23, 'F24':wx.WXK_F24,
        'F3':wx.WXK_F3, 'F4':wx.WXK_F4, 'F5':wx.WXK_F5, 'F6':wx.WXK_F6,
        'F7':wx.WXK_F7, 'F8':wx.WXK_F8, 'F9':wx.WXK_F9, 'HELP':wx.WXK_HELP,
        'HOME':wx.WXK_HOME, 'INSERT':wx.WXK_INSERT, 'LBUTTON':wx.WXK_LBUTTON,
        'LEFT':wx.WXK_LEFT, 'MBUTTON':wx.WXK_MBUTTON, 'MENU':wx.WXK_MENU,
        'MULTIPLY':wx.WXK_MULTIPLY, 'NEXT':wx.WXK_NEXT,
        'NUMLOCK':wx.WXK_NUMLOCK, 'NUMPAD0':wx.WXK_NUMPAD0,
        'NUMPAD1':wx.WXK_NUMPAD1, 'NUMPAD2':wx.WXK_NUMPAD2,
        'NUMPAD3':wx.WXK_NUMPAD3, 'NUMPAD4':wx.WXK_NUMPAD4,
        'NUMPAD5':wx.WXK_NUMPAD5, 'NUMPAD6':wx.WXK_NUMPAD6,
        'NUMPAD7':wx.WXK_NUMPAD7, 'NUMPAD8':wx.WXK_NUMPAD8,
        'NUMPAD9':wx.WXK_NUMPAD9, 'NUMPAD_ADD':wx.WXK_NUMPAD_ADD,
        'NUMPAD_BEGIN':wx.WXK_NUMPAD_BEGIN,
        'NUMPAD_DECIMAL':wx.WXK_NUMPAD_DECIMAL,
        'NUMPAD_DELETE':wx.WXK_NUMPAD_DELETE,
        'NUMPAD_DIVIDE':wx.WXK_NUMPAD_DIVIDE, 'NUMPAD_DOWN':wx.WXK_NUMPAD_DOWN,
        'NUMPAD_END':wx.WXK_NUMPAD_END, 'NUMPAD_ENTER':wx.WXK_NUMPAD_ENTER,
        'NUMPAD_EQUAL':wx.WXK_NUMPAD_EQUAL, 'NUMPAD_F1':wx.WXK_NUMPAD_F1,
        'NUMPAD_F2':wx.WXK_NUMPAD_F2, 'NUMPAD_F3':wx.WXK_NUMPAD_F3,
        'NUMPAD_F4':wx.WXK_NUMPAD_F4, 'NUMPAD_HOME':wx.WXK_NUMPAD_HOME,
        'NUMPAD_INSERT':wx.WXK_NUMPAD_INSERT, 'NUMPAD_LEFT':wx.WXK_NUMPAD_LEFT,
        'NUMPAD_MULTIPLY':wx.WXK_NUMPAD_MULTIPLY, 'NUMPAD_NEXT':wx.WXK_NUMPAD_NEXT,
        'NUMPAD_PAGEDOWN':wx.WXK_NUMPAD_PAGEDOWN, 'NUMPAD_PAGEUP':wx.WXK_NUMPAD_PAGEUP,
        'NUMPAD_PRIOR':wx.WXK_NUMPAD_PRIOR, 'NUMPAD_RIGHT':wx.WXK_NUMPAD_RIGHT,
        'NUMPAD_SEPARATOR':wx.WXK_NUMPAD_SEPARATOR, 'NUMPAD_SPACE':wx.WXK_NUMPAD_SPACE,
        'NUMPAD_SUBTRACT':wx.WXK_NUMPAD_SUBTRACT, 'NUMPAD_TAB':wx.WXK_NUMPAD_TAB,
        'NUMPAD_UP':wx.WXK_NUMPAD_UP, 'PAGEDOWN':wx.WXK_PAGEDOWN,
        'PAGEUP':wx.WXK_PAGEUP, 'PAUSE':wx.WXK_PAUSE, 'PRINT':wx.WXK_PRINT,
        'PRIOR':wx.WXK_PRIOR, 'RBUTTON':wx.WXK_RBUTTON, 'RETURN':wx.WXK_RETURN,
        'RIGHT':wx.WXK_RIGHT, 'SCROLL':wx.WXK_SCROLL, 'SELECT':wx.WXK_SELECT,
        'SEPARATOR':wx.WXK_SEPARATOR, 'SHIFT':wx.WXK_SHIFT,
        'SNAPSHOT':wx.WXK_SNAPSHOT, 'SPACE':wx.WXK_SPACE, 'SPECIAL1':wx.WXK_SPECIAL1,
        'SPECIAL10':wx.WXK_SPECIAL10, 'SPECIAL11':wx.WXK_SPECIAL11,
        'SPECIAL12':wx.WXK_SPECIAL12, 'SPECIAL13':wx.WXK_SPECIAL13,
        'SPECIAL14':wx.WXK_SPECIAL14, 'SPECIAL15':wx.WXK_SPECIAL15,
        'SPECIAL16':wx.WXK_SPECIAL16, 'SPECIAL17':wx.WXK_SPECIAL17,
        'SPECIAL18':wx.WXK_SPECIAL18, 'SPECIAL19':wx.WXK_SPECIAL19,
        'SPECIAL2':wx.WXK_SPECIAL2, 'SPECIAL20':wx.WXK_SPECIAL20,
        'SPECIAL3':wx.WXK_SPECIAL3, 'SPECIAL4':wx.WXK_SPECIAL4,
        'SPECIAL5':wx.WXK_SPECIAL5, 'SPECIAL6':wx.WXK_SPECIAL6,
        'SPECIAL7':wx.WXK_SPECIAL7, 'SPECIAL8':wx.WXK_SPECIAL8,
        'SPECIAL9':wx.WXK_SPECIAL9, 'START':wx.WXK_START,
        'SUBTRACT':wx.WXK_SUBTRACT, 'TAB':wx.WXK_TAB, 'UP':wx.WXK_UP,
        'WINDOWS_LEFT':wx.WXK_WINDOWS_LEFT, 'WINDOWS_MENU':wx.WXK_WINDOWS_MENU,
        'WINDOWS_RIGHT':wx.WXK_WINDOWS_RIGHT,
        }
    _strings_to_accelmods = {
        'Ctrl' : wx.ACCEL_CTRL,
        'Alt' : wx.ACCEL_ALT,
        'Shift' : wx.ACCEL_SHIFT,
        }

    def ConvertStringsToAccels(self,strings) :
        mods = strings[:-1]
        key = strings[-1]
        result = [0,None]
        if len(key)>1 :
            if key in self._strings_to_accels :
                result[1] = self._strings_to_accels[key]
            else :
                raise Exception("Don't know key [%s]" % key)
        else :
            result[1] = ord(key)
        if len(mods) >= 0 :
            for mod in mods :
                if mod in self._strings_to_accelmods :
                    result[0] |= self._strings_to_accelmods[mod]
                else :
                    raise Exception("Don't know key mod [%s]" % mod)
        else :
            result[1] = wx.ACCEL_NORMAL

        return tuple(result)

def get_simple_app() :
    if hasattr(get_simple_app,'_simple_app') :
        return get_simple_app._simple_app
    get_simple_app._simple_app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    return get_simple_app._simple_app

class GuiInfoWx(GuiInfo) :
    names = []
    priority = 50
    RSSReaderFrameClass = None

    def _start_application(self) :
        app = get_simple_app()
        rss_reader_frame = self.RSSReaderFrameClass(self._config, None)
        rss_reader_frame.SetRssReader(self._rss_reader)
        app.SetTopWindow(rss_reader_frame)
        rss_reader_frame.Show()
        rss_reader_frame.Load()
        app.MainLoop()

    def get_doc(self) :
        return ""

register_key( 'wx/sashposition', int, doc='Position of the Sash seperation in pixels', default=200 )
register_key( 'wx/htmlwindow', str, doc='HTML Window component to use (simple/complex/best)', default='best', advanced=True )

# 'gui/next' will be handled elsewere for registration
