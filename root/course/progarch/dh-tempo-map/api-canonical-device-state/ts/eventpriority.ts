// Класифікація важливості події для регулювання зворотного тиску
export type EventPriority = 'TELEMETRY' | 'SAFETY_CRITICAL';

// Типізована подія зміни стану пристрою
export interface DeviceStateChangedEvent {
  // Унікальний ідентифікатор події
  eventId: string;
  // Ідентифікатор пристрою
  deviceId: string;
  // Назва риси, що зазнала змін
  capability: string;
  // Попереднє підтверджене значення
  previousValue: unknown;
  // Нове актуальне значення
  currentValue: unknown;
  // Пріоритет обробки в буфері зворотного тиску
  priority: EventPriority;
  // Часова мітка генерації події на шлюзі
  timestamp: string;
}

// Конфігурація підписки з параметрами згладжування
export interface SubscriptionFilter {
  deviceIds?: string[];
  capabilities?: string[];
  // Мінімальний інтервал між оновленнями числової телеметрії (мс)
  telemetryThrottleMs?: number;
}

// Диспетчер реактивної черги з механізмом conflation
export class ConflatingEventStream {
  // Буфер неперервної телеметрії: ключ deviceId:capability -> остання подія
  private readonly telemetryConflationBuffer: Map<string, DeviceStateChangedEvent> = new Map();
  // Пріоритетна непорушна черга критичних захисних сповіщень
  private readonly criticalEventQueue: DeviceStateChangedEvent[] = [];

  // Додавання нової події до реактивного потоку
  public pushEvent(event: DeviceStateChangedEvent): void {
    if (event.priority === 'SAFETY_CRITICAL') {
      // Критичні події завжди зберігаються у черзі FIFO без втрат
      this.criticalEventQueue.push(event);
    } else {
      // Числова телеметрія схлопується за складеним ключем
      const conflationKey = event.deviceId + ':' + event.capability;
      this.telemetryConflationBuffer.set(conflationKey, event);
    }
  }

  // Вичитування накопиченої порції даних повільним клієнтом
  public pollBatch(maxItems: number): DeviceStateChangedEvent[] {
    const result: DeviceStateChangedEvent[] = [];

    // 1. Спершу вичерпуємо критичні аварійні події
    while (this.criticalEventQueue.length > 0 && result.length < maxItems) {
      const criticalEvent = this.criticalEventQueue.shift();
      if (criticalEvent) {
        result.push(criticalEvent);
      }
    }

    // 2. Якщо ліміт порції не вичерпано, додаємо злиту телеметрію
    if (result.length < maxItems) {
      for (const [key, event] of this.telemetryConflationBuffer.entries()) {
        result.push(event);
        this.telemetryConflationBuffer.delete(key);
        if (result.length >= maxItems) {
          break;
        }
      }
    }

    return result;
  }
}
