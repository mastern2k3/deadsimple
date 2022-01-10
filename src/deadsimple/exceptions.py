from typing import List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratorClosureException(Exception):
    """Exception raised when one or more exceptions occur during the phase of closing
    open generator factories (factory methods with yield).
    """

    resolve_exception: Optional[Exception]
    exceptions: List[Exception]

    def __str__(self):
        return "One or more exceptions while closing generator dependencies."


@dataclass(frozen=True)
class InvalidGeneratorFactoryExcpetion(Exception):
    """Exception raised when a generator factory yields more than one time (has more
    than one iteration).
    """

    def __str__(self):
        return (
            "Generator did not close after one iteration. "
            "(you might have more than one yield in your factory method)"
        )
