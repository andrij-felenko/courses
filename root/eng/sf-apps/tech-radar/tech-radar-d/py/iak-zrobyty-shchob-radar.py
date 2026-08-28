# Радар як дані: кожен блип — назва, кільце, квадрант.
# Найпростіша форма — таблиця, яку легко тримати поряд із кодом.
from enum import IntEnum

class Ring(IntEnum):
    ADOPT  = 0
    TRIAL  = 1
    ASSESS = 2
    HOLD   = 3

# напр. ідентифікатор бібліотеки/пакета -> кільце, куди команда його поклала
RADAR = {
    "grpc":         Ring.ADOPT,
    "kafka":        Ring.ADOPT,
    "postgres":     Ring.ADOPT,
    "rabbitmq":     Ring.TRIAL,
    "mongo":        Ring.ASSESS,
    "soap-legacy":  Ring.HOLD,    # від цього відходимо
    "custom-queue": Ring.HOLD,    # самописна черга — більше нового не заводимо
}

# Знайти кільце технології за назвою; None, якщо її на радарі нема взагалі.
def ring_of(dep):
    return RADAR.get(dep)   # не на радарі — окремий випадок, теж вартий уваги
