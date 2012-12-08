#!/usr/bin/env python
import urllib2
import re
import functools

from . import BOXEE_HTTP_PORT_DEFAULT, CommandError

class Command(object):

    RESPONSE_EXPR = re.compile(r"<html>\n<li>(.*?)</html>")

    def __init__(self, host, port, command):
        self.host = host
        self.port = port
        self.command = command
        self.url = ("http://%s:%d/xbmcCmds/xbmcHttp?command=%s"
                    % (host, port, command))

    def send_request(self):
        try:
            return urllib2.urlopen(self.url)
        except urllib2.URLError, e:
            raise CommandError(e)

    def extract_response_value(self, response_text):
        m = self.RESPONSE_EXPR.match(response_text)
        if m:
            return m.groups()[0]
        return None

    def handle_response_value(self, response_value):
        raise NotImplementedError("command sub-classes required")

    def handle_response(self, response):
        response_text = self.extract_response_value(response.read())
        if response.getcode()==200 and response_text is not None:
            if response_text.startswith("Error:"):
                raise CommandError(response_text.split(":", 1)[1].strip())
            return response_text
        return None
    
    def run(self):
        resp = self.send_request()
        resp_value = self.handle_response(resp)
        return self.handle_response_value(resp_value)

    def __unicode__(self):
        return self.command

    def __repr__(self):
        return (u'<%s host="%s" port=%s command="%s">'
                % (self.__class__.__name__, self.host, self.port, self.command))


class CommandBool(Command):

    def handle_response_value(self, response_value):
        if response_value=="OK":
            return True
        raise CommandError("Unexpected response")

def _get_bool_command(command):
    return functools.partial(CommandBool, command=command)

_command_pause = _get_bool_command("Pause")
_command_stop = _get_bool_command("Stop")
_command_mute = _get_bool_command("Mute")
_command_playnext = _get_bool_command("PlayNext")
_command_playprev = _get_bool_command("PlayPrev")

class CommandSetValue(CommandBool):

    def __init__(self, host, port, command, value):
        command = "%s(%d)" % (command, value)
        super(CommandSendKey, self).__init__(host, port, command)

def _get_setval_command(command):
    return functools.partial(CommandSetValue, command=command)    

_command_setvolume = _get_setval_command("SetVolume")
_command_seekpercentage = _get_setval_command("SeekPercentage")
_command_seekpercentagerelative = _get_setval_command("SeekPercentageRelative")

class CommandSendKey(CommandBool):

    def __init__(self, host, port, key_code):
        command = "SendKey(%d)" % key_code
        super(CommandSendKey, self).__init__(host, port, command)


class CommandSendKeyAscii(CommandSendKey):

    def __init__(self, host, port, char):
        super(CommandSendKeyAscii, self).__init__(host, port,
                                                  61696 + org(char))


def _get_key_command(code):
    return functools.partial(CommandSendKey, key_code=code)

_command_select = _get_key_command(256)
_command_back = _get_key_command(257)
_command_up = _get_key_command(270)
_command_down = _get_key_command(271)
_command_left = _get_key_command(272)
_command_right = _get_key_command(273)
_command_backspace = _get_key_command(61704)

def _string_to_commands(host, port, a_str):
    for char in a_str:
        yield CommandSendKeyAscii(host, port, char)


class CommandInt(Command):

    def handle_response_value(self, response_value):
        try:
            return int(response_value)
        except ValueError:
            raise CommandError("Could not parse response '%s'"
                               % response_value)


def _get_int_command(command):
    return functools.partial(CommandInt, command=command)

_command_getvolume = _get_int_command("GetVolume")
_command_getpercentage = _get_int_command("GetPercentage")

_commands = {
    "pause": _command_pause,
    "stop": _command_stop,
    "mute": _command_mute,
    "playnext": _command_playnext,
    "playprev": _command_playprev,
    "setvolume": _command_setvolume,
    "seekpercentage": _command_seekpercentage,
    "seekpercentagerelative": _command_seekpercentagerelative,
    "select": _command_select,
    "back": _command_back,
    "up": _command_up,
    "down": _command_down,
    "left": _command_left,
    "right": _command_right,
    "backspace": _command_backspace,
    "getvolume": _command_getvolume,
    "getpercentage": _command_getpercentage,
    }

        
class CommandSpawner(object):

    def __init__(self, host, http_port=BOXEE_HTTP_PORT_DEFAULT,
                 command_queue=None):
        self.host = host
        self.http_port = http_port
        self._command_args = [self.host, self.http_port]
        self.command_queue = None

    def _handle_command(self, command, command_value=None):
        command_args = self._command_args
        command_kwargs = {}
        if command_value is not None:
            command_kwargs['value'] = command_value
        #XXX: this is really messy
        if self.commandQueue:
            pass
        else:
            return command(*command_args, **command_kwargs)

    @classmethod
    def from_discovery_result(cls, host, discovery_keys, command_queue=None):
        return cls(host,
                   discovery_keys.get("http_port", BOXEE_HTTP_PORT_DEFAULT),
                   command_queue)

