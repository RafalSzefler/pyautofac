from inspect import isclass

from pyautofac.exceptions import NotClass, NotSubclass
from pyautofac.globals import Tags


class BuilderProxy:
    def __init__(self):
        self.tag = Tags.AlwaysNew
        self.overwrite = False

    def as_interface(self, interface):
        if not isclass(interface):
            raise NotClass('[%s] is not a class.' % interface)
        if not issubclass(self.registered_type, interface):
            raise NotSubclass('[%s] is not a child of [%s]' % (self.registered_type, interface))
        self.interface = interface
        return self

    def as_self(self):
        self.interface = self.registered_type
        return self

    def tag(self, obj):
        assert isinstance(obj, Tags)
        self.tag = obj
        return self

    def single_instance(self):
        self.tag = Tags.SingleInstance
        return self

    def per_lifetime(self):
        self.tag = Tags.Lifetime
        return self

    def always_new(self):
        self.tag = Tags.AlwaysNew
        return self

    def overwrite(self):
        self.overwrite = True
        return self


class ClassProxy(BuilderProxy):
    def __init__(self, cls):
        super().__init__()
        self.registered_type = cls
        self.interface = cls  


class InstanceProxy(BuilderProxy):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance
        self.registered_type = type(instance)
        self.interface = self.registered_type

    def tag(self, obj):
        raise NotImplementedError()

    def single_instance(self):
        raise NotImplementedError()

    def per_lifetime(self):
        raise NotImplementedError()

    def always_new(self):
        raise NotImplementedError()
