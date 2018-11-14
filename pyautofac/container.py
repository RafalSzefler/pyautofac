import inspect
from asyncio import Future
from abc import ABCMeta, abstractmethod
from threading import Lock

from pyautofac.async_resource import IAsyncResource
from pyautofac.exceptions import (
    AlreadyRegistered, NotRegistered, NotAnnotatedConstructorParam, NotSubclass,
)
from pyautofac.globals import Tags
from pyautofac.factory import TypeFactory

get_type = type
_PLACEHOLDER = object()

def get_constructor_params(cls):
    ctr = cls.__init__
    try:
        ann = ctr.__annotations__
    except AttributeError:
        return
    params = inspect.signature(ctr).parameters
    iter_params = iter(params)
    next(iter_params)  # ignore self
    for p in iter_params:
        if p not in ann:
            raise NotAnnotatedConstructorParam(p)
        yield ann[p]


class IContainer(metaclass=ABCMeta):
    @abstractmethod
    def add_instance(self, instance, type=None):
        raise NotImplementedError()

    @abstractmethod
    async def resolve(self, cls):
        raise NotImplementedError()

    @abstractmethod
    async def dispose(self, exc=None):
        raise NotImplementedError()

    @abstractmethod
    def create_nested(self, tag=None):
        raise NotImplementedError()

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError()


class DummyContainer(IContainer):
    async def resolve(self, cls):
        raise NotRegistered()

    async def dispose(self, exc=None):
        raise NotImplementedError()

    def create_nested(self, tag=None):
        raise NotImplementedError()

    def add_instance(self, instance, type=None):
        raise NotImplementedError()

    async def __aenter__(self):
        raise NotImplementedError()

    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError()


class FactoryResolver(TypeFactory):
    def __init__(self, type, container):
        self.type = type
        self.container = container

    def __call__(self):
        return self.container.resolve(self.type)


class Container(IContainer):
    def __init__(self, proxy_mapping, parent, tag=Tags.SingleInstance):
        self._cache = {}
        self._mapping = proxy_mapping
        self._parent = parent
        self._tag = tag
        self._lock = Lock()
        self._to_dispose = []

    def create_nested(self):
        return Container(self._mapping, self, Tags.Lifetime)

    async def dispose(self, exc=None):
        for inst in reversed(self._to_dispose):
            await inst.dispose(exc)

    async def resolve(self, cls):
        with self._lock:
            if cls in self._cache:
                return self._cache[cls]

        proxy = self._mapping.get(cls)
        if proxy is None:
            raise NotRegistered()

        instance = getattr(proxy, 'instance', _PLACEHOLDER)
        if instance is not _PLACEHOLDER:
            with self._lock:
                self._cache[cls] = instance
            return instance

        type = proxy.registered_type
        params = get_constructor_params(type)
        def resolver_builder(param):
            if issubclass(param, TypeFactory):
                def resolver():
                    fut = Future()
                    fut.set_result(FactoryResolver(param.SUB_TYPE, self))
                    return fut
            else:
                def resolver():
                    return self.resolve(param)
            return resolver
        resolvers = [resolver_builder(param) for param in params]            
        async def factory():
            dependencies = []
            for resolver in resolvers:
                dependencies.append(await resolver())
            instance = type(*dependencies)
            if isinstance(instance, IAsyncResource):
                await instance.initialize()
                self._to_dispose.append(instance)
            return instance

        if proxy.tag is Tags.AlwaysNew:
            return await factory()

        if proxy.tag is Tags.SingleInstance and self._tag is not Tags.SingleInstance:
            return await self._parent.resolve(cls)

        instance = await factory()
        with self._lock:
            self._cache[cls] = instance
        return instance


    def add_instance(self, instance, type=None):
        if type is None:
            type = get_type(instance)
        if not isinstance(instance, type):
            raise NotSubclass('Object [%s] is not an instance of [%s].' % (instance, type))
        if type in self._mapping:
            raise AlreadyRegistered('Interface [%s] already registered.' % type)
        with self._lock:
            if type in self._cache:
                raise AlreadyRegistered('Interface [%s] already registered.' % type)
            self._cache[type] = instance

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc, tb):
        return self.dispose(exc)
