// Канал команд (запис): суворий захист інваріантів через доменний агрегат
class SecurityZoneController {
  constructor(private readonly commandService: ArmZoneCommandService) {}

  async arm(zoneId: string, req: ArmZoneRequest): Promise<void> {
    await this.commandService.execute({
      zoneId,
      code: req.securityPin,
      initiatedBy: req.userId
    });
  }
}

// Канал запитів (читання): вільний обхід прокладок через пряму проєкцію у DTO
class DashboardController {
  constructor(private readonly readRepo: IDashboardReadRepository) {}

  async getHomeSummary(homeId: string): Promise<HomeDashboardDto> {
    // Пряма SQL-проєкція зі сховища у DTO без завантаження важких доменних сутностей
    return await this.readRepo.fetchDashboardByHomeId(homeId);
  }
}
