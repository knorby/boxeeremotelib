BOXEE_APPLICATION_NAME = "iphone_remote"
BOXEE_SHARED_KEY = "b0xeeRem0tE!"
BOXEE_UDP_PORT = 2562
BOXEE_HTTP_PORT_DEFAULT = 8800

class CommandError(RuntimeError): pass

from .discoverer import Discoverer
from .remote_commands import CommandSpawner, CommandInterface
