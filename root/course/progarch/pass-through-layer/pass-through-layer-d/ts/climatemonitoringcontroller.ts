// ClimateMonitoringController.ts
@Controller('api/v1/climate/sensors')
export class ClimateMonitoringController {
  constructor(private readonly service: ClimateMonitoringService) {}

  @Get(':id')
  async getMetrics(@Param('id') id: string): Promise<ClimateMetricsResponse> {
    const dto = await this.service.getSensorMetrics(id);
    return {
      id: dto.id,
      temperature: dto.temperature,
      humidity: dto.humidity,
      batteryLevel: dto.batteryLevel,
    };
  }
}
