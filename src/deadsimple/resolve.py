from typing import Callable, Dict, Optional, TypeVar, Any
from dataclasses import dataclass
from inspect import signature, isgeneratorfunction, Parameter

from .exceptions import GeneratorClosureException, InvalidGeneratorFactoryExcpetion


TReturn = TypeVar("TReturn")


def Depends(factory: Callable[..., TReturn]) -> TReturn:
    return _Depends(factory=factory)


@dataclass(frozen=True)
class _Depends:
    factory: Callable


@dataclass(frozen=True)
class _Context:
    resolved_cache: dict
    open_generators: list


def get_context() -> _Context:
    raise NotImplementedError(
        "get_context is an abstract dependency and is only avaliable during injection"
    )


_resolver_cache: Dict[Callable, Callable[[_Context], Any]] = {}


def resolve(factory: Callable[..., TReturn], overrides: dict = None) -> TReturn:

    context = _create_context(overrides)

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


def _create_context(overrides: dict = None) -> _Context:

    resolved_cache = {}

    context = _Context(
        resolved_cache=resolved_cache,
        open_generators=[],
    )

    resolved_cache[get_context] = context

    if overrides is not None:
        resolved_cache.update(overrides)

    return context


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
                exceptions.append(ex)

    if exceptions is not None:
        raise GeneratorClosureException(
            resolve_exception=resolve_exception,
            exceptions=exceptions,
        )


def _resolve(factory: Callable[..., TReturn], context: _Context) -> TReturn:

    _cached_resolver = _resolver_cache.get(factory)
    if _cached_resolver is not None:
        return _cached_resolver(context)

    _signature = signature(factory)

    dependency_factories = []

    for parameter in _signature.parameters.values():

        if parameter.default is Parameter.empty:
            raise ValueError(
                "Factory method missing default definition. "
                f"{parameter.name=} {factory=}"
            )

        if not isinstance(parameter.default, _Depends):
            continue

        dependency_factories.append((parameter.name, parameter.default))

    is_generator = isgeneratorfunction(factory)

    def _resolver(_context: _Context) -> TReturn:

        context_value = _context.resolved_cache.get(factory)
        if context_value is not None:
            return context_value

        dependencies = {}

        for name, depends in dependency_factories:
            dependencies[name] = _resolve(depends.factory, _context)

        value = factory(**dependencies)

        if is_generator:

            _context.open_generators.append(value)
            value = next(value)

        _context.resolved_cache[factory] = value

        return value

    _resolver_cache[factory] = _resolver

    return _resolver(context)
