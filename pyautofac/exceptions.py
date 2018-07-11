class PyautofacException(Exception):
    pass


class NotClass(PyautofacException):
    pass


class NotSubclass(PyautofacException):
    pass


class NotInstance(PyautofacException):
    pass


class AlreadyRegistered(PyautofacException):
    pass


class Unregistered(PyautofacException):
    pass


class NotAnnotatedConstructorParam(PyautofacException):
    pass
