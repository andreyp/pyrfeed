from pyrfeed.config import register_key

class PageSelector(object): 
    def __init__(self,config,cursor_position=0) :
        self.__config = config
        self.__cursor_position = 0
        self.__items = []
        self.__items_count = len(self.__items)
        self.__selected_items = []
        self.__selected_item_count = 0
        
        self.set_cursor_position(cursor_position)

    def select_item(self,position=None) :
        '''Select an item in the current page (given a global position or with the current position if none given)'''
        if position is None :
            position = self.__cursor_position
        if 0 <= position < self.__items_count :
            if self.__selected_items[position] :
                self.__selected_item_count -= 1
            self.__selected_items[position] = not(self.__selected_items[position])
            if self.__selected_items[position] :
                self.__selected_item_count += 1
            return self.__selected_items[position]
        else :
            return False

    def process_current_item(self,action) :
        '''Process the current item with an action'''
        return action([self.__cursor_position])

    def process_selected_items(self,action,callback=None,selection=None) :
        '''Process the selected items with an action, using the callback for updating progression.'''

        if selection is None :
            selection = filter(lambda item_position:self.__selected_items[item_position],xrange(self.__items_count))

        callback( position=-1, count=0, total=len(selection) )

        if 0 < len(selection) :
            item_courant=0
            
            item_step = 1+int(len(selection)/5.)
            item_list = []
            for item_position in selection :
                    item_list.append(item_position)
                    if len(item_list)>=item_step :
                        action(item_list)
                        item_courant += len(item_list)
                        if callback is not None :
                            callback( position=item_position, count=item_courant, total=len(selection) )
                        item_list = []    
        else :
            action([self.__cursor_position])
            if callback is not None :
                callback( position=self.__cursor_position, count=1, total=1 )

    def get_page_number(self) :
        '''Get the current page number (start with 0)'''
        return int(self.__cursor_position/self.__config['pagesize'])

    def get_page_count(self) :
        '''Get the current page count'''
        return ((self.__items_count-1)/self.__config['pagesize'])+1

    def get_cursor_position(self) :
        '''Get the current cursor position (start with 0, and global)'''
        return self.__cursor_position

    def get_local_cursor_position(self) :
        '''Get the current local cursor position (start with 0)'''
        return self.__cursor_position-self.get_page_number()*self.__config['pagesize']

    def get_item_count(self) :
        '''Get item count'''
        return self.__items_count

    def get_selected_items(self) :
        '''Get selected items'''
        selected_items = []
        for position in xrange(self.__items_count) :
            if self.__selected_items[position] :
                selected_items.append(position)
        return selected_items

    def get_selected_item_count(self) :
        '''Get selected item count'''
        return self.__selected_item_count

    def set_page_number(self,page_number) :
        '''Set the current page number (start with 0)'''
        current_page = self.get_page_number()
        if current_page != page_number :
            self.__cursor_position = page_number*self.__config['pagesize']

    def set_cursor_position(self,position) :
        '''Set the current cursor position (start with 0, and global)'''
        if 0 <= position < self.__items_count :
            self.__cursor_position = position

    def set_local_cursor_position(self,position) :
        '''Set the current local cursor position (start with 0)'''
        if 0 <= position < self.__config['pagesize'] :
            self.__cursor_position = position + self.get_page_number()*self.__config['pagesize']

    def set_items(self,items) :
        '''Set the items'''
        self.__items = items
        self.__items_count = len(self.__items)
        self.__selected_items = [False] * self.__items_count
        self.__selected_item_count = 0
        
        if self.__cursor_position >= self.__items_count :
            self.__cursor_position = self.__items_count-1
        if self.__cursor_position < 0 :
            self.__cursor_position = 0

    def get_page(self) :
        """Get the current page (which consist of a tuple of 'a global position', 'a boolean which is True if selected', 'a title')"""
        current_position = self.get_page_number()*self.__config['pagesize']
        page = []
        for title in self.__items[current_position:current_position+self.__config['pagesize']] :
            page.append((current_position,self.__selected_items[current_position],self.__items[current_position]))
            current_position += 1
        return page

register_key( 'pagesize', int, doc='Size of a page of items', default=30 )
