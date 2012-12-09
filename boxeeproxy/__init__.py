BOXEE_APPLICATION_NAME = "iphone_remote"
BOXEE_SHARED_KEY = "b0xeeRem0tE!"
BOXEE_UDP_PORT = 2562
BOXEE_HTTP_PORT_DEFAULT = 8800

class CommandError(RuntimeError): pass

from .discoverer import Discoverer
from .remote_commands import CommandSpawner, CommandInterface

def main():
    from optparse import OptionParser
    usage = "%prog [options] [command]..]"
    desc = (
"""Send remote control commands to a boxee server. Available commands can be
listed out, and values can be passed with a "command:value" format. In addition
to the listed commands, most commands can be set to run serveral times by
giving the command as "command_n" where "n" is the desired number of times to 
run the given command.
""")
    parser = OptionParser(usage=usage, description=desc)
    parser.add_option("-H", "--host",
                      help=("Host to send commands to. If not selected, "
                            "one is auto-selected. See `boxee_discover`."))
    parser.add_option("-p", "--port", default=BOXEE_HTTP_PORT_DEFAULT,
                      type="int", help=("Http port to use (default: %default)"))
    parser.add_option("-l", "--list-commands", default=False, action="store_true",
                      help=("list available commands"))
    opts, args = parser.parse_args()
    if opts.list_commands:
        ci = CommandInterface(None)
        for command in dir(ci):
            print command
        parser.exit()
    if not opts.host:
        d = Discoverer()
        res = d()
        if len(res):
            spawner = CommandSpawner.from_discovery_result(*res.iteritems()
                                                           .next())
        else:
            parser.error("no servers found")
    else:
        spawner = CommandSpawner(opts.host, opts.port)
    ci = CommandInterface(spawner)
    def print_res(res):
        if not isinstance(res, bool):
            print res
    for arg in args:
        val = None
        if ":" in arg:
            arg, val = arg.split(":", 1)
        cmd = getattr(ci, arg, None)
        if cmd is not None:
            cmd(command_value=val, cb=print_res)
        else:
            parser.error("unknown command '%s'" % arg)
                      
    
                            
