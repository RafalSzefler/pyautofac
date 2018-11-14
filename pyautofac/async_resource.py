from abc import ABCMeta, abstractmethod


class IAsyncResource(metaclass=ABCMeta):
    @abstractmethod
    async def initialize(self):
        raise NotImplementedError()

    @abstractmethod
    async def dispose(self, exc=None):
        raise NotImplementedError()
