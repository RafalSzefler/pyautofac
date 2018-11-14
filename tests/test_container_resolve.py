import pytest

from pyautofac import ContainerBuilder
from pyautofac.exceptions import NotSubclass, NotAnnotatedConstructorParam, NotRegistered


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


@pytest.mark.asyncio
async def test_container_resolve():
    org_foo = Foo()
    builder = ContainerBuilder()
    builder.register_instance(org_foo)
    builder.register_class(Bar).as_interface(BarInterface)
    container = builder.build()
    bar = await container.resolve(BarInterface)
    assert bar.foo is org_foo
    assert bar.return_1() == 1


@pytest.mark.asyncio
async def test_container_wrong_instance():
    builder = ContainerBuilder()
    with pytest.raises(NotSubclass):
        builder.register_instance(object()).as_interface(Foo)


@pytest.mark.asyncio
async def test_container_not_subclass():
    builder = ContainerBuilder()
    with pytest.raises(NotSubclass):
        builder.register_class(str).as_interface(BarInterface)


class BrokenConstructor:
    def __init__(self, foo):
        pass


@pytest.mark.asyncio
async def test_broken_constructor():
    builder = ContainerBuilder()
    builder.register_class(BrokenConstructor)
    container = builder.build()
    with pytest.raises(NotAnnotatedConstructorParam):
        await container.resolve(BrokenConstructor)


@pytest.mark.asyncio
async def test_on_the_fly_instance():
    org_foo = Foo()
    builder = ContainerBuilder()
    builder.register_class(Bar).as_interface(BarInterface)
    container = builder.build()
    with pytest.raises(NotRegistered):
        await container.resolve(BarInterface)
    container.add_instance(org_foo)
    await container.resolve(BarInterface)
