def test_rule_holds_without_a_screen():
    m = Thermostat(29)
    m.nudge(+1)          # 30
    m.nudge(+1)          # спроба 31 → лишається 30
    m.nudge(+1)          # знову 30
    assert m.target == 30          # верхня межа тримається — БЕЗ віджета

def test_lower_bound():
    m = Thermostat(6)
    m.nudge(-1); m.nudge(-1); m.nudge(-1)
    assert m.target == 5           # нижня межа тримається

def test_both_views_react_to_one_change():
    m = Thermostat(22)
    seen = []
    m.on_change(lambda: seen.append(("подання-А", m.target)))
    m.on_change(lambda: seen.append(("подання-Б", m.target)))
    m.nudge(+1)
    assert seen == [("подання-А", 23), ("подання-Б", 23)]   # обидва почули одну зміну

def test_no_signal_when_nothing_changes():
    m = Thermostat(30)
    fired = []
    m.on_change(lambda: fired.append(1))
    m.nudge(+1)                    # на межі: число не змінилось
    assert fired == []             # зайвого сповіщення нема
