/**
 * Монітор телеметрії (TelemetryMonitor).
 * Здійснює неблокуюче періодичне опитування датчиків актуатора за квантами часу.
 * Аналізує динаміку фізичних показників та детектує механічне заклинювання
 * за сплеском споживаного струму (перевантаження) або браком приросту координат вала.
 */
import { ActuatorHardwareSimulator } from './hardware-simulator.ts';
import { TelemetryData } from './types.ts';

export interface StallDetectionConfig {
  readonly currentThresholdAmps: number;    // Граничний струм аварії (наприклад, 2.5 A)
  readonly minProgressTicks: number;        // Мінімальний приріст енкодера за вікно
  readonly maxStallSamples: number;         // Кількість підтверджень аномалії поспіль
  readonly pollQuantumMs: number;           // Часовий квант опитування (наприклад, 20 мс)
}

export const DEFAULT_MONITOR_CONFIG: StallDetectionConfig = {
  currentThresholdAmps: 2.5,
  minProgressTicks: 2,
  maxStallSamples: 2,
  pollQuantumMs: 20
};

export class TelemetryMonitor {
  private readonly config: StallDetectionConfig;
  private consecutiveOvercurrentCount = 0;
  private consecutiveZeroProgressCount = 0;
  private lastEncoderTicks: number | null = null;
  private lastSample: TelemetryData | null = null;

  constructor(config: Partial<StallDetectionConfig> = {}) {
    this.config = { ...DEFAULT_MONITOR_CONFIG, ...config };
  }

  /**
   * Скидання внутрішніх лічильників перед початком нового руху.
   */
  public reset(): void {
    this.consecutiveOvercurrentCount = 0;
    this.consecutiveZeroProgressCount = 0;
    this.lastEncoderTicks = null;
    this.lastSample = null;
  }

  /**
   * Опитування датчиків за один часовий квант та перевірка наявності аномалій.
   * Повертає знімок телеметрії та прапорець виявлення заклинювання.
   */
  public async pollQuantum(hardware: ActuatorHardwareSimulator): Promise<{
    telemetry: TelemetryData;
    isStalled: boolean;
    stallReason?: string;
  }> {
    const telemetry = await hardware.readTelemetry();
    this.lastSample = telemetry;

    // Якщо мотор знеструмлено, аналіз заклинювання не проводиться
    if (!telemetry.motorEnergized) {
      this.lastEncoderTicks = telemetry.encoderTicks;
      return { telemetry, isStalled: false };
    }

    let isStalled = false;
    let stallReason: string | undefined;

    // 1. Детекція заклинювання за надструмом (Stall current spike)
    if (telemetry.currentAmperes >= this.config.currentThresholdAmps) {
      this.consecutiveOvercurrentCount++;
      if (this.consecutiveOvercurrentCount >= this.config.maxStallSamples) {
        isStalled = true;
        stallReason = `Сплеск струму двигуна: ${telemetry.currentAmperes} A (поріг ${this.config.currentThresholdAmps} A)`;
      }
    } else {
      this.consecutiveOvercurrentCount = 0;
    }

    // 2. Детекція заклинювання за браком приросту енкодера при поданій напрузі
    if (this.lastEncoderTicks !== null && !isStalled) {
      const progress = Math.abs(telemetry.encoderTicks - this.lastEncoderTicks);
      if (progress < this.config.minProgressTicks) {
        this.consecutiveZeroProgressCount++;
        if (this.consecutiveZeroProgressCount >= this.config.maxStallSamples + 2) {
          isStalled = true;
          stallReason = `Вал не обертається при поданій напрузі: приріст енкодера ${progress} імпульсів`;
        }
      } else {
        this.consecutiveZeroProgressCount = 0;
      }
    }

    this.lastEncoderTicks = telemetry.encoderTicks;

    return { telemetry, isStalled, stallReason };
  }

  public getLastSample(): TelemetryData | null {
    return this.lastSample;
  }

  public getQuantumMs(): number {
    return this.config.pollQuantumMs;
  }
}
