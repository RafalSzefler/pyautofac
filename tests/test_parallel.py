import pytest

from threading import Thread

from pyautofac import ContainerBuilder
from pyautofac.exceptions import NotInstance, NotSubclass


class Foo:
    pass


class Bar:
    def __init__(self, foo: Foo):
        pass


class Zoo:
    def __init__(self, foo: Foo, bar: Bar):
        pass


def _resolve(container):
    inst = container.resolve(Zoo)


def test_parallel():
    builder = ContainerBuilder()
    builder.register_class(Foo)
    builder.register_class(Bar)
    builder.register_class(Zoo)
    container = builder.build()
    threads = []
    for _ in range(10):
        t = Thread(target=_resolve, args=(container,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    inst = container.resolve(Zoo)
    assert isinstance(inst, Zoo)
