from enum import Enum, auto

class Command(Enum):               # рішення — це ЗНАЧЕННЯ, а не вчинок
    HEAT = auto()
    IDLE = auto()

def decide(r: Reading, cfg: "Config") -> Command:   # чиста: ті самі входи → той самий вихід
    if not r.ok:
        return Command.IDLE        # давач мовчить → безпечний спокій, а не «грій наосліп»
    return Command.HEAT if r.celsius < cfg.threshold else Command.IDLE
