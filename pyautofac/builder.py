from pyautofac.container import Container
from pyautofac.exceptions import AlreadyRegistered

class _RegisterProxy:
    def __init__(self, container, target, cls):
        self._container = container
        self._target = target
        self._type = cls
        self.as_interface(self._type)

    def as_interface(self, cls):
        if cls in self._container._mapping:
            raise AlreadyRegistered()
        self._container._mapping.pop(self._type, None)
        self._container._mapping[cls] = self._target
        self._type = cls
        return self


class ContainerBuilder:
    def __init__(self):
        self._mapping = {}

    def register_class(self, cls):
        return _RegisterProxy(self, cls, cls)

    def register_instance(self, inst):
        return _RegisterProxy(self, inst, type(inst))

    def build(self):
        container = Container(self._mapping)
        self._mapping[Container] = container
        return container
