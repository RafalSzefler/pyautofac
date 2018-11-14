import pytest

from pyautofac import ContainerBuilder
from pyautofac.exceptions import NotSubclass, NotAnnotatedConstructorParam


class Singleton:
    def test(self):
        return 1


class IFoo:
    def return_1(self):
        return 'test'


class Foo(IFoo):
    def return_1(self):
        return 'test'


@pytest.mark.asyncio
async def test_single_instance():
    builder = ContainerBuilder()
    builder.register_class(Foo).as_interface(IFoo)
    builder.register_class(Singleton).single_instance()
    container = builder.build()
    s1 = await container.resolve(Singleton)
    s2 = await container.resolve(Singleton)
    assert s1 is s2


@pytest.mark.asyncio
async def test_single_instance_from_nested():
    builder = ContainerBuilder()
    builder.register_class(Foo).as_interface(IFoo)
    builder.register_class(Singleton).single_instance()
    container = builder.build()
    nested = container.create_nested()
    s1 = await container.resolve(Singleton)
    s2 = await nested.resolve(Singleton)
    assert s1 is s2


@pytest.mark.asyncio
async def test_cached():
    builder = ContainerBuilder()
    builder.register_class(Foo).as_interface(IFoo)
    builder.register_class(Singleton).single_instance()
    container = builder.build()
    s1 = await container.resolve(IFoo)
    s2 = await container.resolve(IFoo)
    assert s1 is s2


@pytest.mark.asyncio
async def test_nesting_no_singleton():
    builder = ContainerBuilder()
    builder.register_class(Foo).as_interface(IFoo)
    builder.register_class(Singleton).single_instance()
    container = builder.build()
    nested = container.create_nested()
    s1 = await container.resolve(IFoo)
    s2 = await nested.resolve(IFoo)
    assert s1 is not s2
