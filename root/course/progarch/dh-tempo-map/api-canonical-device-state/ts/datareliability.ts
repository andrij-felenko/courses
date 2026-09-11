// Статус достовірності кешованих даних
export type DataReliability = 'FRESH' | 'STALE' | 'UNREACHABLE';

// Метадані свіжості фізичного стану пристрою
export interface StateFreshnessMetadata {
  // Часова мітка отримання останнього підтвердженого пакета з радіоефіру
  lastUpdatedTimestamp: string;
  // Чи присутній пристрій на радіошині
  isReachable: boolean;
  // Якість та актуальність даних для клієнта
  reliability: DataReliability;
  // Рівень сигналу радіозв'язку (RSSI в дБм або Link Quality Index)
  linkQuality: number;
}

// Повна відповідь на запит стану окремого пристрою
export interface DeviceStateResult {
  deviceId: string;
  schemaVersion: number;
  metadata: StateFreshnessMetadata;
  // Словник чинних значень можливостей пристрою
  capabilities: Record<string, unknown>;
}

// Запит на читання стану одного пристрою
export interface GetDeviceStateRequest {
  deviceId: string;
}

// Запит на пакетне читання стану групи пристроїв
export interface BatchGetDeviceStatesRequest {
  deviceIds: string[];
}

// Результат пакетного читання
export interface BatchDeviceStateResult {
  // Знімки успішно прочитаних пристроїв
  devices: Record<string, DeviceStateResult>;
  // Список ідентифікаторів пристроїв, які не зареєстровані на шлюзі
  notFoundDeviceIds: string[];
  // Часова мітка генерації пакета відповідей
  snapshotTimestamp: string;
}

// Інтерфейс канонічного сховища стану на стороні шлюзу
export interface CanonicalStateStore {
  getDeviceState(request: GetDeviceStateRequest): DeviceStateResult | null;
  batchGetDeviceStates(request: BatchGetDeviceStatesRequest): BatchDeviceStateResult;
}

// Реалізація читання виключно з оперативної пам'яті шлюзу
export class InMemoryCanonicalStateStore implements CanonicalStateStore {
  private readonly stateCache: Map<string, DeviceStateResult> = new Map();

  public getDeviceState(request: GetDeviceStateRequest): DeviceStateResult | null {
    const cached = this.stateCache.get(request.deviceId);
    if (!cached) {
      return null;
    }
    // Повернення клону знімка гарантує незмінність кешу від мутацій споживачами
    return { ...cached };
  }

  public batchGetDeviceStates(request: BatchGetDeviceStatesRequest): BatchDeviceStateResult {
    const devices: Record<string, DeviceStateResult> = {};
    const notFound: string[] = [];

    for (const id of request.deviceIds) {
      const state = this.stateCache.get(id);
      if (state) {
        devices[id] = { ...state };
      } else {
        notFound.push(id);
      }
    }

    return {
      devices: devices,
      notFoundDeviceIds: notFound,
      snapshotTimestamp: new Date().toISOString(),
    };
  }

  // Метод внутрішнього оновлення кешу драйверами апаратних радіошин
  public updateDeviceState(deviceId: string, snapshot: DeviceStateResult): void {
    this.stateCache.set(deviceId, snapshot);
  }
}
