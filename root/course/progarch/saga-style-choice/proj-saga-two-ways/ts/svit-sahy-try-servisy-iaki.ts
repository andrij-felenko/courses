// Три сервіси DH. Кожна дія має компенсацію; прапорець down імітує відмову.
class Registry {
  reserved = new Set<string>();
  async reserve(deviceId: string, homeId: string) { this.reserved.add(deviceId); }
  async unreserve(deviceId: string)               { this.reserved.delete(deviceId); }
}
class Hub {
  configured = new Set<string>(); down = false;
  async pushConfig(homeId: string, deviceId: string) {
    if (this.down) throw new Error("хаб недоступний");
    this.configured.add(deviceId);
  }
  async wipeConfig(homeId: string, deviceId: string) { this.configured.delete(deviceId); }
}
class Billing {
  metered = new Set<string>(); down = false;
  async startMeter(homeId: string, deviceId: string) {
    if (this.down) throw new Error("білінг недоступний");
    this.metered.add(deviceId);
  }
  async stopMeter(homeId: string, deviceId: string) { this.metered.delete(deviceId); }
}

type Enroll = { homeId: string; deviceId: string };
