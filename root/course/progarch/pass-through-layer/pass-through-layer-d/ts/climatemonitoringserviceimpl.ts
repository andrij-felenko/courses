// ClimateMonitoringServiceImpl.ts
@Injectable()
export class ClimateMonitoringServiceImpl implements ClimateMonitoringService {
  constructor(private readonly repository: ClimateSensorRepository) {}

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
