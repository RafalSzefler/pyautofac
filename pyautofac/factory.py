from inspect import isclass


class TypeFactory:
    async def __call__(self):
        raise NotImplementedError()


_PLACEHOLDER = object()
class TypeFactoryBuilder:
    def __init__(self):
        self._types = {}

    def __getitem__(self, key):
        if not isclass(key):
            raise KeyError('Key has to be a class')
        cls = self._types.get(key, _PLACEHOLDER)
        if cls is _PLACEHOLDER:
            cls = type('Factory', (TypeFactory,), {'SUB_TYPE': key})
            self._types[key] = cls
        return cls


Factory = TypeFactoryBuilder()
