interface DeviceRepo { save(agg: DeviceAggregate): void; }
interface EventBus  { publish(event: { type: string; id: string }): void; }

// ❌ Надмір: обряд багатого домену над тим, у чому інваріантів НЕМА.
class DeviceAggregate {
  private constructor(private device: Device) {}

  static register(id: DeviceId, room: RoomName,
                  kind: DeviceKind, name: string): DeviceAggregate {
    return new DeviceAggregate({ id, room, kind, name });   // фабрика, що нічого не стереже
  }
  rename(name: string): void {
    this.device = { ...this.device, name };                 // сетер, перевдягнений у «поведінку»
  }
  get snapshot(): Device { return this.device; }
}

interface RegisterDeviceCommand { id: string; room: string; kind: DeviceKind; name: string; }

class RegisterDeviceHandler {
  constructor(private repo: DeviceRepo, private bus: EventBus) {}
  handle(cmd: RegisterDeviceCommand): void {
    const agg = DeviceAggregate.register(
      deviceId(cmd.id), roomName(cmd.room), cmd.kind, cmd.name);
    this.repo.save(agg);
    this.bus.publish({ type: "DeviceRegistered", id: cmd.id });  // подія, на яку ніхто не підписаний
  }
}
