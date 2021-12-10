from __future__ import annotations
from dataclasses import dataclass
from unittest.mock import Mock, call
from deadsimple import Depends, resolve


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
