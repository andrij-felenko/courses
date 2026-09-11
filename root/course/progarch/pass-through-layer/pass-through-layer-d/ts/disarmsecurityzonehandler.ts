// Асиметрична обробка запитів за патерном CQRS у системі Digital Homes

// --- 1. КОНТУР КОМАНД (MUTATION PATH): глибокий захист інваріантів ---

export interface DisarmSecurityZoneCommand {
  readonly zoneId: string;
  readonly userId: string;
  readonly pinCode: string;
}

export class DisarmSecurityZoneHandler {
  constructor(
    private readonly zoneRepository: ISecurityZoneRepository,
    private readonly unitOfWork: IUnitOfWork,
    private readonly eventPublisher: IDomainEventPublisher
  ) {}

  async handle(command: DisarmSecurityZoneCommand): Promise<void> {
    await this.unitOfWork.executeInTransaction(async () => {
      // Завантаження повного доменного агрегата з контролем блокування
      const zone = await this.zoneRepository.loadForUpdate(command.zoneId);
      if (!zone) {
        throw new Error(`Зону безпеки ${command.zoneId} не знайдено`);
      }

      // Доменний інваріант: перевірка пін-коду та захист від підбору
      zone.disarm(command.pinCode, new Date());

      // Фіксація змін агрегата та відправлення подій
      await this.zoneRepository.save(zone);
      await this.eventPublisher.publishAll(zone.releaseEvents());
    });
  }
}

// --- 2. КОНТУР ЗАПИТІВ (READ BYPASS): плоска проекція без доменних сутностей ---

export interface HomeDashboardDto {
  readonly homeId: string;
  readonly securityStatus: 'ARMED' | 'DISARMED' | 'TRIGGERED';
  readonly activeAlertsCount: number;
  readonly averageTemperature: number;
  readonly lowBatteryDeviceCount: number;
}

export class GetHomeDashboardHandler {
  constructor(private readonly dbConnection: IDbConnection) {}

  // Прямий запит до бази даних: результат одразу проектується у вихідне DTO
  async handle(homeId: string): Promise<HomeDashboardDto> {
    const rawData = await this.dbConnection.queryOne<HomeDashboardDto>(
      `SELECT
         h.id AS homeId,
         s.status AS securityStatus,
         COUNT(DISTINCT a.id) AS activeAlertsCount,
         COALESCE(AVG(t.current_temperature), 20.0) AS averageTemperature,
         COUNT(DISTINCT CASE WHEN d.battery_level < 20 THEN d.id END) AS lowBatteryDeviceCount
       FROM homes h
       LEFT JOIN security_zones s ON s.home_id = h.id
       LEFT JOIN security_alerts a ON a.home_id = h.id AND a.is_resolved = false
       LEFT JOIN thermostats t ON t.home_id = h.id
       LEFT JOIN devices d ON d.home_id = h.id
       WHERE h.id = $1
       GROUP BY h.id, s.status`,
      [homeId]
    );

    if (!rawData) {
      throw new Error(`Будинок з ідентифікатором ${homeId} не знайдено`);
    }

    return rawData;
  }
}
