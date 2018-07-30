import os
try:
    import ujson as json
except ImportError:
    import json


class IConfiguration:
    def get(self, key, default=None):
        raise NotImplementedError()

    def __getitem__(self, key):
        raise NotImplementedError()


class DictConfiguration(IConfiguration):
    def __init__(self, mapping):
        self._mapping = mapping

    def get(self, key, default=None):
        return self._mapping.get(key, default)

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


class ConfigurationBuilder:
    def __init__(self):
        self._mapping = {}

    def add_dict(self, dct):
        self._mapping.update(dct)
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
        self._mapping.update(data)
        return self

    def add_json_file(self, path, optional=False):
        data = read_file(path, json.load, optional)
        self._mapping.update(data)
        return self

    def add_environment_variables(self, prefix=None):
        env = os.environ
        for k in env:
            value = env[k]
            if prefix is not None:
                if not k.startswith(prefix):
                    continue
                k = k[len(prefix):]
            try:
                value = json.loads(value)
            except Exception:
                pass
            self._mapping[k] = value
        return self

    def build(self):
        mapping = self._mapping
        self._mapping = {}
        return DictConfiguration(mapping)
