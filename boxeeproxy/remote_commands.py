#!/usr/bin/env python
import urllib2
import re
import functools

class CommandError(RuntimeError): pass

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
                % (self.__name__, self.host, self.port, self.command))


class CommandBool(Command):

    def handle_response_value(self, response_value):
        if response_value=="OK":
            return True
        raise CommandError("Unexpected response")

def _get_bool_command(command):
    return functools.partial(CommandBool, command=command)

_pause_command = _get_bool_command("Pause")
_stop_command = _get_bool_command("Stop")
_mute_command = _get_bool_command("Mute")
_playnext_command = _get_bool_command("PlayNext")
_playprev_command = _get_bool_command("PlayPrev")

class CommandSetValue(CommandBool):

    def __init__(self, host, port, command, value):
        command = "%s(%d)" % (command, value)
        super(CommandSendKey, self).__init__(host, port, command)

def _get_setval_command(command):
    return functools.partial(CommandSetValue, command=command)    

_setvolume_command = _get_setval_command("SetVolume")
_seekpercentage_command = _get_setval_command("SeekPercentage")
_seekpercentagerelative_command = _get_setval_command("SeekPercentageRelative")

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


        
class CommandSpawner(object):

    def __init__(self, host, port=8800):
        self.host = host
        self.port = port

