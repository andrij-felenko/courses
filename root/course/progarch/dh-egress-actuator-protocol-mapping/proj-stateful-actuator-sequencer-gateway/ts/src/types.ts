/**
 * Доменні типи, об'єкти значень (Value Objects), стани скінченного автомата
 * та контракти вихідного порту для взаємодії з апаратним актуатором.
 */

/**
 * Незмінний об'єкт значення ідентифікатора актуатора.
 */
export class ActuatorId {
  private readonly _value: string;

  constructor(value: string) {
    const trimmed = value.trim();
    if (!trimmed) {
      throw new Error('ActuatorId не може бути порожнім');
    }
    this._value = trimmed;
  }

  public get value(): string {
    return this._value;
  }

  public equals(other: ActuatorId): boolean {
    return this._value === other._value;
  }

  public toString(): string {
    return this._value;
  }
}

/**
 * Об'єкт значення відсотка позиції [0.0 .. 100.0]%.
 * Гарантує фізичну валідність координати ще на рівні доменного ядра,
 * унеможливлюючи вихід за межі механічних упорів.
 */
export class Percentage {
  private readonly _value: number;

  constructor(value: number) {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      throw new Error(`Некоректне значення відсотка: ${value}`);
    }
    if (value < 0.0 || value > 100.0) {
      throw new Error(`Відсоток має бути в діапазоні [0.0 .. 100.0], отримано: ${value}`);
    }
    // Округлення до 2 знаків після коми для стабільності калібрування
    this._value = Math.round(value * 100) / 100;
  }

  public get value(): number {
    return this._value;
  }

  public equals(other: Percentage, tolerance = 0.5): boolean {
    return Math.abs(this._value - other._value) <= tolerance;
  }

  public toString(): string {
    return `${this._value.toFixed(1)}%`;
  }
}

/**
 * Простий токен скасування операції (CancellationToken)
 * для підтримки кооперативного переривання тривалих апаратних дій.
 */
export class CancellationToken {
  private _isCancelled = false;
  private readonly callbacks: Array<() => void> = [];

  public get isCancelled(): boolean {
    return this._isCancelled;
  }

  public cancel(): void {
    if (!this._isCancelled) {
      this._isCancelled = true;
      for (const cb of this.callbacks) {
        cb();
      }
    }
  }

  public onCancelled(callback: () => void): void {
    if (this._isCancelled) {
      callback();
    } else {
      this.callbacks.push(callback);
    }
  }

  public throwIfCancelled(): void {
    if (this._isCancelled) {
      throw new Error('Операцію скасовано за запитом CancellationToken');
    }
  }
}

/**
 * Контекст виклику операції з дедлайном (WCET - Worst-Case Execution Time)
 * та маркером скасування.
 */
export interface CallContext {
  readonly deadlineMs: number;
  readonly cancellationToken?: CancellationToken;
  readonly correlationId?: string;
}

/**
 * Декларативна доменна команда позиціонування актуатора.
 */
export interface SetPositionCommand {
  readonly actuatorId: ActuatorId;
  readonly targetPosition: Percentage;
  readonly context: CallContext;
}

/**
 * Стани кінцевого автомата секвенсера (FSM) життєвого циклу актуатора.
 */
export enum ActuatorState {
  IDLE = 'IDLE',
  CHECKING_POWER = 'CHECKING_POWER',
  RELEASING_BRAKE = 'RELEASING_BRAKE',
  APPLYING_TORQUE = 'APPLYING_TORQUE',
  MOVING = 'MOVING',
  VERIFYING_POSITION = 'VERIFYING_POSITION',
  ENGAGING_BRAKE = 'ENGAGING_BRAKE',
  HOLDING = 'HOLDING',
  FAIL_SAFE = 'FAIL_SAFE',
  INTERLOCKED = 'INTERLOCKED'
}

/**
 * Типізовані доменні коди апаратних відмов (Domain Error Codes).
 */
export enum ActuatorErrorCode {
  MECHANICAL_STALL = 'MECHANICAL_STALL',
  DEVICE_OFFLINE = 'DEVICE_OFFLINE',
  TIMEOUT_EXPIRED = 'TIMEOUT_EXPIRED',
  COMMAND_REJECTED = 'COMMAND_REJECTED',
  HARDWARE_FAULT = 'HARDWARE_FAULT'
}

/**
 * Знімок низькорівневої телеметрії з датчиків актуатора.
 */
export interface TelemetryData {
  readonly currentAmperes: number;
  readonly encoderTicks: number;
  readonly positionPct: number;
  readonly brakeEngaged: boolean;
  readonly motorEnergized: boolean;
  readonly powerGood: boolean;
  readonly timestamp: number;
}

/**
 * Типізований звіт про виконання апаратної дії, що повертається в доменне ядро.
 * Повністю ізолює бізнес-логіку від винятків транспортного та фізичного рівнів.
 */
export interface ActuatorExecutionReport {
  readonly success: boolean;
  readonly actuatorId: ActuatorId;
  readonly requestedPosition: Percentage;
  readonly actualPosition: Percentage;
  readonly durationMs: number;
  readonly finalState: ActuatorState;
  readonly isSafetyInterlocked: boolean;
  readonly error?: {
    readonly code: ActuatorErrorCode;
    readonly message: string;
    readonly telemetrySnapshot?: TelemetryData;
  };
}

/**
 * Контракт вихідного гексагонального порту (Egress Port) для керування актуатором.
 * Доменне ядро володіє цим інтерфейсом і взаємодіє з периферією виключно через нього.
 */
export interface ActuatorOutboundPort {
  execute(command: SetPositionCommand): Promise<ActuatorExecutionReport>;
  emergencyStop(actuatorId: ActuatorId, reason: string): Promise<ActuatorExecutionReport>;
  queryState(actuatorId: ActuatorId): Promise<{
    currentState: ActuatorState;
    position: Percentage;
    isInterlocked: boolean;
  }>;
  resetSafetyInterlock(actuatorId: ActuatorId): Promise<boolean>;
}
