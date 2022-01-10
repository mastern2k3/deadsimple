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


def get_a_hardcoded():
    return get_a(get_b())


def get_a_with_resolver():
    return resolve(get_a)


times = 1000000
repeat = 5


def run_with_resolver():

    duration = Timer(get_a_with_resolver).repeat(number=times, repeat=repeat)
    print(f"took {sum(duration) / repeat} with resolver")
    ms = ((sum(duration) / repeat) / times) * 1000
    print(f"for {ms}ms each call")


def run_hardcoded():

    duration = Timer(get_a_hardcoded).repeat(number=times, repeat=repeat)
    print(f"took {sum(duration) / repeat} hardcoded")
    ms = ((sum(duration) / repeat) / times) * 1000
    print(f"for {ms}ms each call")


if __name__ == "__main__":

    from sys import argv

    if len(argv) <= 1:
        run_hardcoded()
        run_with_resolver()

    elif argv[1] == "hardcoded":
        run_hardcoded()

    elif argv[1] == "resolver":
        run_with_resolver()

    elif argv[1] == "profile-resolver":
        # warmup?
        run_with_resolver()
        from cProfile import run

        run("run_with_resolver()")

    elif argv[1] == "profile-hardcoded":
        # warmup?
        run_hardcoded()
        from cProfile import run

        run("run_hardcoded()")

    else:
        raise ValueError("Benchmarks can only be run for hardcoded or resolver")
