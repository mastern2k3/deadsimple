from dataclasses import dataclass
from unittest.mock import Mock, call

from pytest import raises

from deadsimple import Depends, resolve_open


@dataclass
class _TestDepA:
    value: str


@dataclass
class _TestDepB:
    dep_a: _TestDepA


def test_context_closes_only_after_exit():

    mock = Mock()

    def get_dep_a():
        mock.enter_a()
        yield _TestDepA(value="some value")
        mock.exit_a()

    with resolve_open(get_dep_a) as dep_a:
        assert dep_a.value == "some value"
        mock.inside_scope()

    expected_calls = [
        call.enter_a(),
        call.inside_scope(),
        call.exit_a(),
    ]

    assert mock.mock_calls == expected_calls


def test_generators_closed_on_exception_in_context():

    mock = Mock()

    def get_dep_a():
        mock.enter_a()
        yield _TestDepA(value="some value")
        mock.exit_a()

    class _Exception(Exception):
        pass

    with raises(_Exception):
        with resolve_open(get_dep_a) as dep_a:
            mock.inside_scope()
            assert dep_a.value == "some value"
            raise _Exception()

    expected_calls = [
        call.enter_a(),
        call.inside_scope(),
        call.exit_a(),
    ]

    assert mock.mock_calls == expected_calls


def test_generators_closed_on_exception_in_dependency():

    mock = Mock()

    class _Exception(Exception):
        pass

    def get_dep_a():
        mock.enter_a()
        yield _TestDepA(value="some value")
        mock.exit_a()

    def get_dep_b(dep_a=Depends(get_dep_a)):
        assert dep_a.value == "some value"
        mock.enter_b()
        raise _Exception()

    with raises(_Exception):
        with resolve_open(get_dep_b):
            mock.inside_scope()

    expected_calls = [
        call.enter_a(),
        call.enter_b(),
        call.exit_a(),
    ]

    assert mock.mock_calls == expected_calls
