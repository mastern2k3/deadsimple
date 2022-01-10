from __future__ import annotations
from dataclasses import dataclass
from unittest.mock import Mock, call

from pytest import raises as pytest_raises

from deadsimple import (
    Depends,
    resolve,
    GeneratorClosureException,
    InvalidGeneratorFactoryExcpetion,
)


@dataclass
class _TestDepA:
    value: str


@dataclass
class _TestDepB:
    dep_a: _TestDepA


def test_enter_exit_called_for_yield_factories():

    mock = Mock()

    def get_dep_a() -> _TestDepA:
        mock.start()
        yield _TestDepA(value="some value")
        mock.end()

    def get_dep_b(dep_a: _TestDepA = Depends(get_dep_a)) -> _TestDepB:
        return _TestDepB(dep_a=dep_a)

    dep = resolve(get_dep_b)

    assert dep.dep_a.value == "some value"
    assert mock.method_calls == [call.start(), call.end()]


def test_enter_exit_called_for_immediate_yield_factories():

    mock = Mock()

    def get_dep_a() -> _TestDepA:
        mock.start()
        yield _TestDepA(value="some value")
        mock.end()

    dep = resolve(get_dep_a)

    assert dep.value == "some value"
    assert mock.method_calls == [call.start(), call.end()]


def test_enter_exit_called_on_exception():
    class ExpectedException(Exception):
        pass

    mock = Mock()

    def get_dep_a() -> _TestDepA:
        mock.start()
        yield _TestDepA(value="some value")
        mock.end()

    def get_dep_b(dep_a: _TestDepA = Depends(get_dep_a)) -> _TestDepB:
        raise ExpectedException()

    with pytest_raises(ExpectedException):
        dep = resolve(get_dep_b)

    assert mock.method_calls == [call.start(), call.end()]


@dataclass
class _TestDepC:
    value: str


def test_enter_exit_called_on_exception_in_end():

    mock = Mock()

    dependency_exception = Exception()
    end_exception = Exception()

    def get_dep_a() -> _TestDepA:
        mock.start()
        yield _TestDepA(value="some value")
        mock.end()

    def get_dep_c() -> _TestDepC:
        yield _TestDepC(value="some value")
        raise end_exception

    def get_dep_b(
        dep_a: _TestDepA = Depends(get_dep_a),
        dep_c: _TestDepC = Depends(get_dep_c),
    ) -> _TestDepB:
        raise dependency_exception

    with pytest_raises(GeneratorClosureException) as closure_exception:
        dep = resolve(get_dep_b)

    assert mock.method_calls == [call.start(), call.end()]
    assert closure_exception.value.resolve_exception is dependency_exception
    assert closure_exception.value.exceptions == [end_exception]


def test_two_yield_generator_factory_raise_excpetion():
    def get_dep_a() -> _TestDepA:
        yield _TestDepA(value="some value")
        yield None

    with pytest_raises(GeneratorClosureException) as closure_exception:
        dep = resolve(get_dep_a)

    assert closure_exception.value.resolve_exception is None
    assert len(closure_exception.value.exceptions) == 1
    assert isinstance(
        closure_exception.value.exceptions[0], InvalidGeneratorFactoryExcpetion
    )


def test_nested_generator_factories_start_and_end_in_reverse():

    mock = Mock()

    def get_dep_a() -> _TestDepA:
        mock.start_a()
        yield _TestDepA(value="some value")
        mock.end_a()

    def get_dep_c() -> _TestDepC:
        mock.start_c()
        yield _TestDepC(value="some value")
        mock.end_c()

    def get_dep_b(
        dep_a: _TestDepA = Depends(get_dep_a),
        dep_c: _TestDepC = Depends(get_dep_c),
    ) -> _TestDepB:
        mock.start_b()
        yield _TestDepB(dep_a=dep_a)
        mock.end_b()

    dep = resolve(get_dep_b)

    assert dep.dep_a.value == "some value"

    expected_calls = [
        call.start_a(),
        call.start_c(),
        call.start_b(),
        call.end_b(),
        call.end_c(),
        call.end_a(),
    ]
    assert mock.method_calls == expected_calls
