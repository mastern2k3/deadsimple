from dataclasses import dataclass
from typing import Callable, TypeVar, Any
from inspect import signature, isgeneratorfunction, Parameter


@dataclass
class Depends:
    factory: Callable


@dataclass
class _Context:
    resolved_cache: dict
    open_generators: list


_resolver_cache = {}


TReturn = TypeVar("TReturn")


def resolve(factory: Callable[[Any], TReturn], overrides: dict = None) -> TReturn:

    if overrides is not None:
        resolved_cache = overrides
    else:
        resolved_cache = {}

    context = _Context(
        resolved_cache=resolved_cache,
        open_generators=[],
    )

    value = _resolve(factory, context)

    for open_generator in context.open_generators:

        try:
            next(open_generator)
            raise Exception(
                "Generator didn't close after one iteration. "
                "(you might have more than one yield in your factory method)"
            )
        except StopIteration:
            pass

    return value


def _resolve(factory: Callable[[Any], TReturn], context: _Context) -> TReturn:

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

    is_generator = isgeneratorfunction(factory)

    def _resolver(_context: _Context):

        dependencies = {}

        for name, _factory in dependency_factories:

            context_value = _context.resolved_cache.get(_factory)
            if context_value is not None:
                dependencies[name] = context_value
                continue

            dependency = _resolve(_factory, _context)

            dependencies[name] = dependency
            _context.resolved_cache[_factory] = dependency

        value = factory(**dependencies)

        if is_generator:
            _context.open_generators.append(value)
            value = next(value)

        return value

    _resolver_cache[factory] = _resolver

    return _resolver(context)
