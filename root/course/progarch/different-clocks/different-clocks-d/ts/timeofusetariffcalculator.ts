/**
 * Результат розрахунку енергоспоживання для клієнтів старого покоління.
 */
interface LegacyEnergyBill {
  readonly homeId: string;
  readonly billingPeriod: string;
  readonly totalKwh: number;
  readonly totalCostEur: number;
}

/**
 * Деталізований розрахунок енергоспоживання за зонами доби (новий контракт).
 */
interface DynamicEnergyBill {
  readonly homeId: string;
  readonly billingPeriod: string;
  readonly zoneBreakdown: {
    readonly peakKwh: number;
    readonly peakCostEur: number;
    readonly offPeakKwh: number;
    readonly offPeakCostEur: number;
    readonly solarExportKwh: number;
    readonly solarCreditEur: number;
  };
  readonly totalCostEur: number;
  readonly peakPowerExceeded: boolean;
}

/**
 * Вхідні показники для тарифного ядра.
 */
interface MeterHourlyReadings {
  readonly homeId: string;
  readonly period: string;
  readonly hourlyPeakKwh: number[];
  readonly hourlyOffPeakKwh: number[];
  readonly hourlySolarExportKwh: number[];
}

/**
 * Абстракція калькулятора для техніки Branch by Abstraction.
 * Дозволяє паралельно розвивати обидва рушії в єдиному стовбурі коду.
 */
interface TariffCalculator {
  calculate(readings: MeterHourlyReadings): DynamicEnergyBill;
}

/**
 * Новий рушій ядра: багатозонний облік із компенсацією сонячної генерації.
 */
class TimeOfUseTariffCalculator implements TariffCalculator {
  private readonly peakRate = 0.32; // Євро за кВт·год у години пік
  private readonly offPeakRate = 0.14; // Євро за кВт·год у нічні години
  private readonly solarFeedInCredit = 0.08; // Компенсація за генерацію в мережу

  calculate(readings: MeterHourlyReadings): DynamicEnergyBill {
    const peakKwh = readings.hourlyPeakKwh.reduce((sum, val) => sum + val, 0);
    const offPeakKwh = readings.hourlyOffPeakKwh.reduce((sum, val) => sum + val, 0);
    const solarExportKwh = readings.hourlySolarExportKwh.reduce((sum, val) => sum + val, 0);

    const peakCost = peakKwh * this.peakRate;
    const offPeakCost = offPeakKwh * this.offPeakRate;
    const solarCredit = solarExportKwh * this.solarFeedInCredit;

    const totalCost = Math.max(0, peakCost + offPeakCost - solarCredit);

    return {
      homeId: readings.homeId,
      billingPeriod: readings.period,
      zoneBreakdown: {
        peakKwh,
        peakCostEur: Math.round(peakCost * 100) / 100,
        offPeakKwh,
        offPeakCostEur: Math.round(offPeakCost * 100) / 100,
        solarExportKwh,
        solarCreditEur: Math.round(solarCredit * 100) / 100,
      },
      totalCostEur: Math.round(totalCost * 100) / 100,
      peakPowerExceeded: readings.hourlyPeakKwh.some((val) => val > 7.5),
    };
  }
}

/**
 * Застарілий рушій ядра: фіксована ставка без зон доби.
 */
class FlatRateTariffCalculator implements TariffCalculator {
  private readonly flatRate = 0.22;

  calculate(readings: MeterHourlyReadings): DynamicEnergyBill {
    const totalKwh =
      readings.hourlyPeakKwh.reduce((sum, val) => sum + val, 0) +
      readings.hourlyOffPeakKwh.reduce((sum, val) => sum + val, 0);

    const totalCost = totalKwh * this.flatRate;

    return {
      homeId: readings.homeId,
      billingPeriod: readings.period,
      zoneBreakdown: {
        peakKwh: totalKwh,
        peakCostEur: Math.round(totalCost * 100) / 100,
        offPeakKwh: 0,
        offPeakCostEur: 0,
        solarExportKwh: 0,
        solarCreditEur: 0,
      },
      totalCostEur: Math.round(totalCost * 100) / 100,
      peakPowerExceeded: false,
    };
  }
}

/**
 * Перехідний фасад ядра за патерном Expand and Contract.
 * Одночасно обслуговує швидкі клієнти та застарілих споживачів.
 */
class EnergyBillingFacade {
  constructor(
    private readonly currentEngine: TariffCalculator,
    private readonly isDynamicBillingEnabled: (homeId: string) => boolean
  ) {}

  /**
   * Застарілий контракт для зовнішніх систем комунального обліку та старих панелей.
   * Переводить новий стан на плоску форму попереднього покоління.
   * @deprecated Підлягає видаленню у фазі Contract після переходу всіх провайдерів.
   */
  calculateLegacySummary(readings: MeterHourlyReadings): LegacyEnergyBill {
    const bill = this.resolveEngine(readings.homeId).calculate(readings);
    const totalKwh = bill.zoneBreakdown.peakKwh + bill.zoneBreakdown.offPeakKwh;

    return {
      homeId: bill.homeId,
      billingPeriod: bill.billingPeriod,
      totalKwh,
      totalCostEur: bill.totalCostEur,
    };
  }

  /**
   * Новий розширений контракт для швидких клієнтів (мобільні віджети, розумні розетки).
   */
  calculateDetailedBilling(readings: MeterHourlyReadings): DynamicEnergyBill {
    return this.resolveEngine(readings.homeId).calculate(readings);
  }

  /**
   * Маршрутизатор техніки Branch by Abstraction: дозволяє перемикати
   * конкретні квартири на новий математичний рушій без випуску нового бінарника ядра.
   */
  private resolveEngine(homeId: string): TariffCalculator {
    return this.isDynamicBillingEnabled(homeId)
      ? this.currentEngine
      : new FlatRateTariffCalculator();
  }
}
