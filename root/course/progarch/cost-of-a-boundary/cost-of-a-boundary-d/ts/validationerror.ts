// Контракти та логіка перетину семантичної межі мовою TypeScript
interface ActivateHeaterRequestDTO {
  deviceId?: string;
  requiredPowerKw?: number;
}

class ValidationError extends Error {
  constructor(message: string) {
    super(`Семантична помилка валідації: ${message}`);
    this.name = "ValidationError";
  }
}

// Валідація DTO на межі сервісу
function validateDto(dto: ActivateHeaterRequestDTO): asserts dto is { deviceId: string; requiredPowerKw: number } {
  if (!dto.deviceId || dto.deviceId.trim().length === 0) {
    throw new ValidationError("Ідентифікатор пристрою є обов'язковим");
  }
  if (dto.requiredPowerKw === undefined || dto.requiredPowerKw === null) {
    throw new ValidationError("Поле потужності відсутнє у вхідному пакунку");
  }
  if (dto.requiredPowerKw <= 0 || dto.requiredPowerKw > 15) {
    throw new ValidationError(`Потужність ${dto.requiredPowerKw} кВт порушує межі допустимого діапазону (0, 15]`);
  }
}

interface PowerGateway {
  reserve(reservationId: string, kw: number): Promise<void>;
  release(reservationId: string): Promise<void>;
}

interface DeviceGateway {
  turnOn(deviceId: string): Promise<void>;
}

// Виконання розподіленої саги з ручним викликом компенсації
export class HeaterSagaCoordinator {
  constructor(
    private readonly powerGateway: PowerGateway,
    private readonly deviceGateway: DeviceGateway
  ) {}

  async execute(rawDto: ActivateHeaterRequestDTO): Promise<void> {
    // 1. Ручна валідація замість компіляторного контролю
    validateDto(rawDto);

    const reservationId = `res-${rawDto.deviceId}`;

    // 2. Крок 1: Локальна зміна у віддаленому сервісі енергомережі
    await this.powerGateway.reserve(reservationId, rawDto.requiredPowerKw);

    try {
      // 3. Крок 2: Віддалена команда фізичному приладу
      await this.deviceGateway.turnOn(rawDto.deviceId);
    } catch (error) {
      // Втрата атомарності: ініціалізація зворотного зв'язку компенсації
      try {
        await this.powerGateway.release(reservationId);
      } catch (compensationError) {
        throw new Error(`Незворотна семантична неузгодженість: ${compensationError}. Первинна помилка: ${error}`);
      }
      throw new Error(`Ввімкнення зірвано, зарезервовану потужність компенсовано: ${error}`);
    }
  }
}
