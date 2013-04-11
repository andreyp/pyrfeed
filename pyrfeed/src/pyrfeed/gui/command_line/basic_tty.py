import sys
import webbrowser

from html2text import html2text_file

from pyrfeed.gui.info import GuiInfo
from pyrfeed.gui.info_list import gui_info_list
from pyrfeed.config import register_key


class ExceptionCommandDoesntExist(Exception) :
    pass

class ExceptionMissingMethod(Exception) :
    pass

class ExceptionNoCommand(Exception) :
    pass

class TTYCommands(object) :
    _commands = {
        'QUIT'              : { 'names' : [ 'q',          ], 'importance' : 10, 'comment' : 'Quit' },
        'SEARCH'            : { 'names' : [ '/',          ], 'importance' : 20, 'comment' : 'Search' },
        'SHOW'              : { 'names' : [ 's',          ], 'importance' : 20, 'comment' : 'Show the current page and change the current position' },
        'SELECT'            : { 'names' : [ 'x',          ], 'importance' : 20, 'comment' : 'Select items' },
        'NEXT'              : { 'names' : [ 'j',          ], 'importance' : 20, 'comment' : 'Go to next position' },
        'PREV'              : { 'names' : [ 'k',          ], 'importance' : 20, 'comment' : 'Go to previous position' },
        'RELOAD'            : { 'names' : [ 'R',          ], 'importance' : 10, 'comment' : 'Reload' },
        'SYNCHRO'           : { 'names' : [ 'S',          ], 'importance' : 10, 'comment' : 'Synchro' },
        'VIEW'              : { 'names' : [ 'v',          ], 'importance' : 10, 'comment' : 'View a list of items' },
        'VIEWDETAILS'       : { 'names' : [ 'V',          ], 'importance' : 10, 'comment' : 'View details of a list of items' },
        'VIEWNEXT'          : { 'names' : [ 'vn',         ], 'importance' : 10, 'comment' : 'View current item and go to next' },
        'VIEWDETAILSNEXT'   : { 'names' : [ 'VN',         ], 'importance' : 10, 'comment' : 'View details of current item and go to next' },
        'OPENCURRENT'       : { 'names' : [ 'o',          ], 'importance' : 10, 'comment' : 'Open current item' },
        'OPENALL'           : { 'names' : [ 'O',          ], 'importance' : 10, 'comment' : 'Open a list of items' },
        'ENCODE'            : { 'names' : [ 'e',          ], 'importance' :  0, 'comment' : 'Set the current tty encoding' },
        'MARKASREAD'        : { 'names' : [ 'r',          ], 'importance' : 10, 'comment' : 'Mark a list of items as read' },
        'MARKASUNREAD'      : { 'names' : [ 'u',          ], 'importance' : 10, 'comment' : 'Mark a list of items as unread' },
        'SAVE'              : { 'names' : [ 'save',       ], 'importance' :  0, 'comment' : 'Save configuration' },
        'SET'               : { 'names' : [ 'set',        ], 'importance' :  0, 'comment' : 'Set a configuration key' },
        'GET'               : { 'names' : [ 'get',        ], 'importance' :  0, 'comment' : 'Get a configuration key' },
        'DEL'               : { 'names' : [ 'del',        ], 'importance' :  0, 'comment' : 'Delete a configuration key' },
        'SHOWFILTERS'       : { 'names' : [ 'f',          ], 'importance' :  0, 'comment' : 'Show all filters' },
        'SHOWFILTERSDIFF'   : { 'names' : [ 'F',          ], 'importance' :  0, 'comment' : 'Show filters applicable over the current filter' },
        'ADDSTAR'           : { 'names' : [ 'addstar',    ], 'importance' :  5, 'comment' : 'Add star to a list of items' },
        'DELSTAR'           : { 'names' : [ 'delstar',    ], 'importance' :  5, 'comment' : 'Delete star from a list of items' },
        'ADDPUBLIC'         : { 'names' : [ 'addpublic',  ], 'importance' :  5, 'comment' : 'Add public status to a list of items' },
        'DELPUBLIC'         : { 'names' : [ 'delpublic',  ], 'importance' :  5, 'comment' : 'Remove public status from a list of items' },
        'ADDLABEL'          : { 'names' : [ 'addlabel',   ], 'importance' :  5, 'comment' : 'Add label to a list of items' },
        'DELLABEL'          : { 'names' : [ 'dellabel',   ], 'importance' :  5, 'comment' : 'Remove label from a list of items' },
        'SWITCH'            : { 'names' : [ 'switch',     ], 'importance' :  0, 'comment' : 'Switch to another user interface' },
        'HELP'              : { 'names' : [ 'help', '?',  ], 'importance' : 10, 'comment' : 'Show help' },
        }

    def __init__(self) :
        self._command_id_by_name = {}
        for command_id in self._commands :
            for command_name in self._commands[command_id]['names'] :
                self._command_id_by_name[command_name] = command_id
            setattr(self,command_id,command_id)

    def parse_line(self,line,executor) :
        '''This method execute the command specified in the 'line' assuming executor implement command do_XXXXX if XXXXX is a valid command and have been specified in the line'''

        action = line.strip('\r\n')
        action_list = filter(len,action.split(' '))

        result = None

        if len(action_list)>0 :
            arguments = action_list[1:]
            command_name = action_list[0]
            if command_name in self._command_id_by_name :
                # Ok, the command is valid

                command_id = self._command_id_by_name[command_name]

                method_name = 'do_'+command_id
                if hasattr(executor,method_name) :
                    # Everything is ok here... We call the method...
                    method = getattr(executor,method_name)
                    # No return here : return always at the end of the code
                    result = method(command_name,*arguments)
                else :
                    # The command exists, but the method is not implemented
                    raise ExceptionMissingMethod()
            else :
                # Invalid command
                raise ExceptionCommandDoesntExist()
        else :
            # No command
            raise ExceptionNoCommand()

        return result        

    def get_help(self) :
        commands_list = list(self._commands.iteritems())
        commands_list.sort(key=lambda x:-x[1]['importance'])
        
        help_lines = []
        
        for command_id,command_info in commands_list :
            help_lines.append( ' %-20s %s'%(', '.join(command_info['names']),command_info['comment'] ) )

        return '\n'.join(help_lines)

class BasicTTY(object):
    def __init__(self,config) :
        self._config = config
        self._rss_reader = None
        self._filters = []
        self._filters_diff = []
        self._titles = {}
        self._encoding = self._config['tty/encoding']
        
        self._need_quit = False

    def set_rss_reader(self,rss_reader) :
        self._rss_reader = rss_reader
        self._rss_reader.load()
        self.print_title()

    def _get_line(self) :
        return sys.stdin.readline()

    def _print(self,line) :
        return sys.stdout.write(line.encode(self._encoding,'replace'))

    def synchro(self) :
        if self._rss_reader is not None :
            synchro_result = self._rss_reader.synchro()
            if synchro_result is not None :
                print synchro_result
            self.print_title()

    def reload(self) :
        if self._rss_reader is not None :
            self._rss_reader.reload()
            self.print_title()

    def format_title(self,title) :
        return html2text_file(title,None).strip('\r\n ').replace('\n',' ')

    def print_title(self):
        if self._rss_reader :
            screensize = self._config['tty/screensize']

            self._page = map(lambda (position,selected,title):(position,selected,self.format_title(title)),self._rss_reader.get_page())
            self._print("Current filter : [%s]\n" % (self._rss_reader.get_filter(),))
            self._print("\n")

            current_position = self._rss_reader.get_cursor_position()
            for position,selected,title in self._page :
                self._titles[position] = title
                self._print(" %3d. [%s]%s%s\n" % (position+1, selected and "X" or " ", (current_position==position) and ">" or " ", title[:screensize-11]))

            self._filters = self._rss_reader.get_filters()
            self._filters_diff = self._rss_reader.get_filters_diff()
            self._print("\n")
            self._print("%d items\n" % self._rss_reader.get_item_count())

    def get_int_list(self,args) :
        int_list = []
        for arg in args :
        
            if '-' in arg :
                interval = arg.split('-')
                # TODO : Check len(interval) == 2
                if interval[0] == '' :
                    interval[0] = 0
                else :
                    # TODO : Check interval[0] is an int
                    interval[0] = int(interval[0])-1

                if interval[1] == '' :
                    interval[1] = self._rss_reader.get_item_count()-1
                else :
                    # TODO : Check interval[1] is an int
                    interval[1] = int(interval[1])-1
                int_list += range(interval[0],interval[1]+1)
            elif arg in ('x','X') :
                int_list += self._rss_reader.get_selected_items()
            elif arg in ('c','C') :
                int_list += [self._rss_reader.get_cursor_position()]
            else :
                # TODO : Check arg is an int
                int_list.append(int(arg)-1)
        return int_list

    def get_selection_list(self,args) :
        positions = self.get_int_list(args)
        if len(positions) == 0 :
            positions = self._rss_reader.get_selected_items()
            if len(positions) == 0 :
                positions = [self._rss_reader.get_cursor_position()]
        return positions
        
    def main_loop(self) :
        self._commands = TTYCommands()
        
        while not(self._need_quit) :
            self._print("\nAction? ")
            line = self._get_line().strip('\r\n')

            # This will parse the line, and execute on "self" (this will execute commands like do_XXXXX if XXXXX is the "id" of the command in the line)            
            try :
                self._commands.parse_line(line,executor=self)

            except ExceptionNoCommand :
                # No command is ok, no problem here...
                pass

            except ExceptionCommandDoesntExist :
                # Wrong command typed. We just inform that the command doesn't exists...
                self._print("Don't understand [%s]\nType ? for help." % line)

            except ExceptionMissingMethod :
                # This is quite a problem...
                self._print("The command [%s] is recognized as a command, but is not implemented.\nPlease, report this problem. http://code.google.com/p/pyrfeed/issues/entry" % line)


    def do_QUIT(self,command_name,*args) :
        self._need_quit = True

    def do_RELOAD(self,command_name,*args) :
        self.reload()

    def do_SYNCHRO(self,command_name,*args) :
        self.synchro()

    def do_SHOW(self,command_name,*args) :
        if len(args)>0 :
            position = self.get_int_list(args)[-1]
            self._rss_reader.set_cursor_position(position)

        self.print_title()

    def do_SELECT(self,command_name,*args) :
        for position in self.get_selection_list(args) :
            self._rss_reader.select_item(position)
        self.print_title()

    def do_NEXT(self,command_name,*args) :
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()+1)
        self.print_title()

    def do_PREV(self,command_name,*args) :
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()-1)
        self.print_title()

    def do_VIEW_DETAILS_OR_NOT(self,command_name,details,*args) :
        for position in self.get_selection_list(args) :
            self._print('\n')
            self._print('='*3+' [ '+('%3d'%(position+1,))+' ] '+'='*58+'\n')
            self._print(self.format_title(self._rss_reader.get_title(position))+'\n')
            self._print('-'*65+'\n')
            if details :
                link = self._rss_reader.get_link(position)
                if link and link != '' :
                    self._print(link+'\n')
                    self._print('-'*65+'\n')
            self._print(html2text_file(self._rss_reader.get_content(position),None))
            if details :
                categories = self._rss_reader.get_categories(position)
                if categories is not None :
                    if len(categories)>0 :
                        self._print('-'*65+'\n')
                    for categorie in categories :
                        self._print('  %s\n' % categorie)
                    if len(categories)>0 :
                        self._print('-'*65+'\n')

    def do_VIEW(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,False,*args)

    def do_VIEWDETAILS(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,True,*args)

    def do_VIEWNEXT(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,False)
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()+1)

    def do_VIEWDETAILSNEXT(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,True)
        self._rss_reader.set_cursor_position(self._rss_reader.get_cursor_position()+1)

    def do_ENCODE(self,command_name,*args) :
        # test on len(args) ? or let crash ?
        self._encoding = args[0]

    def do_OPENCURRENT(self,command_name,*args) :
        link = self._rss_reader.get_link(self._rss_reader.get_cursor_position())
        if link and link != '' :
            webbrowser.open(link)

    def do_OPENALL(self,command_name,*args) :
        for position in self.get_selection_list(args) :
            link = self._rss_reader.get_link(position)
            if link and link != '' :
                webbrowser.open(link)

    def do_MARKASREAD(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.mark_as_read, selection=self.get_selection_list(args) )
        self.reload()

    def do_MARKASUNREAD(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.mark_as_unread, selection=self.get_selection_list(args) )
        self.reload()

    def do_SEARCH(self,command_name,*args) :
        self._rss_reader.set_filter(' '.join(args))
        self.print_title()

    def do_SAVE(self,command_name,*args) :
        self._config.save()

    def do_SET(self,command_name,*args) :
        if len(args) > 1 :
            self._config[args[0]] = args[1]
        else :
            for key in self._config.keys() :
                value = self._config[key]
                if key == 'passwd' :
                    # Urk ! not nice !
                    value = '*' * 16
                self._print('%s %s\n' % (key,value))

    def do_GET(self,command_name,*args) :
        if len(args) > 0 :
            for arg in args : 
                if arg in self._config :
                    self._print('%s %s\n' % (arg,self._config[arg]))
                else :
                    self._print('  %s is not configurable\n' % (arg,))
        else :
            config_keys = self._config.config_keys
            keynames = config_keys.keys()
            keynames.sort()

            configkeynames = self._config.keys()
            for keyname in keynames :
                if keyname in configkeynames :
                    value = self._config[keyname]
                    if keyname == 'passwd' :
                        # Urk ! not nice !
                        value = '*' * 16
                    self._print('%-30s %-12s (default:%s)\n' % (keyname,value,config_keys[keyname]['default']))
                else :
                    self._print('%-30s              (default:%s)\n' % (keyname,config_keys[keyname]['default']))

    def do_DEL(self,command_name,*args) :
        del self._config[args[0]]

    def do_SHOWFILTERS(self,command_name,*args) :
        self._print('Filters :\n')
        for filter_command in self._filters :
            self._print('  %s\n' % filter_command)

    def do_SHOWFILTERSDIFF(self,command_name,*args) :
        self._print('Filters diff :\n')
        for filter_command in self._filters_diff :
            self._print('  %s\n' % filter_command)

    def do_ADDSTAR(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.add_star, selection=self.get_selection_list(args) )
        self.reload()

    def do_DELSTAR(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.del_star, selection=self.get_selection_list(args) )
        self.reload()

    def do_ADDPUBLIC(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.add_public, selection=self.get_selection_list(args) )
        self.reload()

    def do_DELPUBLIC(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=self._rss_reader.del_public, selection=self.get_selection_list(args) )
        self.reload()

    def do_ADDLABEL(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=lambda positions:self._rss_reader.add_label(positions,args[0]), selection=self.get_selection_list(args[1:]) )
        self.reload()

    def do_DELLABEL(self,command_name,*args) :
        self._rss_reader.process_selected_items( action=lambda positions:self._rss_reader.del_label(positions,args[0]), selection=self.get_selection_list(args[1:]) )
        self.reload()

    def do_SWITCH(self,command_name,*args) :
        if len(args) > 0 :
            for ui_name,name in gui_info_list.get_ui_names() :
                if name == args[0] or ui_name == args[0] :
                    self._config['gui/next'] = name
                    self._need_quit = True
                    break
            else :
                if name in gui_info_list :
                    self._config['gui/next'] = name
                    self._need_quit = True
                else :
                    self._print("Don't know [%s] as an interface name\n" % name)
        else :
            for ui_name,name in gui_info_list.get_ui_names() :
                self._print("    %s - %s\n" % (name,ui_name))

    def do_HELP(self,command_name,*args) :
        self._print(self._commands.get_help())

class GuiInfoTTY(GuiInfo) :
    names = ['tty','BasicTTY','cl']
    priority = 10
    ui_name = 'TTY interface'

    def _start_application(self) :
        commandline = BasicTTY(self._config)
        commandline.set_rss_reader(self._rss_reader)
        commandline.main_loop()

    def get_doc(self) :
        return ""

register_key( 'tty/encoding', str, doc='TTY Encoding', default='iso-8859-1', advanced=True )
register_key( 'tty/screensize', int, doc='Width of the TTY', default=80, advanced=True )

# 'gui/next' will be handled elsewere for registration

