from __future__ import annotations
from functools import partial
from dataclasses import dataclass
from typing import Any
from deadsimple import Depends, resolve


@dataclass
class _TestDepA:
    dep_b: _TestDepB


@dataclass
class _TestDepB:
    value: str


def _dep_b() -> _TestDepB:
    return _TestDepB(value="some val")


def _dep_a(dep_b: _TestDepB = Depends(_dep_b)) -> _TestDepA:
    return _TestDepA(dep_b=dep_b)


def test_nested_dependencies():

    dep = resolve(_dep_a)

    assert dep.dep_b.value == "some val"


@dataclass
class _TestDepC:
    dep_a: _TestDepA
    dep_b: _TestDepB


def _dep_c(
    dep_a: _TestDepA = Depends(_dep_a),
    dep_b: _TestDepB = Depends(_dep_b),
) -> _TestDepC:

    return _TestDepC(dep_a=dep_a, dep_b=dep_b)


def test_single_instance_per_resolve():

    dep = resolve(_dep_c)

    assert dep.dep_b.value == "some val"
    assert dep.dep_b is dep.dep_a.dep_b


@dataclass
class _MixedDep:
    dep_a: _TestDepA
    dep_default: Any


def _mixed_dep(always_none=None, dep_a: _TestDepA = Depends(_dep_a)) -> _MixedDep:
    return _MixedDep(dep_default=always_none, dep_a=dep_a)


def _mixed_dep_2(
    my_default: str = "default",
    dep_a: _TestDepA = Depends(_dep_a),
) -> _MixedDep:
    return _MixedDep(dep_default=my_default, dep_a=dep_a)


def test_mixed_defaults_without_depends():

    dep = resolve(_mixed_dep)

    assert dep.dep_a.dep_b.value == "some val"
    assert dep.dep_default is None

    dep = resolve(_mixed_dep_2)

    assert dep.dep_a.dep_b.value == "some val"
    assert dep.dep_default == "default"


def test_resolve_with_overrides():

    override_dep_b = _TestDepB(value="some other val")
    dep = resolve(_dep_a, overrides={_dep_b: override_dep_b})

    assert dep.dep_b.value == "some other val"


_partial_dep_c = partial(_dep_c, dep_b=_TestDepB("partial"))


def test_partial_factory():

    dep = resolve(_partial_dep_c)

    assert dep.dep_a.dep_b.value == "some val"
    assert dep.dep_b.value == "partial"


def test_per_resolve_instantiation():

    dep1 = resolve(_dep_a)
    dep2 = resolve(_dep_a)

    assert dep1.dep_b is not dep2.dep_b
