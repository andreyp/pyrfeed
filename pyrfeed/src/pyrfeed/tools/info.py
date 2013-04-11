""" This package's goal is to provide a way to pyrfeed's elements to
register themself to rest of the world with a consistent interface """

class ElementInfo(object) :
    # overloaded in leaf
    names = []
    priority = 50
    ui_name = None

    # overloaded for once per InfoList
    name = 'GenericElement'

    def get_doc(self) :
        ''' This method need to be overloaded '''
        raise Exception('This method never been called. You must overload it.')

