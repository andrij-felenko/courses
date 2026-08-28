function build(env: string): HubService {   // ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
  const [sensor, heater] = env === "prod"
    ? [new OneWireThermometer(), new SmartPlug()]   // справжнє залізо
    : [new FakeSensor(), new FakeHeater()];         // підробки для тесту
  const devices = new InMemoryDeviceRepository();   // SQLite стане сюди в модулі про сховище
  return new HubService(sensor, heater, devices, { threshold: 20.0 });
}

const hub = build(process.env.DH_ENV ?? "dev");
setInterval(() => hub.tick(), 30_000);       // двері 1 крутяться самі
runCli(hub, process.argv.slice(2));          // двері 2 — на команду
