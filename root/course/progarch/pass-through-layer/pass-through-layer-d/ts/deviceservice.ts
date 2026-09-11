// ── Початковий стан: анемічний сервіс-посередник із псевдокоординацією ──

export interface IDeviceService {
  getDevice(id: string): Promise<DeviceServiceDto>;
  getActiveSensors(roomId: string): Promise<DeviceServiceDto[]>;
}

export class DeviceService implements IDeviceService {
  constructor(private readonly deviceRepo: DeviceRepository) {}

  // Однорядкова трансляція виклику: чистий посередник
  async getDevice(id: string): Promise<DeviceServiceDto> {
    const entity = await this.deviceRepo.findById(id);
    if (!entity) {
      throw new NotFoundException(`Пристрій ${id} не знайдено`);
    }
    return this.toServiceDto(entity);
  }

  // Псевдокоординація: викачування всіх сутностей кімнати з фільтрацією в пам'яті
  async getActiveSensors(roomId: string): Promise<DeviceServiceDto[]> {
    const devices = await this.deviceRepo.findByRoomId(roomId);
    return devices
      .filter((d) => d.type === 'sensor' && d.isActive)
      .map((d) => this.toServiceDto(d));
  }

  private toServiceDto(entity: DeviceEntity): DeviceServiceDto {
    return {
      id: entity.id,
      roomId: entity.roomId,
      type: entity.type,
      name: entity.name,
      batteryLevel: entity.batteryLevel,
      isActive: entity.isActive,
    };
  }
}
