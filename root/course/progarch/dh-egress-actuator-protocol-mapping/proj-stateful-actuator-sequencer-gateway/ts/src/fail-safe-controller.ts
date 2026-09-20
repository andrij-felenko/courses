/**
 * Контролер аварійного відкату та безпеки (FailSafeController).
 * Забезпечує детермінований протокольний ланцюжок переведення у безпечний стан:
 * 1. Негайне знеструмлення двигуна (cutMotorPower).
 * 2. Витримка мертвого часу (dead time) для згасання індуктивності та зупинки вала перед ударом гальма.
 * 3. Надійне затискання механічного стопорного гальма.
 * 4. Активація блокування safety interlock, що унеможливлює подальші рухи без явного скидання оператором.
 */
import { ActuatorHardwareSimulator } from './hardware-simulator.ts';
import { ActuatorErrorCode, TelemetryData } from './types.ts';

export interface FailSafeConfig {
  readonly deadTimeMs: number; // Мертвий час для згасання ЕРС самоіндукції (наприклад, 30 мс)
}

export class FailSafeController {
  private readonly config: FailSafeConfig;
  private isInterlocked: boolean = false;
  private lastInterlockReason: string | null = null;
  private lastTelemetrySnapshot: TelemetryData | null = null;

  constructor(config: FailSafeConfig = { deadTimeMs: 30 }) {
    this.config = config;
  }

  public isSafetyInterlocked(): boolean {
    return this.isInterlocked;
  }

  public getInterlockReason(): string | null {
    return this.lastInterlockReason;
  }

  public getLastTelemetry(): TelemetryData | null {
    return this.lastTelemetrySnapshot;
  }

  /**
   * Виконання гарантованого детермінованого ланцюжка безпеки Fail-Safe.
   */
  public async executeEmergencyRollback(
    hardware: ActuatorHardwareSimulator,
    reason: string,
    errorCode: ActuatorErrorCode
  ): Promise<{ snapshot: TelemetryData | null; interlocked: boolean }> {
    this.lastInterlockReason = `[${errorCode}] ${reason}`;

    try {
      // КРОК 1: Негайне зняття живлення з двигуна для запобігання перегріву та руйнуванню зубів шестерень
      await hardware.cutMotorPower();
    } catch {
      // Поглинаємо помилку: продовжуємо ланцюжок безпеки
    }

    // КРОК 2: Витримка мертвого часу (Dead Time)
    // Захищає від удару стопорного гальма по ротору, що ще обертається,
    // та гасить індуктивні струми перехідного процесу
    await this.delay(this.config.deadTimeMs);

    try {
      // КРОК 3: Фіксація механічним гальмом
      await hardware.engageBrake();
    } catch {
      // Поглинаємо помилку шини: механіка гальма підпружинена у fail-safe положення
    }

    // Зчитуємо фінальну телеметрію для діагностичного звіту
    try {
      this.lastTelemetrySnapshot = await hardware.readTelemetry();
    } catch {
      this.lastTelemetrySnapshot = null;
    }

    // КРОК 4: Активація апаратного запобіжника (Safety Interlock)
    this.isInterlocked = true;

    return {
      snapshot: this.lastTelemetrySnapshot,
      interlocked: this.isInterlocked
    };
  }

  /**
   * Скидання апаратного блокування відповідальним оператором або сервісом.
   */
  public resetInterlock(): boolean {
    this.isInterlocked = false;
    this.lastInterlockReason = null;
    return true;
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
