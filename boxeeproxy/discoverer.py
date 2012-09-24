#!/usr/bin/env python
import socket
import hashlib

#somewhat based on http://code.google.com/p/boxeeremote/source/browse/trunk/Boxee%20Remote/src/com/andrewchatham/Discoverer.java
#api at http://developer.boxee.tv/Remote_Control_Interface

BOXEE_APPLICATION_NAME = "boxee"
BOXEE_SHARED_KEY = ""
BOXEE_UDP_PORT = 2562
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
        self.challenge = "foo"
        self.application_name = application_name

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', self.port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(self.timeout)
        return s

    def _get_signature(self):
        m = hashlib.md5()
        m.update(self.challenge)
        m.update(self.shared_key)
        return m.digest()

    def send_request(self, sock):
        msg = ('<?xml version="1.0"?>'
               '<BDP1 cmd="discover" application="%s" challenge="%s" '
               'signature="%s"/>'
               % (self.application_name, self.challenge,
                  self._get_signature()))
        sock.sendto(msg, ('<broadcast>', self.port))

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
        sig = self._get_signature()
        #XXX: verify responses
        return [server for server,packet in responses]

    def get_servers(self):
        sock = self._get_socket()
        self.send_request(sock)
        return self.recv_responses(sock)

    __call__ = get_servers
        
def main():
    import sys
    d = Discoverer()
    servers = d()
    if len(servers)==0:
        print "no servers found"
        sys.exit(1)
    else:
        for server in servers:
            print server

if __name__=="__main__":
    main()
