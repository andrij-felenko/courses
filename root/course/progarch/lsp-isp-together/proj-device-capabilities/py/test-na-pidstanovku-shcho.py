def switchable_contract(make) -> None:
    d = make()
    d.turn_on();  assert d.is_on() is True,  "після turn_on має бути ввімкнено"
    d.turn_off(); assert d.is_on() is False, "після turn_off має бути вимкнено"

class LyingSwitch:                        # форма Switchable є, поведінка бреше
    def turn_on(self):  raise RuntimeError("не вмикається")
    def turn_off(self): raise RuntimeError("не вимикається")
    def is_on(self) -> bool: return False

# 1) сторож (isinstance) ПРОПУСКАЄ брехуна — форма ж збігається:
assert isinstance(LyingSwitch(), Switchable)
# 2) чесна реалізація проходить контракт:
switchable_contract(lambda: SmartSocket())
# 3) а контракт брехуна ЛОВИТЬ:
try:
    switchable_contract(lambda: LyingSwitch())
    raise AssertionError("контракт мусив упіймати брехню")
except RuntimeError:
    pass                                  # саме цього й чекали
print("усе зелене")
