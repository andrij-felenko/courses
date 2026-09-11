// ============================================================================
// 1. СТАБІЛЬНЕ ЯДРО СИСТЕМИ (Внутрішній домен із повільним годинником)
// ============================================================================

/** Незмінне значення тарифу в термінах домену Digital Homes */
export class EnergyTariff {
  readonly centsPerKWh: number;
  readonly validFrom: Date;
  readonly validTo: Date;

  constructor(centsPerKWh: number, validFrom: Date, validTo: Date) {
    if (centsPerKWh < 0) {
      throw new Error("Тариф не може бути від'ємним у звичайному режимі споживання");
    }
    if (validFrom >= validTo) {
      throw new Error("Початок дії тарифу має передувати його завершенню");
    }
    this.centsPerKWh = centsPerKWh;
    this.validFrom = validFrom;
    this.validTo = validTo;
  }
}

/** Інтерфейс постачальника тарифів, яким володіє ядро (інверсія залежностей) */
export interface ITariffProvider {
  getCurrentTariff(zoneId: string): Promise<EnergyTariff>;
}

// ============================================================================
// 2. ЗОВНІШНІЙ МІНЛИВИЙ СВІТ (Сторонній постачальник зі швидким годинником)
// ============================================================================

/** Нестабільний зовнішній DTO, підконтрольний сторонньому постачальнику */
export interface VendorTariffPayloadDto {
  grid_zone: string;
  currency: string;
  quote_unit: string;             // Наприклад, "EUR/MWh"
  price_raw_str: string;          // Наприклад, "124.50"
  interval_start_epoch_sec: number;
  interval_end_epoch_sec: number;
  meta?: {
    schema_version: string;
    deprecated_flag?: boolean;
  };
}

// ============================================================================
// 3. ЗАПОБІЖНИЙ ШАР (ANTI-CORRUPTION LAYER): БУФЕР МІЖ ДВОМА ТЕМПАМИ
// ============================================================================

/** Транслятор: перетворює зовнішні DTO на захищені доменні сутності ядра */
export class VendorTariffTranslator {
  /**
   * Поглинає будь-які дивацтва зовнішнього контракту й гарантує
   * повернення валідного доменного об'єкта EnergyTariff.
   */
  public toDomain(dto: VendorTariffPayloadDto): EnergyTariff {
    const rawPrice = parseFloat(dto.price_raw_str);
    if (Number.isNaN(rawPrice)) {
      throw new Error(`Неможливо прочитати ціну зовнішнього провайдера: ${dto.price_raw_str}`);
    }

    // Трансляція одиниць вимірювання: з EUR/MWh у центи за кВт-год
    let centsPerKWh: number;
    if (dto.quote_unit === "EUR/MWh") {
      // 1 MWh = 1000 kWh; 1 EUR = 100 центів -> ділимо на 10
      centsPerKWh = Math.round((rawPrice / 10) * 100) / 100;
    } else if (dto.quote_unit === "cents/kWh") {
      centsPerKWh = rawPrice;
    } else {
      throw new Error(`Непідтримувана одиниця вимірювання тарифу: ${dto.quote_unit}`);
    }

    const validFrom = new Date(dto.interval_start_epoch_sec * 1000);
    const validTo = new Date(dto.interval_end_epoch_sec * 1000);

    return new EnergyTariff(centsPerKWh, validFrom, validTo);
  }
}

/** Адаптер: інкапсулює мережевий протокол, авторизацію та HTTP-запити */
export class VendorHttpAdapter {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  public async fetchRawTariff(zoneId: string): Promise<VendorTariffPayloadDto> {
    const response = await fetch(`${this.baseUrl}/v2/market/tariffs/${zoneId}/latest`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Accept": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Помилка шлюзу зовнішнього тарифу: HTTP ${response.status}`);
    }

    return (await response.json()) as VendorTariffPayloadDto;
  }
}

/** Фасад запобіжного шару: реалізує інтерфейс ядра ITariffProvider */
export class TariffAntiCorruptionLayerFacade implements ITariffProvider {
  private readonly adapter: VendorHttpAdapter;
  private readonly translator: VendorTariffTranslator;

  constructor(adapter: VendorHttpAdapter, translator: VendorTariffTranslator) {
    this.adapter = adapter;
    this.translator = translator;
  }

  public async getCurrentTariff(zoneId: string): Promise<EnergyTariff> {
    // 1. Адаптер забирає сирі дані через мережу
    const externalDto = await this.adapter.fetchRawTariff(zoneId);
    // 2. Транслятор поглинає сторонню структуру й створює чистий доменний об'єкт
    return this.translator.toDomain(externalDto);
  }
}
