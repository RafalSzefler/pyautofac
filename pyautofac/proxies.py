from inspect import isclass

from pyautofac.exceptions import NotClass, NotSubclass
from pyautofac.globals import TAG_SINGLE_INSTANCE


class BuilderProxy:
    def __init__(self):
        self.tag = None

    def as_interface(self, interface):
        if not isclass(interface):
            raise NotClass('[%s] is not a class.' % interface)
        if not issubclass(self.registered_type, interface):
            raise NotSubclass('[%s] is not a child of [%s]' % (self.registered_type, interface))
        self.interface = interface

    def as_self(self):
        self.interface = self.registered_type

    def tag(self, obj):
        self.tag = obj

    def single_instance(self):
        self.tag = TAG_SINGLE_INSTANCE

    def per_lifetime(self):
        self.tag = None


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
