// Стани життєвого циклу команди керування
export type CommandStatus = 'PENDING' | 'APPLIED' | 'REJECTED';

// Директива наміру керування пристроєм
export interface CommandIntent {
  // Унікальний мережевий ідентифікатор повідомлення
  commandId: string;
  // Ключ ідемпотентності бізнес-дії для дедуплікації
  idempotencyKey: string;
  // Наскрізний ідентифікатор розподіленого трасування
  correlationId: string;
  // Цільовий фізичний пристрій
  targetDeviceId: string;
  // Цільова можливість
  targetCapability: 'on_off' | 'brightness' | 'target_temperature';
  // Бажаний стан у канонічних одиницях SI
  desiredValue: Record<string, unknown>;
  // Час створення директиви на клієнті
  issuedAt: string;
  // Граничний час чинності команди (захист від запізнілого виконання)
  expiresAt: string;
}

// Результат обробки команди керування
export interface CommandResult {
  commandId: string;
  idempotencyKey: string;
  status: CommandStatus;
  // Причина відхилення (у разі REJECTED)
  rejectReason?: string;
  // Оновлений моментальний знімок стану пристрою
  updatedState?: Record<string, unknown>;
}

// Інтерфейс диспетчера команд із вбудованою дедуплікацією
export class IdempotentCommandDispatcher {
  // Буфер нещодавніх ключів ідемпотентності з їхніми результатами
  private readonly idempotencyCache: Map<string, CommandResult> = new Map();

  public async executeCommand(
    intent: CommandIntent,
    radioSender: (intent: CommandIntent) => Promise<boolean>
  ): Promise<CommandResult> {
    const now = new Date();
    const expiryDate = new Date(intent.expiresAt);

    // 1. Перевірка актуальності часу життя команди
    if (now.getTime() > expiryDate.getTime()) {
      return {
        commandId: intent.commandId,
        idempotencyKey: intent.idempotencyKey,
        status: 'REJECTED',
        rejectReason: 'COMMAND_EXPIRED',
      };
    }

    // 2. Перевірка на дублювання за ключем ідемпотентності
    const existing = this.idempotencyCache.get(intent.idempotencyKey);
    if (existing) {
      // Повертаємо попередньо зареєстрований стан без повторного смикання заліза
      return existing;
    }

    // 3. Реєструємо статус PENDING перед відправкою в радіошину
    const pendingResult: CommandResult = {
      commandId: intent.commandId,
      idempotencyKey: intent.idempotencyKey,
      status: 'PENDING',
    };
    this.idempotencyCache.set(intent.idempotencyKey, pendingResult);

    try {
      // 4. Безпосередня взаємодія з драйвером радіомодуля
      const isDelivered = await radioSender(intent);

      if (isDelivered) {
        const appliedResult: CommandResult = {
          commandId: intent.commandId,
          idempotencyKey: intent.idempotencyKey,
          status: 'APPLIED',
          updatedState: intent.desiredValue,
        };
        this.idempotencyCache.set(intent.idempotencyKey, appliedResult);
        return appliedResult;
      } else {
        const failedResult: CommandResult = {
          commandId: intent.commandId,
          idempotencyKey: intent.idempotencyKey,
          status: 'REJECTED',
          rejectReason: 'DEVICE_UNREACHABLE_NO_ACK',
        };
        this.idempotencyCache.set(intent.idempotencyKey, failedResult);
        return failedResult;
      }
    } catch (error) {
      const errorResult: CommandResult = {
        commandId: intent.commandId,
        idempotencyKey: intent.idempotencyKey,
        status: 'REJECTED',
        rejectReason: 'COORDINATOR_DISPATCH_FAILURE',
      };
      this.idempotencyCache.set(intent.idempotencyKey, errorResult);
      return errorResult;
    }
  }
}
