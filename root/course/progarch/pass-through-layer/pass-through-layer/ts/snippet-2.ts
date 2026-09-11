// Тавтологічний тест перевіряє факт написання коду, а не поведінку системи
test('getSensorMetrics викликає репозиторій з переданим ідентифікатором', async () => {
  const mockRepo = {
    findById: jest.fn().mockResolvedValue({
      id: 'sensor-1',
      temperature: 22.0,
      humidity: 50,
      batteryLevel: 90,
    }),
  };

  const service = new ClimateMonitoringServiceImpl(mockRepo as any);
  const result = await service.getSensorMetrics('sensor-1');

  expect(mockRepo.findById).toHaveBeenCalledWith('sensor-1');
  expect(result.batteryLevel).toBe(90);
});
