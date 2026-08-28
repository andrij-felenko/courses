# test_wiring.py
from home import Reading, Config, tick
from doubles import FakeSensor, SpyHeater

CFG = Config(threshold=20.0)

def test_cold_reading_turns_heater_on():
    heater = SpyHeater()
    tick(FakeSensor(Reading(18.0)), heater, CFG)
    assert heater.calls == ["on"]       # холодний вимір докрутив саме розетку

def test_warm_reading_turns_heater_off():
    heater = SpyHeater()
    tick(FakeSensor(Reading(22.0)), heater, CFG)
    assert heater.calls == ["off"]      # теплий — вимкнув, а не забув

def test_dead_sensor_turns_heater_off():
    heater = SpyHeater()
    tick(FakeSensor(Reading(5.0, ok=False)), heater, CFG)
    assert heater.calls == ["off"]      # холодно, та вірити нема чому → не грій

def test_each_turn_drives_the_heater():
    heater = SpyHeater()
    sensor = FakeSensor(Reading(18.0), Reading(22.0), Reading(19.0))
    for _ in range(3):
        tick(sensor, heater, CFG)
    assert heater.calls == ["on", "off", "on"]   # кожен оберт докрутив свою команду
