def run_loop(hub: HubService) -> None:      # двері 1: автономний цикл
    from time import sleep
    while True:
        hub.tick()
        sleep(30)

def run_cli(hub: HubService) -> None:       # двері 2: читаємо команди, поки дім живе
    import sys
    for line in sys.stdin:                  # головний потік блокується на вводі…
        match line.split():
            case ["state"]:
                s = hub.state()
                print(f"heating={s.heating}, пристроїв={len(s.devices)}")
            case ["set-threshold", c]:
                hub.set_threshold(float(c)); print(f"поріг → {c} °C")
            case ["add", kind, room]:
                hub.add_device(Device(kind, room)); print(f"додано {kind} у {room}")
            case ["quit"]:
                break
            case _:
                print("вживай: state | set-threshold <°C> | add <kind> <room> | quit")

def build(env: str) -> HubService:          # ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
    if env == "prod":
        sensor: Sensor = OneWireThermometer("28-0119a1b2c3d4")   # справжнє залізо
        heater: Heater = SmartPlug("http://192.168.1.50")
    else:
        sensor, heater = FakeSensor(), FakeHeater()              # підробки для тесту й розробки
    devices = InMemoryDeviceRepository()        # SQLite стане сюди в модулі про сховище
    return HubService(sensor, heater, devices, Config(threshold=20.0))

if __name__ == "__main__":
    import os
    from threading import Thread
    hub = build(os.getenv("DH_ENV", "dev"))
    Thread(target=run_loop, args=(hub,), daemon=True).start()   # двері 1 — фоновий потік
    run_cli(hub)                                                # двері 2 — головний потік
