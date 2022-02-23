# Classes as factories

Although discouraged, deadsimple supports classes as dependency factories.

So the following is possible:

``` python hl_lines="21 25"
from dataclasses import dataclass
from deadsimple import Depends, resolve


@dataclass
class DepB:
    value: str


def get_dep_b() -> DepB:
    return DepB(value="some val")


@dataclass
class DepA:
    dep_b: DepB = Depends(get_dep_b)


@dataclass
class DepC:
    dep_a: DepA = Depends(DepA)
    dep_b: DepB = Depends(get_dep_b)


dep = resolve(DepC)

assert dep.dep_b.value == "some val"
assert dep.dep_b is dep.dep_a.dep_b
```

The problem being that using class names to define dependencies doesn't leave
room to add logic to the way it is instantiated, e.g. making it singleton,
scoped or adding some initialization logic.

There is a compromise if you want to avoid wiring all the parameters from the
factory into the new instance.

Simply declare the factory as an alias to the class name:

```python
@dataclass
class DepB:
    value: str


def get_dep_b() -> DepB:
    return DepB(value="some val")


@dataclass
class DepA:
    dep_b: DepB = Depends(get_dep_b)


get_dep_a = DepA


@dataclass
class DepC:
    dep_a: DepA = Depends(get_dep_a)
    dep_b: DepB = Depends(get_dep_b)


get_dep_c = DepC


dep = resolve(get_dep_c)
```

This allows you to later make changes like:

```python
@dataclass
class DepA:

    dep_b: DepB

    def open(self):
        ...

    def close(self):
        ...


def get_dep_a(dep_b = Depends(get_dep_b)) -> DepA:

    dep_a = DepA(dep_b=dep_b)

    try:
        dep_a.open()
        yield dep_b
    finally:
        dep_a.close()
```

This without going back and changing all instances of `Depends(...)`.
