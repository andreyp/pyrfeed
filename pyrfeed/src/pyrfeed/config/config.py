import os
import sys
import ConfigParser

CONFIGURATION_NAME = ".pyrfeed.ini"

class InvalidConfigurationKey(Exception) :
    pass

class ConfigClass(object) :
    config_types = {}
    config_keys = {}

    _main_section = 'pyrfeed'

    def __init__(self,argv=[]) :
        self._config_parser = ConfigParser.SafeConfigParser()
        self._filename = None
        self._non_persistant = {'':[]}

        self.process_argv(None,argv)
        self.load()

    def _get_default(self,key) :
        return self.config_keys[key]['default']

    def _from_str(self,key,str_value) :
        if str_value is None :
            return self._get_default(key)
        return self.config_types[self.config_keys[key]['type']]['from_str'](str_value)

    def _from_type(self,key,type_value) :
        return self.config_types[self.config_keys[key]['type']]['from_type'](type_value)

    def __getitem__(self,key) :
        if key not in self.config_keys :
            raise InvalidConfigurationKey("%s is not a valid configuration key" % key)

        section = self._main_section
        result = self._get_default(key)
        if key in self._non_persistant :
            result = self._from_str(key,self._non_persistant[key])
        elif self._config_parser.has_section(section) :
            if self._config_parser.has_option(section,key) :
                result = self._from_str(key,self._config_parser.get(section,key))
        # print result
        return result

    def __contains__(self,key) :
        return key in self.config_keys

    def __setitem__(self,key,value) :
        if key not in self.config_keys :
            raise InvalidConfigurationKey("%s is not a valid configuration key" % key)

        section = self._main_section
        if key in self._non_persistant :
            del self._non_persistant[key]
        if not(self._config_parser.has_section(section)) :
            self._config_parser.add_section(section)
        self._config_parser.set(section,key,self._from_type(key,value))

    def __delitem__(self,key) :
        if key not in self.config_keys :
            raise InvalidConfigurationKey("%s is not a valid configuration key" % key)

        section = self._main_section
        if key in self._non_persistant :
            del self._non_persistant[key]
        if self._config_parser.has_section(section) :
            if self._config_parser.has_option(section,key) :
                self._config_parser.remove_option(section,key)

    def keys(self) :
        section = self._main_section
        keys = set(self._non_persistant.keys())
        if self._config_parser.has_section(section) :
            keys = keys.union(set(self._config_parser.options(section)))
        keys = filter(lambda key:key in self.config_keys,keys)
        keys.sort()
        return keys

    # def set_non_persistant(self,key,value) :
    #     if key not in self.config_keys :
    #         raise InvalidConfigurationKey("%s is not a valid configuration key" % key)
    #     self._non_persistant[key] = self._from_type(key,value)

    def save_non_persistant(self) :
        for key in self._non_persistant.keys() :
            if key != '' :
                value = self._non_persistant[key]
                if value is None :
                    del self[key]
                else :
                    self[key] = value
        self.save()

    def process_argv(self,binname=None,argv=None) :
        if binname is not None :
            binpath,binname = os.path.split(binname)
            respath = os.path.join(binpath,'..','res')
            userdatapath = os.path.join(binpath,'..')
            self._non_persistant['binpath'] = binpath
            self._non_persistant['respath'] = respath
            self._non_persistant['userdatapath'] = userdatapath
            self._non_persistant['binname'] = binname
        if argv is not None :
            for arg in argv :
                if arg[:2]=='--' :
                    if '=' in arg :
                        key,value = arg[2:].split('=',1)
                        if key not in self.config_keys :
                            raise InvalidConfigurationKey("%s is not a valid configuration key" % key)
                        self._non_persistant[key] = value
                    else :
                        if arg[-1:] == '-' :
                            key = arg[2:-1]
                            if key not in self.config_keys :
                                raise InvalidConfigurationKey("%s is not a valid configuration key" % key)
                            self._non_persistant[key] = None
                        else :
                            key = arg[2:]
                            if key not in self.config_keys :
                                raise InvalidConfigurationKey("%s is not a valid configuration key" % key)
                            keytype = self.config_keys[key]['type']
                            self._non_persistant[key] = self.config_types[keytype]['from_type'](self.config_types[keytype]['default'])
                else :
                    self._non_persistant[''].append(arg)

    def get_filename(self,filename=None) :
        """Acces to the filename of the configuration file."""
        if filename == None :
            home = os.path.expanduser('~')
            if not os.path.isdir(home) :
                # Now, we're not on unix-like environnement, nor under Win NT/2k/XP, look like Win9x !!!!
                paths_to_test = []
                if 'HOME' in os.environ :
                    paths_to_test.append(os.environ['HOME'])
                if len(sys.argv) >= 1 :
                    exe_path = os.path.split(sys.argv[0])[0]
                    if exe_path == '' :
                        exe_path = '.'
                    paths_to_test.append(exe_path)
                # We're desperate, we didn't find neither somathing looking like a "home" so we try to save config files in tmp dir !!!
                if 'TEMP' in os.environ :
                    paths_to_test.append(os.environ['TEMP'])
                # We're desperate, we didn't find neither somathing looking like a "home" so we try to save config files in tmp dir !!!
                if 'TMP' in os.environ :
                    paths_to_test.append(os.environ['TMP'])
                # As an ultimate try, we'll store this in C:\ !!! At least Win 95 have it (yes, that's Win 95 who is bothering me !)
                paths_to_test.append("C:\\")
                for path in paths_to_test :
                    if os.path.isdir(path) :
                        home = path
                        break
            filename = os.path.join(home,CONFIGURATION_NAME)
        elif self._filename != None :
            filename = self._filename
        return filename

    def load(self,filename=None) :
        filename = self.get_filename(filename)
        if os.path.isfile(filename) :
            self._filename = filename
            self._config_parser.read(filename)

    def save(self,filename=None) :
        filename = self.get_filename(filename)
        handle = open(filename,'wb')
        self._filename = filename
        self._config_parser.write(handle)
        handle.close()
