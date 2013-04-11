import sys
import cProfile
from pyrfeed.config import config
from pyrfeed.config import register_key

__version__ = '0.5.1'

# ------------------------------------------------------------
# This is not a plugin based yet because of those imports.
# Those imports will auto-register pseudo-plugins to the
# pyrfeed framework. A run-time import would also work
# (and this would be real plugin)
# ------------------------------------------------------------
import pyrfeed.gui.command_line
import pyrfeed.gui.wx

import pyrfeed.rss_reader.google_direct
import pyrfeed.rss_reader.google_cache
import pyrfeed.rss_reader.fake
# ------------------------------------------------------------

# ------------------------------------------------------------
from pyrfeed.help import usage
from pyrfeed.help import usage_advanced
from pyrfeed.config import config
from pyrfeed.gui.info_list import gui_info_list
from pyrfeed.rss_reader.info_list import rssreader_info_list
# ------------------------------------------------------------

def pyrfeed_main() :
    # Due to profiling usage, those import should be done here and not
    # on the global space.

    from pyrfeed.help import usage
    # from pyrfeed.config import config
    from pyrfeed.gui.info_list import gui_info_list
    from pyrfeed.rss_reader.info_list import rssreader_info_list

    if config['help-advanced'] :
        usage_advanced()
    elif config['help'] :
        usage()
    elif config['save'] :
        del config['save']
        config.save_non_persistant()
    else :
        rss_reader = rssreader_info_list.get_rss_reader(config)

        if config['forcesynchro'] :
            rss_reader.synchro()
        else :
            gui_info_list.mainloop(config,rss_reader)

def main(binname=None,argv=None) :
    if binname is None :
        if len(sys.argv) > 0 :
            binname = sys.argv[0]
        else :
            binname = '.'
    if argv is None :
        argv = sys.argv[1:]
    config.process_argv(binname,argv)

    if config['profile'] :
        cProfile.run(pyrfeed_main.func_code)
    else :
        pyrfeed_main()

register_key('help',bool,doc='Show help')
register_key('help-advanced',bool,doc='Show help for advanced options')
register_key('save',bool,doc='Save the options in command line into configuration file', advanced=True)
register_key('forcesynchro',bool,doc='Force synchronisation and stop without interactive GUI.', advanced=True)
register_key('profile',bool,doc='Profile the current application. Developer only.', advanced=True)

if __name__ == '__main__' :
    main()
