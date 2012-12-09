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
        
        
