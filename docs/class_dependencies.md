# Classes as factories

Although discouraged, deadsimple supports classes as dependency factories.

So the following is possible:

``` python hl_lines="21 25"
from dataclasses import dataclass
from deadsimple import Depends, resolve


@dataclass
class DepB:
    value: str


def dep_b() -> DepB:
    return DepB(value="some val")


@dataclass
class DepA:
    dep_b: DepB = Depends(dep_b)


@dataclass
class DepC:
    dep_a: DepA = Depends(DepA)
    dep_b: DepB = Depends(dep_b)


dep = resolve(DepC)

assert dep.dep_b.value == "some val"
assert dep.dep_b is dep.dep_a.dep_b
```
