import typing


class Cache(object):
    def __init__(self):
        self._data: typing.Dict[str, typing.Any] = {}

    def set(self, key: str, value: None):
        self._data[key] = value

    def get(self, key: str):
        if key not in self._data:
            raise ValueError(f"{key} not in cache")
        return self._data.get(key)

    def check(self, name: str):
        if name in self._data:
            raise ValueError(f"{name} already in cache, plz change it")

    def scan(self, type: str = "") -> dict:
        if type:
            return [self._data[d] for d in self._data if d.startswith(type)]
        return self._data

    def clear(self):
        self._data = {}


cache = Cache()
