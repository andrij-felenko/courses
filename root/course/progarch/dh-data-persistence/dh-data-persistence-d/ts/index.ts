class InMemoryDeviceRepository {             // за портом DeviceRepository з v2
  private devices = new Map<string, Device>();

  save(d: Device): void {
    this.devices.set(d.id, d);              // ← усе життя цієї мапи = життя процесу
  }
  all(): Device[] {
    return [...this.devices.values()];
  }
}
