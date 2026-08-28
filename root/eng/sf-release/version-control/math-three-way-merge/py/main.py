from enum import Enum

class Verdict(Enum):
    TAKE_BASE = 1
    TAKE_OURS = 2
    TAKE_THEIRS = 3
    CONFLICT = 4

# base, ours, theirs — три версії одного рядка (порівнюємо як рядки)
def decide_line(base: str, ours: str, theirs: str) -> Verdict:
    ours_changed   = ours   != base   # наше рухалося?
    theirs_changed = theirs != base   # їхнє рухалося?

    if not ours_changed and not theirs_changed:
        return Verdict.TAKE_BASE      # випадок 1
    if ours_changed and not theirs_changed:
        return Verdict.TAKE_OURS      # випадок 2
    if not ours_changed and theirs_changed:
        return Verdict.TAKE_THEIRS    # випадок 2 (дзеркало)

    # тут обидва рухалися:
    if ours == theirs:
        return Verdict.TAKE_OURS      # випадок 3: збіглися → одне значення
    return Verdict.CONFLICT           # випадок 4: розійшлися
