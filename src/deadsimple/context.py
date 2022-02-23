from typing import TypeVar, Generic, Callable
from dataclasses import dataclass

from .resolve import (
    _Context,
    _resolve,
    _close_open_generators,
    get_context,
    _create_context,
)


TContextValue = TypeVar("TContextValue")


@dataclass
class ResolutionContextManager(Generic[TContextValue]):

    factory: Callable[..., TContextValue]
    context: _Context

    def __enter__(self) -> TContextValue:

        try:
            value = _resolve(self.factory, self.context)
        except Exception as ex:
            if len(self.context.open_generators) > 0:
                _close_open_generators(self.context, ex)
            raise ex

        return value

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if len(self.context.open_generators) > 0:
            _close_open_generators(self.context, exc_value)


def resolve_open(
    factory: Callable[..., TContextValue],
    overrides: dict = None,
) -> ResolutionContextManager[TContextValue]:

    context = _create_context(overrides)

    resolved_cache = {}

    context = _Context(
        resolved_cache=resolved_cache,
        open_generators=[],
    )

    resolved_cache[get_context] = context

    if overrides is not None:
        resolved_cache.update(overrides)

    return ResolutionContextManager[TContextValue](
        factory=factory,
        context=context,
    )
