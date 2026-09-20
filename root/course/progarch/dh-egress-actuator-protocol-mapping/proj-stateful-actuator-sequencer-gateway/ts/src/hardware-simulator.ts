/**
 * Симулятор фізичного приводу актуатора.
 * Моделює електродвигун постійного струму, стопорне електромагнітне гальмо,
 * датчик струму шунта та оптичний/магнітний енкодер кута/позиції.
 * Дозволяє імітувати рух, тертя, індуктивні перехідні процеси та аварійні заклинювання.
 */
import { TelemetryData } from './types.ts';

export class ActuatorHardwareSimulator {
  private readonly actuatorId: string;
  private currentPositionPct: number = 0.0;

  // Фізичний стан апаратури
  private powerGood: boolean = true;
  private brakeEngaged: boolean = true; // За замовчуванням затиснуте пружиною (fail-safe)
  private motorEnergized: boolean = false;
  private motorDirection: 'FORWARD' | 'REVERSE' | 'STOP' = 'STOP';
  private motorPowerPct: number = 0;

  // Імітація аномалій для тестів
  private forcedStallAtPosition: number | null = null;
  private isMechanicallyJammed: boolean = false;
  private simulateCommDrop: boolean = false;

  constructor(actuatorId: string, initialPositionPct: number = 0.0) {
    this.actuatorId = actuatorId;
    this.currentPositionPct = Math.max(0, Math.min(100, initialPositionPct));
  }

  /**
   * Перевірка шини живлення та готовності силової частини.
   */
  public async checkPower(): Promise<boolean> {
    if (this.simulateCommDrop) {
      throw new Error('COMM_TIMEOUT: Пристрій не відповідає на шині RS-485');
    }
    return this.powerGood;
  }

  /**
   * Подача напруги на електромагніт розтискання гальма (зняття стопора).
   */
  public async releaseBrake(): Promise<void> {
    if (this.simulateCommDrop) {
      throw new Error('COMM_TIMEOUT: Помилка передачі кадру розтискання гальма');
    }
    this.brakeEngaged = false;
  }

  /**
   * Зняття напруги з соленоїда: пружина миттєво затискає фрикційне гальмо.
   */
  public async engageBrake(): Promise<void> {
    this.brakeEngaged = true;
  }

  /**
   * Подача живлення на обмотки двигуна.
   */
  public async setMotorPower(powerPct: number, direction: 'FORWARD' | 'REVERSE'): Promise<void> {
    if (this.simulateCommDrop) {
      throw new Error('COMM_TIMEOUT: Помилка шини при активації приводу');
    }
    if (!this.powerGood) {
      throw new Error('POWER_FAULT: Відсутня напруга на силовій шині');
    }
    this.motorEnergized = true;
    this.motorPowerPct = Math.max(0, Math.min(100, powerPct));
    this.motorDirection = direction;
  }

  /**
   * Негайне зняття тяги (знеструмлення мотора).
   */
  public async cutMotorPower(): Promise<void> {
    this.motorEnergized = false;
    this.motorPowerPct = 0;
    this.motorDirection = 'STOP';
  }

  /**
   * Зчитування аналогових і цифрових сигналів датчиків актуатора.
   */
  public async readTelemetry(): Promise<TelemetryData> {
    if (this.simulateCommDrop) {
      throw new Error('COMM_TIMEOUT: Датчики не відповідають');
    }

    // Розрахунок струму:
    // Якщо мотор вимкнено - струм спокою (~0.1 A)
    // Якщо мотор увімкнено і гальмо розтиснуте - робочий струм (~0.9 .. 1.3 A)
    // Якщо заклинило або мотор бореться з гальмом - струм перевантаження (3.2 A)
    let current = 0.1;
    if (this.motorEnergized) {
      if (this.brakeEngaged || this.isMechanicallyJammed) {
        current = 3.2; // Сплеск струму при блокуванні ротора
      } else {
        current = 0.9 + (this.motorPowerPct / 100) * 0.4;
      }
    }

    const encoderTicks = Math.round(this.currentPositionPct * 40.96); // 12-бітний енкодер (4096 імпульсів = 100%)

    return {
      currentAmperes: Math.round(current * 100) / 100,
      encoderTicks,
      positionPct: Math.round(this.currentPositionPct * 10) / 10,
      brakeEngaged: this.brakeEngaged,
      motorEnergized: this.motorEnergized,
      powerGood: this.powerGood,
      timestamp: Date.now()
    };
  }

  /**
   * Симуляційний квант часу: переміщує механізм залежно від стану двигуна й гальма.
   */
  public simulateStep(deltaMs: number): void {
    if (!this.motorEnergized || this.brakeEngaged) {
      return;
    }

    // Перевірка на примусове заклинювання
    if (this.forcedStallAtPosition !== null) {
      const reachedStallPoint =
        (this.motorDirection === 'FORWARD' && this.currentPositionPct >= this.forcedStallAtPosition) ||
        (this.motorDirection === 'REVERSE' && this.currentPositionPct <= this.forcedStallAtPosition);

      if (reachedStallPoint) {
        this.isMechanicallyJammed = true;
        return; // Вал заклинило: обертання припиняється
      }
    }

    if (this.isMechanicallyJammed) {
      return;
    }

    // Швидкість переміщення: ~50% шкали на секунду при 100% тяги
    const speedPerSec = 50.0 * (this.motorPowerPct / 100);
    const stepDelta = (speedPerSec * deltaMs) / 1000;

    if (this.motorDirection === 'FORWARD') {
      this.currentPositionPct = Math.min(100.0, this.currentPositionPct + stepDelta);
    } else if (this.motorDirection === 'REVERSE') {
      this.currentPositionPct = Math.max(0.0, this.currentPositionPct - stepDelta);
    }
  }

  public forceStallAt(positionPct: number): void {
    this.forcedStallAtPosition = positionPct;
  }

  public clearFaults(): void {
    this.forcedStallAtPosition = null;
    this.isMechanicallyJammed = false;
    this.simulateCommDrop = false;
    this.powerGood = true;
  }

  public setPowerGood(state: boolean): void {
    this.powerGood = state;
  }

  public setCommDrop(state: boolean): void {
    this.simulateCommDrop = state;
  }

  public getActuatorId(): string {
    return this.actuatorId;
  }
}
