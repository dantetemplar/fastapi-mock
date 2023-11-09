__all__ = ["ExampleProvider"]

import random
from random import choice

from pydantic.fields import FieldInfo

_str_examples = (
    "Hello, World ❤️",
    "Nihil verum omnia licet",
    "Lorem ipsum dolor sit amet",
)


class ExampleProvider:
    BOOL: FieldInfo
    STR: FieldInfo
    FLOAT: FieldInfo
    INT: FieldInfo

    def __init__(
        self,
        BOOL: FieldInfo = FieldInfo(default_factory=lambda: random.getrandbits(1)),
        STR: FieldInfo = FieldInfo(default_factory=lambda: choice(_str_examples)),
        FLOAT: FieldInfo = FieldInfo(default_factory=lambda: random.uniform(0, 100)),
        INT: FieldInfo = FieldInfo(default_factory=lambda: random.randrange(0, 100)),
    ):
        self.BOOL = BOOL
        self.STR = STR
        self.FLOAT = FLOAT
        self.INT = INT
