from pyrfeed.config.config import ConfigClass

class ConversionException(Exception) :
    pass

class DuplicateDefinition(Exception) :
    pass

def register_type( keytype, from_type=None, from_str=None, from_type_exception=None, from_str_exception=None, ihm_name=None, default=None ) :

    def create_convert_and_catch_function(from_type,to_type,exception) :
        def convert_and_catch(value) :
            try :
                return to_type(value)
            except exception :
                raise ConversionException("Can't convert %r from %s to %s" % (value,from_type,to_type))
        return convert_and_catch

    if from_type is None :
        if from_type_exception is not None :
            from_type = create_convert_and_catch_function(keytype,str,from_type_exception)
    if from_str is None :
        if from_str_exception is not None :
            from_str = create_convert_and_catch_function(str,keytype,from_str_exception)

    if from_type is None :
        from_type = lambda value:str(value)

    if from_str is None :
        from_str = lambda value:keytype(value)

    if ihm_name is None :
        ihm_name = "%s" % keytype

    ConfigClass.config_types[keytype] = {
        'from_type' : from_type,
        'from_str' : from_str,
        'ihm_name' : ihm_name,
        'default' : default
        }

def register_key( name, keytype, doc, default=None, internal=False, advanced=False ) :
    if keytype not in ConfigClass.config_types :
        raise TypeError

    config_key = {
        'name' : name,
        'type' : keytype,
        'doc' : doc,
        'default' : default,
        'internal' : internal,
        'advanced' : advanced,
        }
    if name in ConfigClass.config_keys :
        if config_key != ConfigClass.config_keys[name] :
            raise DuplicateDefinition('Configuration key %r already registered with %s. Trying to register with %s '%(name,ConfigClass.config_keys[name],config_key))

    ConfigClass.config_keys[name] = config_key

register_type( int, from_type_exception=ValueError, ihm_name='integer', default=0 )
register_type( str, ihm_name='string', default='' )

def from_bool_to_str(bool_value) :
    if bool_value :
        return "1"
    return "0"

def from_str_to_bool(str_value) :
    if str_value in ('0',str(False)) :
        return False
    if str_value in ('','1',str(True)) :
        return True
    raise ConversionException("Can't convert %r from %s to %s" % (str_value,'str','bool'))

register_type( bool, from_type=from_bool_to_str, from_str=from_str_to_bool, ihm_name='boolean', default=True )

