from dataclasses import dataclass
from unittest.mock import Mock, call

from deadsimple import Lazy, Depends, resolve


@dataclass
class _TestDepA:
    value: str


@dataclass
class _TestDepB:
    dep_a: _TestDepA


def test_lazy_depends_produced_on_access():

    mock = Mock()

    def get_dep_a():
        mock.get_a_called()
        return _TestDepA(value="some value")

    def get_dep_b(dep_a=Lazy(get_dep_a)):
        mock.get_b_called()
        return _TestDepB(dep_a=dep_a.lazy)

    dep = resolve(get_dep_b)

    assert dep.dep_a.value == "some value"
    assert mock.mock_calls == [call.get_b_called(), call.get_a_called()]


@dataclass
class _TestDepC:
    dep_a: _TestDepA
    dep_b: _TestDepB


def test_lazy_depends_produced_once():

    mock = Mock()

    def get_dep_a():
        mock.get_a_called()
        return _TestDepA(value="some value")

    def get_dep_b(dep_a=Lazy(get_dep_a)):
        mock.get_b_called()
        return _TestDepB(dep_a=dep_a.lazy)

    def get_dep_c(dep_a=Lazy(get_dep_a), dep_b=Depends(get_dep_b)):
        mock.get_c_called()
        return _TestDepC(dep_a=dep_a.lazy, dep_b=dep_b)

    dep = resolve(get_dep_c)

    assert dep.dep_a.value == "some value"
    assert dep.dep_b.dep_a.value == "some value"
    assert dep.dep_b.dep_a is dep.dep_a

    expected_calls = [
        call.get_b_called(),
        call.get_a_called(),
        call.get_c_called(),
    ]

    assert mock.mock_calls == expected_calls


def test_lazy_mixed_depends_produced_once():

    mock = Mock()

    def get_dep_a():
        mock.get_a_called()
        return _TestDepA(value="some value")

    def get_dep_b(dep_a=Lazy(get_dep_a)):
        mock.get_b_called()
        return _TestDepB(dep_a=dep_a.lazy)

    def get_dep_c(dep_a=Depends(get_dep_a), dep_b=Depends(get_dep_b)):
        mock.get_c_called()
        return _TestDepC(dep_a=dep_a, dep_b=dep_b)

    dep = resolve(get_dep_c)

    assert dep.dep_a.value == "some value"
    assert dep.dep_b.dep_a.value == "some value"
    assert dep.dep_b.dep_a is dep.dep_a

    expected_calls = [
        call.get_a_called(),
        call.get_b_called(),
        call.get_c_called(),
    ]

    assert mock.mock_calls == expected_calls
