# deadsimple

A dependency injection library for python, aimed for the least amount of magic.

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

assert my_a.dep_b == "some_val"
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


[FastAPI]: https://github.com/tiangolo/fastapi
