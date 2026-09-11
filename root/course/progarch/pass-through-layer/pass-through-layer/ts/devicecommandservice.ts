// Справжній системний бар'єр: мінімум коду, але утримує безпеку, транзакцію та Outbox
class DeviceCommandService {
  constructor(
    private readonly txManager: TransactionManager,
    private readonly deviceRepo: DeviceRepository,
    private readonly outboxRepo: OutboxRepository,
    private readonly authorizer: SecurityContext
  ) {}

  async unlockDoor(command: UnlockDoorCommand): Promise<void> {
    // 1. Межа авторизації та ізоляції орендаря
    this.authorizer.assertHomeAccess(command.homeId);

    // 2. Атомарна зміна агрегата та збереження події
    await this.txManager.transaction(async (tx) => {
      const lock = await this.deviceRepo.findDoorLock(command.deviceId, tx);
      const event = lock.unlock(command.requestedBy);

      await this.deviceRepo.save(lock, tx);
      await this.outboxRepo.saveEvent(event, tx);
    });
  }
}

// Фіктивна прокладка: видалення класу не порушує жодної системної гарантії
class DeviceQueryService {
  constructor(private readonly deviceRepo: DeviceRepository) {}

  async getDevice(id: string): Promise<DeviceDto> {
    // Механічна трансляція без власної ролі
    return await this.deviceRepo.findById(id);
  }
}
