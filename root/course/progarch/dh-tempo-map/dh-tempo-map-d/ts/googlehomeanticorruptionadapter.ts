import { CanonicalCommand } from './tempo-buffer-bus';

// Зовнішня схема Google Smart Home (мінлива, контролюється сторонньою компанією)
export interface GoogleSmartHomePayload {
  readonly requestId: string;
  readonly inputs: Array<{
    readonly intent: string;
    readonly payload: {
      readonly commands: Array<{
        readonly devices: Array<{ readonly id: string }>;
        readonly execution: Array<{
          readonly command: string;
          readonly params: Record<string, unknown>;
        }>;
      }>;
    };
  }>;
}

// Канонічний інтерфейс передачі команди в буфер темпів
export interface CommandBufferSink {
  enqueueCommand(command: CanonicalCommand): { accepted: boolean; reason?: string };
}

// 1. Адаптер Google Smart Home
export class GoogleHomeAntiCorruptionAdapter {
  constructor(private readonly bufferSink: CommandBufferSink) {}

  public handleExternalWebhook(rawPayload: GoogleSmartHomePayload): { status: string; correlationId: string } {
    for (const input of rawPayload.inputs) {
      if (input.intent !== 'action.devices.EXECUTE') {
        continue;
      }

      for (const commandGroup of input.payload.commands) {
        for (const device of commandGroup.devices) {
          for (const execution of commandGroup.execution) {
            const canonical = this.translateToCanonical(device.id, execution.command, execution.params);
            if (canonical) {
              this.bufferSink.enqueueCommand(canonical);
            }
          }
        }
      }
    }

    return { status: 'SUCCESS', correlationId: rawPayload.requestId };
  }

  // Поглинання стороннього діалекту та переведення в канонічні SI-одиниці ядра
  private translateToCanonical(
    externalDeviceId: string,
    commandName: string,
    params: Record<string, unknown>
  ): CanonicalCommand | null {
    const timestamp = Date.now();

    switch (commandName) {
      case 'action.devices.commands.OnOff': {
        const onValue = Boolean(params['on']);
        return {
          commandId: `gh-${timestamp}-${Math.random().toString(36).slice(2, 7)}`,
          deviceId: externalDeviceId,
          capability: 'power',
          targetValue: onValue,
          priority: 'normal',
          createdAt: timestamp,
        };
      }

      case 'action.devices.commands.BrightnessAbsolute': {
        // Google передає відсотки 0..100, канонічне ядро працює в діапазоні 0.0..1.0
        const rawBrightness = Number(params['brightness']);
        if (Number.isNaN(rawBrightness) || rawBrightness < 0 || rawBrightness > 100) {
          return null; // Відкидання невалідних даних на межі системи
        }

        return {
          commandId: `gh-${timestamp}-${Math.random().toString(36).slice(2, 7)}`,
          deviceId: externalDeviceId,
          capability: 'brightness',
          targetValue: rawBrightness / 100.0,
          priority: 'normal',
          createdAt: timestamp,
        };
      }

      default:
        // Невідомі команди сторонньої системи ігноруються без збою ядра
        return null;
    }
  }
}

// 2. Адаптер зовнішніх динамічних тарифів на електроенергію (Nord Pool / ENTSO-E)
export interface ExternalTariffFeedItem {
  readonly timestamp_utc: string;
  readonly price_eur_per_mwh: number;
  readonly currency: string;
}

export interface CanonicalTariffUpdate {
  readonly validFromEpochMs: number;
  readonly priceCentsPerKWh: number;
  readonly tariffZone: 'peak' | 'standard' | 'economy';
}

export class DynamicTariffAntiCorruptionAdapter {
  constructor(private readonly onCanonicalTariff: (tariff: CanonicalTariffUpdate) => void) {}

  // Трансляція нестабільного зовнішнього формату в канонічну подію ядра
  public ingestExternalFeed(feed: ExternalTariffFeedItem[]): void {
    for (const item of feed) {
      const epochMs = Date.parse(item.timestamp_utc);
      if (Number.isNaN(epochMs)) {
        continue; // Помилка формату дати залишається в адаптері й не торкається ядра
      }

      // Переведення EUR/MWh у канонічні центи за кВт·год
      const centsPerKWh = (item.price_eur_per_mwh * 100) / 1000;

      // Класифікація за доменною логікою Digital Homes
      let zone: 'peak' | 'standard' | 'economy' = 'standard';
      if (centsPerKWh > 25.0) {
        zone = 'peak';
      } else if (centsPerKWh < 8.0) {
        zone = 'economy';
      }

      this.onCanonicalTariff({
        validFromEpochMs: epochMs,
        priceCentsPerKWh: Math.round(centsPerKWh * 100) / 100,
        tariffZone: zone,
      });
    }
  }
}
