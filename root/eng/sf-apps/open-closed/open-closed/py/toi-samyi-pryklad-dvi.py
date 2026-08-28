from dataclasses import dataclass
from enum import Enum

class ShapeKind(Enum):
    CIRCLE = 1
    RECT = 2
    TRIANGLE = 3

@dataclass
class Shape:
    kind: ShapeKind
    a: float                # радіус / сторони / основа й висота
    b: float = 0.0

def area(s: Shape) -> float:
    match s.kind:
        case ShapeKind.CIRCLE:   return 3.14159265 * s.a * s.a
        case ShapeKind.RECT:     return s.a * s.b
        case ShapeKind.TRIANGLE: return 0.5 * s.a * s.b
        # кожна нова фігура — нова гілка ТУТ, у вже працюючій функції
    return 0.0
