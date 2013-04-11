class ElementInfoList(object) :
    # You must set a base class when you overload, not None
    BaseClass = None

    def __init__(self) :
        self._elementinfo_class_by_name = {}
        self._default_info = None
        self._name_by_ui_name = {}

    def register(self,element_info_class) :
        if len(element_info_class.names) > 0 :
            if (self._default_info is None) or (self._default_info.priority <= element_info_class.priority) :
                self._default_info = element_info_class
            if element_info_class.ui_name is not None :
                self._name_by_ui_name[element_info_class.ui_name] = element_info_class.names[0]

        for name in element_info_class.names :
            if name in self._elementinfo_class_by_name :
                if self._elementinfo_class_by_name[name].priority <= element_info_class.priority :
                    self._elementinfo_class_by_name[name] = element_info_class
            else :
                self._elementinfo_class_by_name[name] = element_info_class

    def __getitem__(self,name) :
        return self._elementinfo_class_by_name[name]

    def __contains__(self,name) :
        return name in self._elementinfo_class_by_name

    def get_default_info(self) :
        return self._default_info

    def get_default_info_name(self) :
        return self._default_info.names[0]

    def get_ui_names(self) :
        ui_names = list(self._name_by_ui_name.iteritems())
        ui_names.sort(key=lambda x:self[x[1]].priority)
        return ui_names

    def _auto_register(self,element_info_class=None) :
        if element_info_class == None :
            element_info_class = self.BaseClass
        self.register(element_info_class)

        for subclass in element_info_class.__subclasses__() :
            self._auto_register(subclass)
