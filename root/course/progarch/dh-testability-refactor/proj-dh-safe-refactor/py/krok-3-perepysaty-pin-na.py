def test_stuck_sensor_stops_heating_blind():    # тепер БАЖАНЕ, не пришпилена вада
    heater = SpyHeater()
    stuck = FreshnessGuard(FakeSensor(*[Reading(19.9)] * 5), stale_after=3)
    for _ in range(5):
        tick(stuck, heater, Config(threshold=20.0))
    assert heater.calls == ["on", "on", "on", "off", "off"]   # гріє, поки вірить; тоді спокій

def test_guard_flips_on_fourth_identical():     # регресія: вартовий пильнує саме 4-й вимір
    guard = FreshnessGuard(FakeSensor(*[Reading(19.9)] * 4), stale_after=3)
    assert [guard.read().ok for _ in range(4)] == [True, True, True, False]
