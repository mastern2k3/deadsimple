# deadsimple

> A dependency injection library for python, aimed for the least amount of magic.

Heavily influenced by [FastAPI]'s dependency injection classes and logic.


Simple Example

```python
from dataclasses import dataclass
from deadsimple import Depends, resolve


@dataclass
class DepA():
    dep_b: DepB


@dataclass
class DepB():
    value: str


def get_dep_b() -> DepB:
    return DepB(value="some val")


def get_dep_a(dep_b: DepB = Depends(get_dep_b)) -> DepA:
    return DepA(dep_b=dep_b)


my_a = resolve(get_dep_a)

assert my_a.dep_b.value == "some val"
```


Dependencies will instantiate once per factory for each call to `resolve`.

```python
@dataclass
class DepC():
    dep_a: DepA
    dep_b: DepB


def get_dep_c(
    dep_a: DepA = Depends(get_dep_a),
    dep_b: DepB = Depends(get_dep_b),
) -> DepC:

    return DepC(dep_a=dep_a, dep_b=dep_b)


my_c = resolve(get_dep_c)

assert my_c.dep_b is my_c.dep_a.dep_b
```


For Singleton use [lru_cache] or [cache] from [functools]

```python
from functools import lru_cache
# or from functools import cache if you're 3.9+


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


not_singleton_a = resolve(get_not_singleton)
not_singleton_b = resolve(get_not_singleton)

assert not_singleton_a is not not_singleton_b
assert not_singleton_a.singleton_dep is not_singleton_b.singleton_dep
```

Override dependencies:

```python
override_dep_b = DepB(value="some other val")

my_a = resolve(get_dep_a, overrides={get_dep_b: override_dep_b})

assert my_a.dep_b.value == "some other val"
```

Generator factory methods:

```python
def get_dep_b() -> DepB:
    print("enter b")
    yield DepB(value="some val")
    print("exit b")


def get_dep_a(dep_b: DepB = Depends(get_dep_b)) -> DepA:
    print("enter a")
    yield DepA(dep_b=dep_b)
    print("exit a")


resolve(get_dep_a)

# prints:
# enter b
# enter a
# exit a
# exit b
```

Lazy / optional resolution:

```python
from deadsimple import Lazy


def get_dep_b() -> DepB:
    print("enter b")
    return DepB(value="some val")


def get_dep_a(dep_b = Lazy(get_dep_b)) -> DepA:
    print("enter a")
    return DepA(dep_b=dep_b.lazy)


resolve(get_dep_a)

# prints:
# enter a
# enter b
```

Controlled dependency lifetime scope:

```python
from deadsimple import resolve_open


def get_dep_b() -> DepB:
    print("enter b")
    yield DepB(value="some val")
    print("exit b")


with resolve_open(get_dep_b) as dep_b:
    print("inside")

# prints:
# enter b
# inside
# exit b
```


## Todo

- [x] Lazy resolution
- [ ] Async support
- [ ] Better performance benchmarks


## Installing

```
pip install deadsimple
```


[FastAPI]: https://github.com/tiangolo/fastapi
[lru_cache]: https://docs.python.org/3/library/functools.html#functools.lru_cache
[cache]: https://docs.python.org/3/library/functools.html#functools.cache
[functools]: https://docs.python.org/3/library/functools.html
