from dataclasses import dataclass

@dataclass
class Pkg:
    Ca: int; Ce: int; Na: int; Nc: int

def metrics(p: Pkg) -> dict:
    I = p.Ce / (p.Ca + p.Ce)      # нестабільність: частка вихідних залежностей
    A = p.Na / p.Nc               # абстрактність: частка абстрактних типів
    D = abs(A + I - 1)            # відстань до головної послідовності
    return {"I": round(I, 2), "A": round(A, 2), "D": round(D, 2)}

metrics(Pkg(Ca=30, Ce=2, Na=0, Nc=9))       # db-gateway → {'I': 0.06, 'A': 0.0, 'D': 0.94}
