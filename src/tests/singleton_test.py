from functools import lru_cache
from dataclasses import dataclass
from deadsimple import Depends, resolve


@dataclass
class Singleton():
    pass


@dataclass
class NotSingleton():
    singleton_dep: Singleton


@lru_cache
def get_singleton() -> Singleton:
    return Singleton()


def get_not_singleton(singleton: Singleton = Depends(get_singleton)) -> NotSingleton:
    return NotSingleton(singleton_dep=singleton)


def test_singleton():

    singleton = resolve(get_singleton)

    not_singleton_a = resolve(get_not_singleton)
    not_singleton_b = resolve(get_not_singleton)

    assert not_singleton_a is not not_singleton_b
    assert not_singleton_a.singleton_dep is not_singleton_b.singleton_dep
    assert not_singleton_a.singleton_dep is singleton
    assert not_singleton_a.singleton_dep is singleton
