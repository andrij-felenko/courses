from dataclasses import dataclass

@dataclass
class Reg:
    value: object
    ts: int
    node: str

def merge(a: Reg, b: Reg) -> Reg:
    if a.ts != b.ts:
        return a if a.ts > b.ts else b     # новіша мітка перемагає
    return a if a.node > b.node else b      # рівні мітки — стабільний тайбрейк за вузлом
