function run(sensor: Sensor, heater: Heater, cfg: Config) {
  while (true) {
    const reading = sensor.read();        // драйвер ховає діалект заліза
    const cmd = decide(reading, cfg);     // чисте рішення — саме лише °C усередині
    if (cmd === "HEAT") heater.on();
    else heater.off();
    sleep(30);
  }
}

// єдине місце, де конкретне зустрічає конкретне:
run(new OneWireThermometer(), new SmartPlug(), { threshold: 20.0 });
