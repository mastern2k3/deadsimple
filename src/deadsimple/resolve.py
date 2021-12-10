from typing import Callable, TypeVar, Any, NamedTuple
from inspect import signature, Parameter


class Depends(NamedTuple):
    factory: Callable


_resolver_cache = {}


TReturn = TypeVar("TReturn")


def resolve(factory: Callable[[Any], TReturn], overrides: dict = None) -> TReturn:

    if overrides is None:
        overrides = {}

    return _resolve(factory, overrides)


def _resolve(factory: Callable[[Any], TReturn], context: dict) -> TReturn:

    _resolver = _resolver_cache.get(factory)
    if _resolver is not None:
        return _resolver(context)

    _signature = signature(factory)

    dependency_factories = []

    for parameter in _signature.parameters.values():

        if parameter.default is Parameter.empty:
            raise Exception("Factory method missing default definition")

        if not isinstance(parameter.default, Depends):
            continue

        _depends: Depends = parameter.default

        dependency_factories.append((parameter.name, _depends.factory))

    def _resolver(_context: dict):

        dependencies = {}

        for name, _factory in dependency_factories:

            context_value = _context.get(_factory)
            if context_value is not None:
                dependencies[name] = context_value
                continue

            dependency = _resolve(_factory, _context)

            dependencies[name] = dependency
            _context[_factory] = dependency

        return factory(**dependencies)

    _resolver_cache[factory] = _resolver

    return _resolver(context)
