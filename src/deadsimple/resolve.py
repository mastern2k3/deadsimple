from typing import Callable, Optional, TypeVar, Any
from dataclasses import dataclass
from inspect import signature, isgeneratorfunction, Parameter

from .exceptions import GeneratorClosureException, InvalidGeneratorFactoryExcpetion


@dataclass(frozen=True)
class Depends:
    factory: Callable


@dataclass(frozen=True)
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

    resolve_exception = None

    try:
        value = _resolve(factory, context)
    except Exception as ex:
        resolve_exception = ex
        raise
    finally:
        if len(context.open_generators) > 0:
            _close_open_generators(context, resolve_exception)

    return value


def _close_open_generators(context: _Context, resolve_exception: Optional[Exception]):

    exceptions = None

    for open_generator in reversed(context.open_generators):

        try:
            next(open_generator)
            raise InvalidGeneratorFactoryExcpetion()
        except StopIteration:
            pass
        except Exception as ex:
            if exceptions is None:
                exceptions = [ex]
            else:
                exceptions.append[ex]

    if exceptions is not None:
        raise GeneratorClosureException(
            resolve_exception=resolve_exception,
            exceptions=exceptions,
        )


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
