from __future__ import annotations
from functools import partial
from dataclasses import dataclass
from typing import Any
from deadsimple import Depends, resolve


@dataclass
class _TestDepB:
    value: str


def _dep_b() -> _TestDepB:
    return _TestDepB(value="some val")


@dataclass
class _TestDepA:
    dep_b: _TestDepB = Depends(_dep_b)


def test_resolve_class():

    dep = resolve(_TestDepA)

    assert dep.dep_b.value == "some val"


@dataclass
class _TestDepC:
    dep_a: _TestDepA = Depends(_TestDepA)
    dep_b: _TestDepB = Depends(_dep_b)


def test_nested_resolve_class():

    dep = resolve(_TestDepC)

    assert dep.dep_b.value == "some val"
    assert dep.dep_b is dep.dep_a.dep_b
