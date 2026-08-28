import time
import hub

def test_decision_latency_under_budget(monkeypatch):
    monkeypatch.setattr(hub, "read_sensor", lambda: 18.0)
    monkeypatch.setattr(hub, "heater_on",  lambda: None)
    monkeypatch.setattr(hub, "heater_off", lambda: None)

    start = time.perf_counter()
    hub.step()
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 100                      # шлях рішення без мережевого стрибка
