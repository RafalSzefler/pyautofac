import os
import json
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
try:
    import ujson
except ImportError:
    ujson = json


_PLACEHOLDER = object()
class IConfiguration(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key, default=_PLACEHOLDER):
        raise NotImplementedError()

    @abstractmethod
    def parse_value(self, key, type=str):
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()


def parse_timedelta(value):
    if not value:
        raise ValueError('Invalid timedelta')
    value = value.split(':')
    value.reverse()
    seconds = int(value[0])
    if seconds < 0 or seconds >= 60:
        raise ValueError('Invalid timedelta')
    minutes = 0
    hours = 0

    try:
        minutes = int(value[1])
        if minutes < 0 or minutes >= 60:
            raise ValueError('Invalid timedelta')
    except IndexError:
        pass

    try:
        hours = int(value[2])
        if hours < 0:
            raise ValueError('Invalid timedelta')
    except IndexError:
        pass
    return timedelta(seconds=seconds, minutes=minutes, hours=hours)


def parse_datetime(value):
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return datetime.strptime(value, '%Y-%m-%d')


_PARSERS = {
    str: lambda value: value,
    int: lambda value: int(value),
    float: lambda value: float(value),
    json: lambda value: json.loads(value),
    ujson: lambda value: ujson.loads(value),
    datetime: parse_datetime,
    timedelta: parse_timedelta,
}
class DictConfiguration(IConfiguration):
    def __init__(self, mapping):
        self._mapping = mapping

    def get(self, key, default=_PLACEHOLDER):
        value = self._mapping.get(key)
        if value is _PLACEHOLDER:
            raise KeyError(key)
        return value

    def parse_value(self, key, type=str):
        value = self.get(key)
        parser = _PARSERS[type]
        return parser(value)

    def __getitem__(self, key):
        return self._mapping[key]



def read_file(path, processor, optional):
    if not isinstance(path, (str, bytes)):
        if optional:
            return {}
        raise ValueError('Invalid file path passed to configuration.')
    if not os.path.exists(path):
        if not optional:
            open(path)  # will raise
        return {}
    with open(path) as fo:
        return processor(fo)


_NESTING_SEPARATOR = ':'
def flatten_dict(dct, prefix=[], result={}):
    for key, value in dct.items():
        prefix_copy = prefix[:]
        prefix_copy.append(key)
        if isinstance(value, dict):
            flatten_dict(value, prefix_copy, result)
        else:
            new_key = _NESTING_SEPARATOR.join(prefix_copy)
            result[new_key] = str(value)
    return result


_ENV_KEY_SEPARTOR = '__'
class ConfigurationBuilder:
    def __init__(self):
        self._mapping = {}

    def add_dict(self, dct):
        if not isinstance(dct, dict):
            raise TypeError('dct is not a dict')
        flatten = flatten_dict(dct)
        self._mapping.update(flatten)
        return self

    def add_yaml_file(self, path, optional=False):
        try:
            from yaml import load
        except ImportError:
            raise ImportError('[add_yaml_file] method requires PyYAML package')

        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader
        processor = lambda fo: load(fo, Loader=Loader)
        data = read_file(path, processor, optional)
        self.add_dict(data)
        return self

    def add_json_file(self, path, optional=False):
        data = read_file(path, ujson.load, optional)
        self.add_dict(data)
        return self

    def add_environment_variables(self, prefix=None):
        env = os.environ
        keys = list(self._mapping.keys())
        for k in keys:
            new_key = k.replace(_NESTING_SEPARATOR, _ENV_KEY_SEPARTOR)
            if prefix is not None:
                new_key = prefix + _ENV_KEY_SEPARTOR + new_key
            try:
                value = env[new_key]
            except KeyError:
                continue
            self._mapping[k] = value
        return self

    def build(self):
        mapping = self._mapping
        self._mapping = {}
        return DictConfiguration(mapping)
