import socket
import hashlib
try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

from . import (BOXEE_APPLICATION_NAME, BOXEE_SHARED_KEY, BOXEE_UDP_PORT,
               BOXEE_HTTP_PORT_DEFAULT)
from .utils import get_random_string

TIMEOUT = 0.500
BUFFER_SIZE = 1024


class Discoverer(object):
    """Tool to discover any boxee servers on the local network
    following the boxee remote control api"""

    def __init__(self, shared_key=BOXEE_SHARED_KEY, port=BOXEE_UDP_PORT,
                 timeout=TIMEOUT, buffer_size=BUFFER_SIZE,
                 application_name=BOXEE_APPLICATION_NAME):
        self.shared_key = shared_key
        self.port = port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.challenge = get_random_string()
        self.application_name = application_name

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(self.timeout)
        s.bind(('', 0))
        return s

    def _get_signature(self, challenge=None):
        m = hashlib.md5()
        m.update(challenge)
        m.update(self.shared_key)
        return m.hexdigest()

    def send_request(self, sock):
        msg = ('<?xml version="1.0"?>\n'
               '<BDP1 cmd="discover" application="%s" challenge="%s" '
               'signature="%s"/>'
               % (self.application_name, self.challenge,
                  self._get_signature(self.challenge)))
        sock.sendto(msg, ('<broadcast>', self.port))

    def _parse_response(self, resp):
        elem = etree.fromstring(resp)
        if (elem.get("signature", "-invalid-").upper() ==
            self._get_signature(elem.get("response", "")).upper()):
            return {'name': elem.get('name', "boxeebox"),
                    "http_port": int(elem.get("httpPort",
                                              BOXEE_HTTP_PORT_DEFAULT)),
                    "application": elem.get("application", "boxee"),
                    "http_auth_required": (elem.get("httpAuthRequired",
                                                    "false")=="true"),
                    "version": elem.get("version", -1)}
        return None
        
    def recv_responses(self, sock):
        responses = []
        if not self.timeout>0:
            raise ValueError("A timeout is required")
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                responses.append((addr[0], data))
        except socket.timeout:
            pass
        #keeping this 2.6 compatible, so no dict expression
        return dict(i for i in ((ip,self._parse_response(resp))
                                for ip,resp in responses)
                    if i[1] is not None)

    def get_servers(self):
        sock = self._get_socket()
        self.send_request(sock)
        return self.recv_responses(sock)

    __call__ = get_servers


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          description=("lists boxee servers on the "
                                       "local network"))
    args, opts = parser.parse_args()
    d = Discoverer()
    servers = d()
    if len(servers)==0:
        parser.error("no servers found")
    else:
        for server, opts in servers.iteritems():
            print ("%s:%d" % (server, opts.get("http_port", BOXEE_HTTP_PORT_DEFAULT)))
