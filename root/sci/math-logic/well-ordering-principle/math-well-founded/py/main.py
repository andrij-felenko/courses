from dataclasses import dataclass

@dataclass
class Num: v: int
@dataclass
class Add: l: object; r: object
@dataclass
class Mul: l: object; r: object

def ev(e):
    match e:
        case Num(v):    return v             # лист — мінімальний елемент: відповідь одразу
        case Add(l, r): return ev(l) + ev(r)  # виклики на СТРОГО менших піддеревах
        case Mul(l, r): return ev(l) * ev(r)
    raise TypeError(e)
