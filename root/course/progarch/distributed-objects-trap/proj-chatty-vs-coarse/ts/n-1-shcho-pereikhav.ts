class Radio {                    // друга межа: синхронний драйвер заліза
  reads = 0;
  read(id: string): string { this.reads++; return "on"; }   // кожне читання — перехід
}

class HubLive {
  private devices = new Map<string, Device>();
  constructor(private radio: Radio) {}
  // ... register / ids ...
  snapshot(): DeviceDTO[] {
    const out: DeviceDTO[] = [];
    for (const d of this.devices.values())
      out.push({ v: 1, id: d.id, type: d.type(), room: d.room(),
                 state: this.radio.read(d.id),          // ← прихований перехід на кожен!
                 brightness: d.brightness(), lastSeen: d.lastSeen() });
    return out;
  }
}
// cloudLink.crossings === 1     ← грубо, як домовлялись
// radio.reads       === 30      ← балакучий N+1, лише сховався всередину
