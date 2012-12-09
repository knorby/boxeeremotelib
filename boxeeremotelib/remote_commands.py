#!/usr/bin/env python
import urllib2
import re
import functools

from . import BOXEE_HTTP_PORT_DEFAULT, CommandError
from .utils import MultiBoolCallbackHandler

class Command(object):

    RESPONSE_EXPR = re.compile(r"<html>\n<li>(.*?)</html>")

    def __init__(self, host, port, command):
        self.host = host
        self.port = port
        self.command = command
        self._url = ("http://%s:%d/xbmcCmds/xbmcHttp?command=%s"
                     % (host, port, command))

    def get_url(self):
        return self._url

    def extract_response_value(self, response_text):
        m = self.RESPONSE_EXPR.match(response_text)
        if m:
            return m.groups()[0]
        return None

    def handle_response_value(self, response_value):
        raise NotImplementedError("command sub-classes required")

    def _handle_response(self, response):
        response_text = self.extract_response_value(response.read())
        if response.getcode()==200 and response_text is not None:
            if response_text.startswith("Error:"):
                raise CommandError(response_text.split(":", 1)[1].strip())
            return response_text
        return None

    def handle_response(self, response):
        resp_value = self._handle_response(response)
        return self.handle_response_value(resp_value)
            
    def run(self):
        resp = self.send_request()

    def __unicode__(self):
        return self.command

    def __repr__(self):
        return (u'<%s host="%s" port=%s command="%s">'
                % (self.__class__.__name__, self.host, self.port,
                   self.command))


def simple_command_runner(cmd, cb=None):
    try:
        res = cmd.handle_response(urllib2.urlopen(cmd.get_url()))
        if cb:
            cb(res)
    except urllib2.URLError, e:
        raise CommandError(e)


class CommandBool(Command):

    def handle_response_value(self, response_value):
        if response_value=="OK":
            return True
        raise CommandError("Unexpected response")

def _get_bool_command(command):
    return functools.partial(CommandBool, command=command)


_COMMAND_PAUSE = _get_bool_command("Pause")
_COMMAND_STOP = _get_bool_command("Stop")
_COMMAND_MUTE = _get_bool_command("Mute")
_COMMAND_PLAYNEXT = _get_bool_command("PlayNext")
_COMMAND_PLAYPREV = _get_bool_command("PlayPrev")


class CommandSetValue(CommandBool):

    def __init__(self, host, port, command, value):
        command = "%s(%s)" % (command, int(value))
        super(CommandSetValue, self).__init__(host, port, command)


def _get_setval_command(command):
    return functools.partial(CommandSetValue, command=command)    

_COMMAND_SETVOLUME = _get_setval_command("SetVolume")
_COMMAND_SEEKPERCENTAGE = _get_setval_command("SeekPercentage")
_COMMAND_SEEKPERCENTAGERELATIVE = _get_setval_command("SeekPercentageRelative")

class CommandSendKey(CommandBool):

    def __init__(self, host, port, key_code):
        command = "SendKey(%d)" % key_code
        super(CommandSendKey, self).__init__(host, port, command)


class CommandSendKeyAscii(CommandSendKey):

    def __init__(self, host, port, char):
        super(CommandSendKeyAscii, self).__init__(host, port,
                                                  61696 + ord(char))


def _get_key_command(code):
    return functools.partial(CommandSendKey, key_code=code)

_COMMAND_SELECT = _get_key_command(256)
_COMMAND_BACK = _get_key_command(257)
_COMMAND_UP = _get_key_command(270)
_COMMAND_DOWN = _get_key_command(271)
_COMMAND_LEFT = _get_key_command(272)
_COMMAND_RIGHT = _get_key_command(273)
_COMMAND_BACKSPACE = _get_key_command(61704)

def _string_to_commands(a_str):
    for char in a_str:
        yield functools.partial(CommandSendKeyAscii, char=char)

class CommandInt(Command):

    def handle_response_value(self, response_value):
        try:
            return int(response_value)
        except ValueError:
            raise CommandError("Could not parse response '%s'"
                               % response_value)


def _get_int_command(command):
    return functools.partial(CommandInt, command=command)

_COMMAND_GETVOLUME = _get_int_command("GetVolume")
_COMMAND_GETPERCENTAGE = _get_int_command("GetPercentage")

_SET_COMMANDS = {
    "setvolume": _COMMAND_SETVOLUME,
    "seekpercentage": _COMMAND_SEEKPERCENTAGE,
    "seekpercentagerelative": _COMMAND_SEEKPERCENTAGERELATIVE,
    }    

_COMMANDS = {
    "pause": _COMMAND_PAUSE,
    "stop": _COMMAND_STOP,
    "mute": _COMMAND_MUTE,
    "playnext": _COMMAND_PLAYNEXT,
    "playprev": _COMMAND_PLAYPREV,
    "select": _COMMAND_SELECT,
    "back": _COMMAND_BACK,
    "up": _COMMAND_UP,
    "down": _COMMAND_DOWN,
    "left": _COMMAND_LEFT,
    "right": _COMMAND_RIGHT,
    "backspace": _COMMAND_BACKSPACE,
    "getvolume": _COMMAND_GETVOLUME,
    "getpercentage": _COMMAND_GETPERCENTAGE,
    }

_META_COMMANDS = {
    "setstring": _string_to_commands,
    }
        
class CommandSpawner(object):

    def __init__(self, host, http_port=BOXEE_HTTP_PORT_DEFAULT):
        self.host = host
        self.http_port = http_port
        self._command_args = [self.host, self.http_port]

    def _handle_command(self, command, command_value=None):
        command_args = self._command_args
        command_kwargs = {}
        if command_value is not None:
            command_kwargs['value'] = command_value
        return command(*command_args, **command_kwargs)

    @classmethod
    def from_discovery_result(cls, host, discovery_keys):
        return cls(host,
                   discovery_keys.get("http_port", BOXEE_HTTP_PORT_DEFAULT))


class CommandInterface(object):

    def __init__(self, command_spawner, command_handler=simple_command_runner):
        self.command_spawner = command_spawner
        self.command_handler = command_handler

    def _single_wrapper(self, cmd, name, setter=False):
        if setter:
            def run(command_value=None, cb=None, **kwargs):
                comp = self.command_spawner._handle_command(cmd, command_value)
                self.command_handler(comp, cb)
        else:
            def run(cb=None, **kwargs):
                comp = self.command_spawner._handle_command(cmd)
                self.command_handler(comp, cb)
        run.__name__ = name
        return run

    def _multi_wrapper(self, cmds, name, meta=False):
        if not meta:
            def run(cb=None, **kwargs):
                multi_cb = MultiBoolCallbackHandler(cb)
                for cmd in cmds:
                    comp = self.command_spawner._handle_command(cmd)
                    self.command_handler(comp, multi_cb.get_cb())
        else:
            def run(command_value=None, cb=None, **kwargs):
                multi_cb = MultiBoolCallbackHandler(cb)
                for cmd in cmds(command_value):
                    comp = self.command_spawner._handle_command(cmd)
                    self.command_handler(comp, multi_cb.get_cb())
        run.__name__ = name
        return run
        
    def __dir__(self):
        listing = _COMMANDS.keys()
        listing.extend(_SET_COMMANDS.keys())
        listing.extend(_META_COMMANDS.keys())
        return listing

    def __getattr__(self, attr_name):
        if attr_name in _COMMANDS:
            return self._single_wrapper(_COMMANDS[attr_name], attr_name)
        elif attr_name in _SET_COMMANDS:
            return self._single_wrapper(_SET_COMMANDS[attr_name], attr_name,
                                        True)
        elif attr_name in _META_COMMANDS:
            return self._multi_wrapper(_META_COMMANDS[attr_name], attr_name,
                                       True)
        elif "_" in attr_name:
            command_name, num = attr_name.split("_", 1)
            if num.isdigit() and command_name in _COMMANDS:
                cmd = _COMMANDS[command_name]
                return self._multi_wrapper((cmd for i in xrange(int(num))),
                                           attr_name)
        raise AttributeError("Unknown Command")
