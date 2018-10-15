import os
import json
from contextlib import contextmanager
from datetime import timedelta

from pyautofac import ConfigurationBuilder


ROOT = os.path.abspath(os.path.dirname(__file__))

@contextmanager
def env_var(key, value):
    if key in os.environ:
        raise RuntimeError('Env variable [%s] already defined' % key)
    try:
        os.environ[key] = value
        yield
    finally:
        del os.environ[key]


def test_configuration_builder():
    path = os.path.join(ROOT, 'config.json')
    config = ConfigurationBuilder()  \
        .add_json_file(path)  \
        .add_json_file('test.json', optional=True)  \
        .build()
    
    assert config['foo-key'] == 'bar-value'


def test_configuration_builder_with_env():
    with env_var('Nested__Bar', 'abc'):
        path = os.path.join(ROOT, 'config.json')
        config = ConfigurationBuilder()  \
            .add_json_file(path)  \
            .add_environment_variables()  \
            .build()
        assert config['Nested.Bar'] == 'abc'


def test_configuration_builder_with_env_prefix():
    with env_var('ABC__Nested__Bar', 'abc'):
        path = os.path.join(ROOT, 'config.json')
        config = ConfigurationBuilder()  \
            .add_json_file(path)  \
            .add_environment_variables(prefix='ABC')  \
            .build()
    
        assert config['Nested.Bar'] == 'abc'


def test_configuration_builder_with_overwritten_env():
    with env_var('foo-key', 'test'):
        path = os.path.join(ROOT, 'config.json')
        config = ConfigurationBuilder()  \
            .add_json_file(path)  \
            .add_environment_variables()  \
            .build()
        assert config['foo-key'] == 'test'


def test_configuration_builder_with_overwritten_env2():
    with env_var('foo-key', 'test'):
        path = os.path.join(ROOT, 'config.json')
        config = ConfigurationBuilder()  \
            .add_environment_variables()  \
            .add_json_file(path)  \
            .build()
    
        assert config['foo-key'] == 'bar-value'


def test_configuration_builder_parsing():
    path = os.path.join(ROOT, 'config.json')
    config = ConfigurationBuilder()  \
        .add_json_file(path)  \
        .add_json_file('test.json', optional=True)  \
        .build()
    assert config.parse_value('value', int) == 111
    assert config.parse_value('json', json) == {'x': None}
    assert config.parse_value('time', timedelta) == timedelta(seconds=15, hours=123)
