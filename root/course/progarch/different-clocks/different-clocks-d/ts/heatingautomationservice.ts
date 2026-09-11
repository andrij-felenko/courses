// --- 1. СТАБІЛЬНЕ ЯДРО (I = 0) ---

// core/heating-plan.ts
// Доменна сутність: не залежить від жодних зовнішніх бібліотек.
export interface EnergyRate {
  readonly pricePerKwh: number;
  readonly currency: string;
  readonly validUntil: Date;
}

// core/ports.ts
// Контракт порту: належить ядру і змінюється лише за рішенням авторів ядра.
export interface TariffProvider {
  getCurrentRate(zoneId: string): Promise<EnergyRate>;
}

// core/heating-service.ts
// Бізнес-логіка: знає лише власний інтерфейс порту TariffProvider.
export class HeatingAutomationService {
  constructor(private readonly tariffProvider: TariffProvider) {}

  public async calculateHeatingPower(
    zoneId: string,
    targetTemp: number,
    currentTemp: number
  ): Promise<number> {
    const tempDelta = targetTemp - currentTemp;
    if (tempDelta <= 0) {
      return 0; // Кімната вже нагріта
    }

    const rate = await this.tariffProvider.getCurrentRate(zoneId);

    // Консервативне правило: знижувати навантаження під час пікового тарифу
    const isPeakRate = rate.pricePerKwh > 4.5;
    const basePower = tempDelta * 500; // Розрахункова потужність у ватах

    return isPeakRate ? basePower * 0.6 : basePower;
  }
}

// --- 2. ВОЛАТИЛЬНА ПЕРИФЕРІЯ (I = 1) ---

// adapters/nordpool-tariff-adapter.ts
// Адаптер: залежить від ядра та зовнішньої бібліотеки біржі.
import { TariffProvider } from "../core/ports";
import { EnergyRate } from "../core/heating-plan";

interface ExternalNordPoolPayload {
  readonly rate_cents_raw: number;
  readonly market_zone: string;
  readonly expires_epoch_sec: number;
}

export class NordPoolTariffAdapter implements TariffProvider {
  constructor(private readonly apiEndpoint: string) {}

  public async getCurrentRate(zoneId: string): Promise<EnergyRate> {
    const response = await fetch(`${this.apiEndpoint}/prices/latest?zone=${zoneId}`);
    if (!response.ok) {
      throw new Error(`Помилка запиту біржових тарифів: ${response.statusText}`);
    }

    const rawData = (await response.json()) as ExternalNordPoolPayload;

    // Трансляція нестабільних сторонніх полів у стійку структуру ядра
    return {
      pricePerKwh: rawData.rate_cents_raw / 100,
      currency: "UAH",
      validUntil: new Date(rawData.expires_epoch_sec * 1000),
    };
  }
}
