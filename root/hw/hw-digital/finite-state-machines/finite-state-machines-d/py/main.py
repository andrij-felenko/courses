from enum import Enum


class State(Enum):
    GREEN = 0
    YELLOW = 1
    RED = 2
    RED_YELLOW = 3


state = State.GREEN

# Мур: вихід залежить ЛИШЕ від стану — лампи горять рівно й стабільно
def set_lamps(r, y, g):
    LAMP_RED[0], LAMP_YELLOW[0], LAMP_GREEN[0] = r, y, g


def traffic_outputs(s):
    lamps = {                      # R  Y  G
        State.GREEN:      (0, 0, 1),
        State.YELLOW:     (0, 1, 0),
        State.RED:        (1, 0, 0),
        State.RED_YELLOW: (1, 1, 0),
    }
    set_lamps(*lamps[s])


# перехід «по колу за модулем 4» — викликати на кожен tick таймера
def traffic_on_tick():
    global state
    nxt = {
        State.GREEN:      State.YELLOW,
        State.YELLOW:     State.RED,
        State.RED:        State.RED_YELLOW,
        State.RED_YELLOW: State.GREEN,
    }
    state = nxt[state]
    traffic_outputs(state)         # вихід Мура: з нового стану
