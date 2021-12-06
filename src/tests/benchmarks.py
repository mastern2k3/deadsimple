from timeit import Timer
from dataclasses import dataclass

from deadsimple import resolve, Depends


@dataclass
class TestClassB:
    my_field: str


@dataclass
class TestClassA:
    my_b: TestClassB


def get_b() -> TestClassB:
    return TestClassB("hello")


def get_a(dep_b: TestClassB = Depends(get_b)) -> TestClassA:
    return TestClassA(dep_b)


# @profile
def get_a_hardcoded():
    return TestClassA(get_b())


def get_a_with_resolver():
    return resolve(get_a)


times = 1000000
repeat = 5


def run_with_resolver():

    duration = Timer(get_a_with_resolver).repeat(number=times, repeat=repeat)
    print(f"took {sum(duration) / repeat} with resolver")
    ms = ((sum(duration) / repeat) / times) * 1000
    print(f"for {ms}ms")

    print("================================")

    duration = Timer(get_a_hardcoded).repeat(number=times, repeat=repeat)
    print(f"took {sum(duration) / repeat} hardcoded")
    ms = ((sum(duration) / repeat) / times) * 1000
    print(f"for {ms}ms")


run_with_resolver()
