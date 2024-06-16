from _typeshed import Incomplete
from typing import Final

__version__: Final[str]

def mkTimeTuple(timeString): ...
def str2seconds(timeString): ...
def seconds2str(seconds): ...
def nextRoundNumber(x): ...
def find_interval(lo, hi, I: int = 5): ...
def find_good_grid(lower, upper, n=(4, 5, 6, 7, 8, 9), grid: Incomplete | None = None): ...
def ticks(
    lower, upper, n=(4, 5, 6, 7, 8, 9), split: int = 1, percent: int = 0, grid: Incomplete | None = None, labelVOffset: int = 0
): ...
def findNones(data): ...
def pairFixNones(pairs): ...
def maverage(data, n: int = 6): ...
def pairMaverage(data, n: int = 6): ...

class DrawTimeCollector:
    formats: Incomplete
    disabled: bool
    def __init__(self, formats=["gif"]) -> None: ...
    def clear(self) -> None: ...
    def record(self, func, node, *args, **kwds) -> None: ...
    def __call__(self, node, canvas, renderer) -> None: ...
    @staticmethod
    def rectDrawTimeCallback(node, canvas, renderer, **kwds): ...
    @staticmethod
    def transformAndFlatten(A, p): ...
    @property
    def pmcanv(self): ...
    def wedgeDrawTimeCallback(self, node, canvas, renderer, **kwds): ...
    def save(self, fnroot) -> None: ...

def xyDist(xxx_todo_changeme, xxx_todo_changeme1): ...
def lineSegmentIntersect(xxx_todo_changeme2, xxx_todo_changeme3, xxx_todo_changeme4, xxx_todo_changeme5): ...
def makeCircularString(
    x, y, radius, angle, text, fontName, fontSize, inside: int = 0, G: Incomplete | None = None, textAnchor: str = "start"
): ...

class CustomDrawChanger:
    store: Incomplete
    def __init__(self) -> None: ...
    def __call__(self, change, obj) -> None: ...

class FillPairedData(list[Incomplete]):
    other: Incomplete
    def __init__(self, v, other: int = 0) -> None: ...