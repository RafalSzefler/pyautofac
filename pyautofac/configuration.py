import copy
import os
import json
import sys
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


_TRUE_VALUES = {'1', 'y', 't', 'true', 'yes'}
_FALSE_VALUES = {'0', 'n', 'f', 'false', 'no'}
def parse_bool(data):
    data = data.lower()
    if data in _TRUE_VALUES:
        return True
    if data in _FALSE_VALUES:
        return False
    raise ValueError('Invalid boolean value')


_PARSERS = {
    bool: parse_bool,
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
        try:
            return self._mapping[key]
        except KeyError:
            if default is not _PLACEHOLDER:
                return default
            raise

    def parse_value(self, key, type=str):
        value = self.get(key)
        parser = _PARSERS.get(type, _PLACEHOLDER)
        if parser is _PLACEHOLDER:
            raise TypeError("Don't know how to parse [%s] type." % type)
        return parser(value)

    def get_section(self, prefix):
        result = {}
        for key, value in self._mapping.items():
            if key.startswith(prefix):
                key = key[len(prefix):]
                if not (key != '' and key[0] == _NESTING_SEPARATOR):
                    continue
                key = key[1:].split(_NESTING_SEPARATOR)
                last = key.pop()
                root = result
                for subkey in key:
                    if subkey not in root:
                        root[subkey] = {}
                    root = root[subkey]
                root[last] = value
        return DictConfiguration(result)

    def to_dict(self):
        return copy.deepcopy(self._mapping)

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

    def get(self, key, default=_PLACEHOLDER):
        try:
            return self._mapping[key]
        except KeyError:
            if default is not _PLACEHOLDER:
                return default
            raise

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

    def add_command_line(self, args=None):
        if args is None:
            args = sys.argv[1:]
        args = list(reversed(args))
        result = self._mapping
        while args:
            key = args.pop()
            if not key.startswith('--'):
                continue
            key = key[2:]
            key, sep, value = key.partition('=')
            if sep:
                result[key] = value
                continue
            if not args:
                raise ValueError('Invalid command line arguments')
            value = args.pop()
            if value.startswith('--'):
                raise ValueError('Command line value cannot start with [--]')
            result[key] = value
        self._mapping.update(result)
        return self

    def build(self):
        mapping = self._mapping
        self._mapping = {}
        return DictConfiguration(mapping)
