interface Sensor { read(): number; }
interface Heater { on(): void; off(): void; }

function decide(sensor: Sensor, heater: Heater, threshold: number) {
  const t = sensor.read();           // ← шов: чим є sensor — вирішують ЗЗОВНІ
  if (t < threshold) heater.on();
  else heater.off();
}

// точка ввімкнення — головний код обирає, ЩО під'єднати до шва:
decide(new RealSensor(), new RealHeater(), 20.0);        // продакшен
decide(new FakeSensor(19.0), new SpyHeater(), 20.0);     // тест
