from dataclasses import dataclass

@dataclass
class Zero: pass                       # Z(x⃗) = 0
@dataclass
class Succ: pass                       # S(x) = x + 1
@dataclass
class Proj: i: int                     # Pᵢⁿ: вертає i-й аргумент (від 1)
@dataclass
class Comp: f: "Expr"; gs: list        # f( g₁, …, gₘ )
@dataclass
class Rec:  base: "Expr"; step: "Expr" # база, крок

Expr = Zero | Succ | Proj | Comp | Rec
