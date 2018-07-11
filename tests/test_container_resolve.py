import pytest

from pyautofac import ContainerBuilder
from pyautofac.exceptions import NotInstance, NotSubclass, NotAnnotatedConstructorParam


class Foo:
    pass


class BarInterface:
    def return_1(self):
        return 0


class Bar(BarInterface):
    def __init__(self, foo: Foo):
        self.foo = foo

    def return_1(self):
        return 1


def test_container_resolve():
    org_foo = Foo()
    builder = ContainerBuilder()
    builder.register_instance(org_foo)
    builder.register_class(Bar).as_interface(BarInterface)
    container = builder.build()
    bar = container.resolve(BarInterface)
    assert bar.foo is org_foo
    assert bar.return_1() == 1


def test_container_wrong_instance():
    builder = ContainerBuilder()
    builder.register_instance(object()).as_interface(Foo)
    container = builder.build()
    with pytest.raises(NotInstance):
        container.resolve(Foo)


def test_container_not_subclass():
    builder = ContainerBuilder()
    builder.register_class(str).as_interface(BarInterface)
    container = builder.build()
    with pytest.raises(NotSubclass):
        container.resolve(BarInterface)


class BrokenConstructor:
    def __init__(self, foo):
        pass


def test_broken_constructor():
    builder = ContainerBuilder()
    builder.register_class(BrokenConstructor)
    container = builder.build()
    with pytest.raises(NotAnnotatedConstructorParam):
        container.resolve(BrokenConstructor)