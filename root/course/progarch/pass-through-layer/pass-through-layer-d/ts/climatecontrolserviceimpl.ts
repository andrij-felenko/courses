// Приклад 1: Повноцінний сервіс із захистом інваріантів
@Injectable()
export class ClimateControlServiceImpl implements ClimateControlService {
  constructor(
    private readonly heaterRepository: HeaterRepository,
    private readonly windowRepository: WindowSensorRepository,
    private readonly eventBus: EventBus
  ) {}

  async setTargetTemperature(roomId: string, targetTemp: number): Promise<void> {
    // 1. Перевірка системного інваріанта: неприпустимість нагріву при відкритих вікнах
    const hasOpenWindows = await this.windowRepository.hasOpenWindowsInRoom(roomId);
    if (hasOpenWindows) {
      throw new DomainValidationException('Неможливо увімкнути опалення: у кімнаті відчинені вікна');
    }

    // 2. Координація стану та зміна агрегату
    const heater = await this.heaterRepository.findByRoomId(roomId);
    if (!heater) {
      throw new EntityNotFoundException(`Обігрівач у кімнаті ${roomId} не знайдено`);
    }

    heater.updateTargetTemperature(targetTemp);
    await this.heaterRepository.save(heater);

    // 3. Публікація доменної події
    await this.eventBus.publish(new TemperatureTargetChangedEvent(roomId, targetTemp));
  }
}

// Приклад 2: Шар-прокладка без власної поведінки
@Injectable()
export class ClimateMonitoringServiceImpl implements ClimateMonitoringService {
  constructor(private readonly repository: ClimateSensorRepository) {}

  // Метод є дзеркалом репозиторію з тотожним мапінгом без інваріантів
  async getSensorMetrics(sensorId: string): Promise<SensorReadingDto> {
    const entity = await this.repository.findById(sensorId);
    if (!entity) {
      throw new EntityNotFoundException(`Датчик ${sensorId} не знайдено`);
    }
    return {
      id: entity.id,
      temperature: entity.temperature,
      humidity: entity.humidity,
      batteryLevel: entity.batteryLevel,
    };
  }
}
