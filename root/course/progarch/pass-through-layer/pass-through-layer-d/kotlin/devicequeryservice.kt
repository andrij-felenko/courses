// ============================================================================
// 1. СПРАВЖНІЙ ШАР-ПРОКЛАДКА (Middle Man)
// ============================================================================

// Цей сервіс позбавлений системної відповідальності:
// він не відкриває транзакцій, не перевіряє права і лише дзеркалює репозиторій.
class DeviceQueryService(
    private val deviceRepository: DeviceRepository
) {
    // Метод дублює сигнатуру репозиторію 1-в-1.
    // Якщо контролер викличе deviceRepository.findDeviceInfo(id) напряму —
    // поведінка системи залишиться ідентичною, але зникне зайвий проміжний шар.
    fun getDeviceInfo(id: DeviceId): DeviceInfoResponse {
        val entity = deviceRepository.findDeviceInfo(id) 
            ?: throw DeviceNotFoundException(id)
        
        return DeviceInfoResponse(
            id = entity.id,
            batteryLevel = entity.batteryLevel,
            firmwareVersion = entity.firmwareVersion
        )
    }
}

// ============================================================================
// 2. ЗОВНІ ТОНКИЙ, АЛЕ КРИТИЧНИЙ СИСТЕМНИЙ БАР'ЄР
// ============================================================================

class DeviceCommandService(
    private val lockRepository: LockRepository,
    private val securityContext: SecurityContext,
    private val outbox: TransactionalOutbox
) {
    // Всього чотири рядки координації, проте кожен тримає системний інваріант:
    @Transactional
    fun unlockDoor(deviceId: DeviceId) {
        // 1. Бар'єр безпеки: отримання контексту авторизованого орендаря
        val currentHomeId = securityContext.getCurrentHomeId()

        // 2. Ізоляція орендарів (Tenant Isolation): пошук замка суворо в межах цієї оселі
        val lock = lockRepository.findLockInHome(deviceId, currentHomeId)
            ?: throw AccessDeniedException("Пристрій не знайдено або доступ заборонено")

        // 3. Доменний інваріант: бізнес-правило переходу в новий стан і створення події
        val event = lock.unlock()

        // 4. Транзакційна атомарність: одночасне збереження стану сутності та події в Outbox
        lockRepository.save(lock)
        outbox.save(event)
    }
}
