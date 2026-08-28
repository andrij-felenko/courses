interface HomeSnapshot { readonly heating: boolean; readonly devices: Device[]; }

class HubService {
  private heating = false;           // стан живе ТУТ, на краю ядра
  constructor(
    private sensor: Sensor,          // драйвовані порти — інтерфейси, не класи
    private heater: Heater,
    private devices: DeviceRepository,
    private cfg: Config,
  ) {}

  tick(): void {                                        // сценарій дверей 1 (цикл)
    const reading = this.sensor.read();
    this.heating = decide(reading, this.cfg, this.heating);  // те саме чисте ядро
    this.heating ? this.heater.on() : this.heater.off();
  }
  addDevice(d: Device): void { this.devices.save(d); }  // сценарій дверей 2
  state(): HomeSnapshot { return { heating: this.heating, devices: this.devices.all() }; }
  setThreshold(celsius: number): void { this.cfg = { ...this.cfg, threshold: celsius }; }
}
