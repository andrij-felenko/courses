from enum import IntEnum

class State(IntEnum):
    LOCKED = 0
    OPEN   = 1

class Event(IntEnum):
    COIN = 0
    PUSH = 1

# клітинка: (новий стан, дія переходу — модель Мілі; None — нічого)
# уся поведінка — тут, як дані; рядок = стан, стовпець = подія
table = {
    #                COIN                        PUSH
    State.LOCKED: {Event.COIN: (State.OPEN,   unlock), Event.PUSH: (State.LOCKED, None)},
    State.OPEN:   {Event.COIN: (State.OPEN,   None),   Event.PUSH: (State.LOCKED, lock)},
}

state = State.LOCKED

def fsm_dispatch(ev):
    global state
    if ev not in table[state]:         # чужа / невалідна подія
        state = State.LOCKED           # failsafe: безпечний стан турнікета — замкнено
        return
    nxt, action = table[state][ev]     # один індекс — O(1)
    if action:                         # дія НА переході — модель Мілі
        action()
    if nxt != state:                   # перехід СПРАВДІ змінює стан?
        on_exit(state)                 # дії «на виході» зі старого…
        on_enter(nxt)                  # …і «на вході» в новий — модель Мура
    state = nxt
