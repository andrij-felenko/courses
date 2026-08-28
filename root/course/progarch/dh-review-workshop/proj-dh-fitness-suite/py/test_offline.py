# tests/fitness/test_offline.py
from hub import Hub

def test_local_rules_run_without_cloud():
    hub = Hub()                          # cloud уже мертвий (DeadLink)
    hub.local_sensor = lambda: 18.0      # холодно
    fired = []
    hub.on_actuate = fired.append
    hub.tick()                           # один локальний цикл правил
    assert fired == [("heater", "on")]   # рішення сталося — і ЖОДНОГО дотику до хмари
