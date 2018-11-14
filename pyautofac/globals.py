from enum import Enum


class Tags(Enum):
    SingleInstance = 1
    Lifetime = 2
    AlwaysNew = 3

_LTE_MAP = {
    (Tags.AlwaysNew, Tags.SingleInstance),
    (Tags.AlwaysNew, Tags.Lifetime),
    (Tags.Lifetime, Tags.SingleInstance),
}

def lte(tag1, tag2):
    return (tag1, tag2) in _LTE_MAP
