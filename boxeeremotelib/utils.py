import random


class MultiResultCallbackHandler(object):

    def __init__(self, cb=None):
        self._count = 0
        self._results = []
        self._cb = cb
        def result_cb(res):
            self._results.append(res)
            if len(self._results)==self._count:
                self._fire()
        self._result_cb = result_cb

    def _fire(self):
        if self._cb:
            self._cb(self._results)

    def get_cb(self):
        self._count+=1
        return self._result_cb


class MultiBoolCallbackHandler(MultiResultCallbackHandler):

    def _fire(self):
        if self._cb:
            self._cb(all(self._results))
        
        
def get_random_string(min_length=5, max_length=15):
    chrs = [chr(x) for x in range(ord('A'), ord('Z')+1)]
    chrs.extend([chr(x) for x in range(ord('a'), ord('z')+1)])
    return ''.join(random.choice(chrs) for i in
                   xrange(random.randint(min_length, max_length)))
