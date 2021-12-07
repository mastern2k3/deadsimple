from typing import Callable, TypeVar, Any, NamedTuple
from inspect import signature, Parameter


class Depends(NamedTuple):
    factory: Callable


_signature_cache = {}


TReturn = TypeVar("TReturn")


def resolve(factory: Callable[[Any], TReturn], overrides: dict = {}) -> TReturn:
    return _resolve(factory, overrides)


def _resolve(factory: Callable[[Any], TReturn], context: dict) -> TReturn:

    _signature = _signature_cache.get(factory)
    if _signature is None:
        _signature = signature(factory)
        _signature_cache[factory] = _signature

    dependencies = {}

    for parameter in _signature.parameters.values():

        if parameter.default is Parameter.empty:
            raise Exception("Factory with no default")

        if not isinstance(parameter.default, Depends):
            continue

        _depends: Depends = parameter.default

        context_value = context.get(_depends.factory)
        if context_value is not None:

            dependencies[parameter.name] = context_value

            continue

        dependency = _resolve(_depends.factory, context)

        dependencies[parameter.name] = dependency
        context[_depends.factory] = dependency

    return factory(**dependencies)
