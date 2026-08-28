function tick(sensor: Sensor, heater: Heater, cfg: Config): void {  // один оберт, без розкладу
  const cmd = decide(sensor.read(), cfg);
  if (cmd === "HEAT") heater.on();
  else heater.off();
}

function run(sensor: Sensor, heater: Heater, cfg: Config) {
  while (true) { tick(sensor, heater, cfg); sleep(30_000); }
}

test("cold room turns heater on", () => {
  const heater = new SpyHeater();
  tick(new FakeSensor({ celsius: 18.0, ok: true }), heater, { threshold: 20.0 });
  expect(heater.calls).toEqual(["on"]);   // холодний вимір докрутив саме розетку
});
