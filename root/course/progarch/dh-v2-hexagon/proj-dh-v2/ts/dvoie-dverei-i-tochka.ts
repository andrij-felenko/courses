import { createInterface } from "node:readline";

function runLoop(hub: HubService): NodeJS.Timeout {   // двері 1: тік на таймері подієвого циклу
  return setInterval(() => hub.tick(), 30_000);       // не OS-потік — сам подієвий цикл
}

function runCli(hub: HubService): void {              // двері 2: читаємо рядки, не блокуючи цикл
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {
    const [cmd, ...rest] = line.trim().split(/\s+/);
    if (cmd === "state") {
      const s = hub.state();
      console.log(`heating=${s.heating}, пристроїв=${s.devices.length}`);
    } else if (cmd === "set-threshold") {
      hub.setThreshold(Number(rest[0])); console.log(`поріг → ${rest[0]} °C`);
    } else if (cmd === "add") {
      hub.addDevice({ kind: rest[0], room: rest[1], state: "unknown" });
      console.log(`додано ${rest[0]} у ${rest[1]}`);
    } else if (cmd === "quit") rl.close();
  });
}

function build(env: string): HubService {            // ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
  const [sensor, heater]: [Sensor, Heater] = env === "prod"
    ? [new OneWireThermometer("28-0119a1b2c3d4"), new SmartPlug("http://192.168.1.50")]  // залізо
    : [new FakeSensor(), new FakeHeater()];          // підробки
  const devices = new InMemoryDeviceRepository();    // SQLite стане сюди пізніше
  return new HubService(sensor, heater, devices, { threshold: 20.0 });
}

const hub = build(process.env.DH_ENV ?? "dev");
runLoop(hub);   // цокає у фоні подієвого циклу
runCli(hub);    // а ми читаємо команди — обидві двері, один hub
