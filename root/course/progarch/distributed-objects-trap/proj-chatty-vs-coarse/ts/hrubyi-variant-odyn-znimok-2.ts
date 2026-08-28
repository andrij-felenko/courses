// НА ХМАРІ пакунок знову стає об'єктом — зі СВОЄЮ поведінкою (локальною, даровою).
class CloudDevice {
  constructor(
    readonly id: string,
    readonly type: string, readonly room: string, readonly state: string,
    readonly brightness: number, readonly lastSeen: number,
  ) {}
  static fromDTO(dto: DeviceDTO): CloudDevice {
    return new CloudDevice(dto.id, dto.type, dto.room, dto.state,
                           dto.brightness, dto.lastSeen);
  }
  isStale(now: number): boolean { return now - this.lastSeen > 60; }
  label(): string { return `${this.room}: ${this.type}`; }
}

async function renderCoarse(hub: Hub, link: Link, now: number) {
  const dtos = await link.cross(() => hub.snapshot());   // 1 перехід — увесь знімок
  const devices = dtos.map(CloudDevice.fromDTO);         // пакунки → об'єкти
  for (const d of devices)
    render(d.label(), d.state, d.brightness, d.isStale(now));   // локально, дарма
}
