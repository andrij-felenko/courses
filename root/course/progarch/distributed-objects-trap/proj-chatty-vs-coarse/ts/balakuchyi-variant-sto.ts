// НА ХАБІ — справжні об'єкти з поведінкою. Геттери локальні, тобто дарові.
class Device {
  constructor(
    readonly id: string,
    private _type: string, private _room: string, private _state: string,
    private _brightness: number, private _lastSeen: number,
  ) {}
  type()       { return this._type; }
  room()       { return this._room; }
  state()      { return this._state; }
  brightness() { return this._brightness; }
  lastSeen()   { return this._lastSeen; }
}

class Hub {
  private devices = new Map<string, Device>();
  register(d: Device) { this.devices.set(d.id, d); }
  get(id: string): Device {
    const d = this.devices.get(id);
    if (!d) throw new Error(`no device ${id}`);
    return d;
  }
  ids(): string[] { return [...this.devices.keys()]; }
}
