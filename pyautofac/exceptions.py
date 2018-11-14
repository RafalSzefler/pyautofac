class PyautofacException(Exception):
    pass


class NotClass(PyautofacException):
    pass


class NotSubclass(PyautofacException):
    pass


class AlreadyRegistered(PyautofacException):
    pass


class NotRegistered(PyautofacException):
    pass


class NotAnnotatedConstructorParam(PyautofacException):
    pass
