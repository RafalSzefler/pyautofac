from pyautofac.container import Container, DummyContainer
from pyautofac.exceptions import AlreadyRegistered
from pyautofac.globals import TAG_SINGLE_INSTANCE
from pyautofac.proxies import ClassProxy, InstanceProxy


class ContainerBuilder:
    def __init__(self):
        self._proxies = []

    def _register(self, cls, proxy_type):
        proxy = proxy_type(cls)
        self._proxies.append(proxy)
        return proxy

    def register_class(self, cls):
        return self._register(cls, ClassProxy)

    def register_instance(self, inst):
        return self._register(inst, InstanceProxy)

    def build(self):
        mapping = {}
        for pr in self._proxies:
            if pr.interface in mapping:
                raise AlreadyRegistered('Interface [%s] is already registered' % pr.interface)
            mapping[pr.interface] = pr
        parent = DummyContainer()
        return Container(mapping, parent, tag=TAG_SINGLE_INSTANCE)
