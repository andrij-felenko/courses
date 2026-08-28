def build(env: str) -> HubService:          # ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
    if env == "prod":
        sensor, heater = OneWireThermometer(), SmartPlug()   # справжнє залізо
        devices = InMemoryDeviceRepository()                 # SQLite стане сюди в модулі про сховище
    else:
        sensor, heater = FakeSensor(), FakeHeater()          # підробки для тесту
        devices = InMemoryDeviceRepository()
    return HubService(sensor, heater, devices, Config(threshold=20.0))

if __name__ == "__main__":
    hub = build(os.getenv("DH_ENV", "dev"))
    Thread(target=run_loop, args=(hub,), daemon=True).start()  # двері 1 крутяться самі
    run_cli(hub, sys.argv[1:])                                 # двері 2 — на команду
