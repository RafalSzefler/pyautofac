import pytest

from pyautofac import ContainerBuilder, IAsyncResource
from pyautofac.exceptions import NotSubclass, NotAnnotatedConstructorParam


class Singleton(IAsyncResource):
    def __init__(self, messages: list):
        self.messages = messages

    async def initialize(self):
        self.messages.append('singleton-init')

    async def dispose(self, exc=None):
        self.messages.append('singleton-dispose')


class IFoo:
    def return_1(self):
        return 'test'


class Foo(IFoo, IAsyncResource):
    def __init__(self, messages: list):
        self.messages = messages

    async def initialize(self):
        self.messages.append('foo-init')

    async def dispose(self, exc=None):
        self.messages.append('foo-dispose')


class Bar(IAsyncResource):
    def __init__(self, messages: list, singleton: Singleton):
        self.messages = messages

    async def initialize(self):
        self.messages.append('bar-init')

    async def dispose(self, exc=None):
        self.messages.append('bar-dispose')


@pytest.mark.asyncio
async def test_async_resource():
    messages = []
    builder = ContainerBuilder()
    builder.register_instance(messages).as_interface(list)
    builder.register_class(Foo).as_interface(IFoo)
    container = builder.build()
    instance = await container.resolve(IFoo)
    await container.dispose()
    assert messages == ['foo-init', 'foo-dispose']


@pytest.mark.asyncio
async def test_async_resource_nested():
    messages = []
    builder = ContainerBuilder()
    builder.register_instance(messages).as_interface(list)
    builder.register_class(Singleton).single_instance()
    builder.register_class(Foo).as_interface(IFoo)
    container = builder.build()
    nested = container.create_nested()
    assert messages == []
    await nested.resolve(Singleton)
    assert messages == ['singleton-init']
    await nested.resolve(IFoo)
    assert messages == ['singleton-init', 'foo-init']
    await nested.dispose()
    assert messages == ['singleton-init', 'foo-init', 'foo-dispose']
    await container.dispose()
    assert messages == ['singleton-init', 'foo-init', 'foo-dispose', 'singleton-dispose']


@pytest.mark.asyncio
async def test_async_resource_dependency():
    messages = []
    builder = ContainerBuilder()
    builder.register_instance(messages).as_interface(list)
    builder.register_class(Singleton).single_instance()
    builder.register_class(Bar).single_instance()
    container = builder.build()
    await container.resolve(Bar)
    await container.dispose()
    assert messages == ['singleton-init', 'bar-init', 'bar-dispose', 'singleton-dispose']


@pytest.mark.asyncio
async def test_async_resource_context_manager():
    messages = []
    builder = ContainerBuilder()
    builder.register_instance(messages).as_interface(list)
    builder.register_class(Singleton).single_instance()
    builder.register_class(Bar).single_instance()
    async with builder.build() as container:
        await container.resolve(Bar)
    assert messages == ['singleton-init', 'bar-init', 'bar-dispose', 'singleton-dispose']