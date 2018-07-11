from pyautofac import ContainerBuilder


class Foo:
    def __init__(self, value):
        self.value = value


class Bar:
    def __init__(self, foo: Foo):
        self.foo = foo

    def square(self):
        return self.foo.value ** 2


class Zoo:
    def __init__(self, bar: Bar):
        self.bar = bar

    def increment(self):
        return self.bar.square() + 1


def test_direct():
    foo = Foo(2)
    bar = Bar(foo)
    zoo = Zoo(bar)
    assert zoo.increment() == 5


def test_pyautofac():
    builder = ContainerBuilder()
    builder.register_instance(Foo(2))
    builder.register_class(Bar)
    builder.register_class(Zoo)
    container = builder.build()
    zoo = container.resolve(Zoo)
    assert zoo.increment() == 5
