from inspect import getmro
from typing import Any, TypeVar

D = TypeVar('D')


class FlexMixin:
    """
    Mixin for flexible data handling, providing methods to access and manipulate data in a flexible manner.  @dataclass
    is nice but a little restrictive for my purposes.
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name: str) -> Any: ...

    def get(self, k: str, default: D = None) -> D:
        return self.__dict__.get(k, default)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for cls in getmro(type(self)):
            for k, v in vars(cls).items():
                if not k.startswith('_') and not callable(v):
                    result.setdefault(k, v)
        result.update({k: v for k, v in self.__dict__.items() if not k.startswith('_')})
        return result

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'
