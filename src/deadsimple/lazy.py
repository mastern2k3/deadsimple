from __future__ import annotations
from typing import Callable, TypeVar, Generic
from dataclasses import dataclass

from .resolve import _Context, _Depends, Depends, _resolve, get_context


TLazyValue = TypeVar("TLazyValue")


def _lazy_wrapper(
    factory: Callable[..., TLazyValue],
) -> Callable[..., LazyResolver[TLazyValue]]:
    def _wrapped(context: _Context = Depends(get_context)) -> LazyResolver[TLazyValue]:
        return LazyResolver(factory=factory, context=context)

    return _wrapped


def Lazy(factory: Callable[..., TLazyValue]) -> LazyResolver[TLazyValue]:
    return _Depends(factory=_lazy_wrapper(factory))


@dataclass
class LazyResolver(Generic[TLazyValue]):

    factory: Callable[..., TLazyValue]
    context: _Context

    @property
    def lazy(self) -> TLazyValue:
        return _resolve(self.factory, self.context)
