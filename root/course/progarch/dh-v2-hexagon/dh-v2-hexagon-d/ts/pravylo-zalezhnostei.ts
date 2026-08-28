interface HomeSnapshot {           // DTO: плаский знімок для відповіді назовні
  heating: boolean;
  devices: Device[];
}

class HubService {
  private heating = false;         // стан живе тут, на краю ядра
  constructor(
    private sensor: Sensor,        // драйвовані порти — інтерфейси, не класи
    private heater: Heater,
    private devices: DeviceRepository,
    private cfg: Config,
  ) {}

  // ── сценарій, який смикає автономний цикл ──
  tick(): void {
    const reading = this.sensor.read();                     // Sensor: read
    this.heating = decide(reading, this.cfg, this.heating); // те саме чисте ядро
    this.heating ? this.heater.on() : this.heater.off();    // Heater: act
  }

  // ── сценарії, які смикає зовнішній запит (CLI, згодом HTTP) ──
  addDevice(d: Device): void { this.devices.save(d); }                    // DeviceRepository
  state(): HomeSnapshot { return { heating: this.heating, devices: this.devices.all() }; }
  setThreshold(celsius: number): void { this.cfg = { ...this.cfg, threshold: celsius }; }
}
