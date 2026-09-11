// Контролер пристроїв Digital Homes з відкритою шаровою моделлю
export interface BatteryStatusDto {
  readonly deviceId: string;
  readonly percentage: number;
  readonly isLowPower: boolean;
  readonly updatedAt: Date;
}

export interface IDeviceReadRepository {
  findBatteryLevel(deviceId: string): Promise<BatteryStatusDto | null>;
}

export interface ArmZoneRequest {
  readonly userId: string;
  readonly pinCode: string;
}

export class DeviceController {
  constructor(
    private readonly deviceReadRepo: IDeviceReadRepository,
    private readonly securityService: SecurityCommandService
  ) {}

  // Прямий відкритий обхід: тривіальне читання заряду батареї без проміжного сервісу
  async getBatteryStatus(deviceId: string): Promise<BatteryStatusDto> {
    const status = await this.deviceReadRepo.findBatteryLevel(deviceId);
    if (!status) {
      throw new Error(`Пристрій ${deviceId} не знайдено`);
    }
    return status;
  }

  // Закрита межа: мутація стану вимагає валідації доменних інваріантів у сервісі
  async armZone(zoneId: string, request: ArmZoneRequest): Promise<void> {
    await this.securityService.armZone({
      zoneId,
      userId: request.userId,
      pinCode: request.pinCode,
      requestedAt: new Date()
    });
  }
}
