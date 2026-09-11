// ClimateMonitoringServiceImpl.spec.ts
describe('ClimateMonitoringServiceImpl', () => {
  it('повинен транслювати дані з репозиторію у вихідне DTO', async () => {
    const mockEntity: ClimateSensorEntity = {
      id: 'sensor-42',
      temperature: 21.5,
      humidity: 45.0,
      batteryLevel: 88,
    };
    repositoryMock.findById.mockResolvedValue(mockEntity);

    const result = await service.getSensorMetrics('sensor-42');

    expect(repositoryMock.findById).toHaveBeenCalledWith('sensor-42');
    expect(result.batteryLevel).toBe(88);
  });
});
