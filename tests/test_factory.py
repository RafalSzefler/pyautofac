import pytest

from pyautofac import ContainerBuilder, Factory
from pyautofac.exceptions import NotSubclass, NotAnnotatedConstructorParam


class Bar:
    pass


class Foo:
    def __init__(self, factory: Factory[Bar]):
        self.factory = factory

    async def get_bar(self):
        return await self.factory()


@pytest.mark.asyncio
async def test_factory_1():
    builder = ContainerBuilder()
    builder.register_class(Foo)
    builder.register_class(Bar)
    container = builder.build()
    foo = await container.resolve(Foo)
    b1 = await foo.get_bar()
    b2 = await foo.get_bar()
    assert b1 is not b2


@pytest.mark.asyncio
async def test_factory_2():
    builder = ContainerBuilder()
    builder.register_class(Foo)
    builder.register_class(Bar).per_lifetime()
    container = builder.build()
    foo = await container.resolve(Foo)
    b1 = await foo.get_bar()
    b2 = await foo.get_bar()
    assert b1 is b2
