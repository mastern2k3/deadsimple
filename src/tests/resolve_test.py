from __future__ import annotations
from dataclasses import dataclass
from deadsimple import Depends, resolve


@dataclass
class _TestDepA():
    dep_b: _TestDepB


@dataclass
class _TestDepB():
    value: str


def _dep_b() -> _TestDepB:
    return _TestDepB(value="some val")


def _dep_a(dep_b: _TestDepB = Depends(_dep_b)) -> _TestDepA:
    return _TestDepA(dep_b=dep_b)


def test_nested_dependencies():

    dep = resolve(_dep_a)

    assert dep.dep_b.value == "some val"


@dataclass
class _TestDepC():
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
