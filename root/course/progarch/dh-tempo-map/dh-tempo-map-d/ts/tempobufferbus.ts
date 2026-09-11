// Типи канонічних команд та стану ядра
export interface CanonicalCommand {
  readonly commandId: string;
  readonly deviceId: string;
  readonly capability: string;
  readonly targetValue: number | boolean | string;
  readonly priority: 'low' | 'normal' | 'critical';
  readonly createdAt: number;
}

export interface DeviceStateSnapshot {
  readonly deviceId: string;
  readonly values: Readonly<Record<string, number | boolean | string>>;
  readonly lastUpdatedAt: number;
  readonly reachable: boolean;
}

export interface HardwareDispatcher {
  dispatchToHardware(command: CanonicalCommand): Promise<boolean>;
}

// Реалізація шини темпів
export class TempoBufferBus {
  // 1. Кеш знімків стану: швидке читання без доступу до радіомережі
  private readonly stateCache = new Map<string, DeviceStateSnapshot>();

  // 2. Черга зі злиттям (conflation map): ключ = "deviceId:capability"
  private readonly pendingCommands = new Map<string, CanonicalCommand>();
  private readonly criticalQueue: CanonicalCommand[] = [];

  // Параметри регулювання швидкості (Token Bucket)
  private readonly maxTokens: number = 10;
  private availableTokens: number = 10;
  private readonly refillIntervalMs: number = 200; // додаємо токени що 200 мс
  private isProcessing: boolean = false;

  constructor(
    private readonly dispatcher: HardwareDispatcher,
    private readonly maxQueueCapacity: number = 500
  ) {
    // Періодичне поповнення маркерного кошика
    setInterval(() => this.refillTokens(), this.refillIntervalMs);
  }

  // Швидке читання стану (мікросекундний відгук)
  public getSnapshot(deviceId: string): DeviceStateSnapshot | undefined {
    return this.stateCache.get(deviceId);
  }

  // Оновлення кешу подій ядра при надходженні телеметрії
  public updateSnapshot(
    deviceId: string,
    capability: string,
    value: number | boolean | string,
    reachable: boolean = true
  ): void {
    const existing = this.stateCache.get(deviceId);
    const updatedValues = { ...(existing?.values ?? {}), [capability]: value };

    this.stateCache.set(deviceId, {
      deviceId,
      values: updatedValues,
      lastUpdatedAt: Date.now(),
      reachable,
    });
  }

  // Прийом команди від швидкої периферії (non-blocking)
  public enqueueCommand(command: CanonicalCommand): { accepted: boolean; reason?: string } {
    if (this.pendingCommands.size + this.criticalQueue.length >= this.maxQueueCapacity) {
      // Політика скидання при переповненні
      if (command.priority !== 'critical') {
        return { accepted: false, reason: 'Буфер переповнений (Backpressure)' };
      }
    }

    if (command.priority === 'critical') {
      // Критичні аварійні команди йдуть в окрему чергу без злиття
      this.criticalQueue.push(command);
    } else {
      // Злиття команд: перезапис проміжного наміру для тієї самої сутності
      const conflationKey = `${command.deviceId}:${command.capability}`;
      this.pendingCommands.set(conflationKey, command);
    }

    this.triggerProcessing();
    return { accepted: true };
  }

  private refillTokens(): void {
    if (this.availableTokens < this.maxTokens) {
      this.availableTokens = Math.min(this.maxTokens, this.availableTokens + 2);
      this.triggerProcessing();
    }
  }

  private async triggerProcessing(): Promise<void> {
    if (this.isProcessing) {
      return;
    }
    this.isProcessing = true;

    try {
      while (this.availableTokens > 0 && (this.criticalQueue.length > 0 || this.pendingCommands.size > 0)) {
        let commandToExecute: CanonicalCommand | undefined;

        if (this.criticalQueue.length > 0) {
          commandToExecute = this.criticalQueue.shift();
        } else {
          // Витягуємо першу злиту команду з мапи
          const nextKey = this.pendingCommands.keys().next().value;
          if (nextKey) {
            commandToExecute = this.pendingCommands.get(nextKey);
            this.pendingCommands.delete(nextKey);
          }
        }

        if (!commandToExecute) {
          break;
        }

        // Списуємо токен і надсилаємо команду в повільне апаратне ядро
        this.availableTokens -= 1;
        await this.dispatcher.dispatchToHardware(commandToExecute);
      }
    } finally {
      this.isProcessing = false;
    }
  }
}
