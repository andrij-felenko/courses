def tick(sensor: Sensor, heater: Heater, cfg: Config) -> None:  # рівно один оберт, без розкладу
    match decide(sensor.read(), cfg):
        case Command.HEAT: heater.on()
        case Command.IDLE: heater.off()

def run(sensor, heater, cfg):
    while True:
        tick(sensor, heater, cfg)   # логіка обороту
        sleep(30)                   # розклад — окремо

def test_cold_room_turns_heater_on():
    heater = SpyHeater()
    tick(FakeSensor(Reading(18.0)), heater, Config(threshold=20.0))
    assert heater.calls == ["on"]   # холодний вимір докрутив саме розетку
