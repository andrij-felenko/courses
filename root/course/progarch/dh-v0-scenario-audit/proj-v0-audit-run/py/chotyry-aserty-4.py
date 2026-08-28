import hub

def test_stuck_sensor_is_flagged(monkeypatch):
    monkeypatch.setattr(hub, "read_sensor", lambda: 19.9)                 # застиг намертво
    monkeypatch.setattr(hub, "heater_on",  lambda: None)
    monkeypatch.setattr(hub, "heater_off", lambda: None)

    for _ in range(240):                          # 2 год по 30 с — те саме число
        hub.step()

    # надійність: після 240 однакових читань хаб мусив би засумніватися
    assert getattr(hub, "stale_alarm", False), \
        "давач застиг на 19.9 — хаб не помітив і грів дві години наосліп"
