import inspect
from threading import Lock

from pyautofac.exceptions import (
    Unregistered, NotAnnotatedConstructorParam, NotSubclass, NotInstance,
)



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

_PLACEHOLDER = object()


class Container:
    def __init__(self, mapping):
        self._mapping = mapping
        self._generated = {type(self): self}
        self._locks = {key: Lock() for key in self._mapping}

    def resolve(self, cls):
        pregenerated = self._generated.get(cls, _PLACEHOLDER)
        if pregenerated is not _PLACEHOLDER:
            return pregenerated

        target = self._mapping.get(cls, _PLACEHOLDER)
        if target is _PLACEHOLDER:
            raise Unregistered(cls)

        lock = self._locks.get(cls)
        if lock is None:
            return self._generated[cls]
        with lock:
            if cls in self._generated:
                return self._generated[cls]
            if not inspect.isclass(target):
                if not isinstance(target, cls):
                    raise NotInstance()
                self._generated[cls] = target
                del self._locks[cls]
                return target
            
            if not (cls == target or issubclass(target, cls)):
                raise NotSubclass()

            params_classes = get_constructor_params(target)
            resolved_params = [
                self.resolve(param_cls)
                for param_cls in params_classes
            ]
            instance = target(*resolved_params)
            self._generated[cls] = instance
            del self._locks[cls]
            return instance
