

class Redis:
    _data = {}

    def __init__(self, *args, **kwargs):
        pass

    def set(self, key, val, *args, **kwargs):
        self._data[key] = val

    def get(self, key, *args, **kwargs):
        return self._data.get(key)
