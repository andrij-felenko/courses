// Контролер копіює поля з сервісного DTO у вихідну модель представлення
@Get(':id')
async getMetrics(@Param('id') id: string): Promise<ClimateMetricsResponse> {
  const dto = await this.climateService.getSensorMetrics(id);
  return {
    id: dto.id,
    temperature: dto.temperature,
    humidity: dto.humidity,
    batteryLevel: dto.batteryLevel,
  };
}

// Реалізація сервісу лише перекладає поля з сутності бази у сервісний DTO
async getSensorMetrics(sensorId: string): Promise<SensorReadingDto> {
  const entity = await this.sensorRepo.findById(sensorId);
  if (!entity) {
    throw new NotFoundException(`Датчик ${sensorId} не знайдено`);
  }

  return {
    id: entity.id,
    temperature: entity.temperature,
    humidity: entity.humidity,
    batteryLevel: entity.batteryLevel,
  };
}
