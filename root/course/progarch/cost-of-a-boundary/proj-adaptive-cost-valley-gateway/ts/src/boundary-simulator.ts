import type { EntityId, ItemRecord, BoundaryConfig } from './types.ts';

/**
 * Симулятор віддаленого сервісу та вартості перетину системної межі.
 * Моделює фіксовані накладні витрати виклику (baseLatencyMs)
 * та лінійний штраф за обсяг переданих серіалізованих даних (perByteLatencyMs).
 */
export class BoundarySimulator {
  private readonly config: BoundaryConfig;
  private readonly repository: Map<EntityId, ItemRecord> = new Map();

  constructor(config: BoundaryConfig) {
    this.config = config;
    this.seedSampleData();
  }

  /**
   * Пакетне вилучення сутностей через дорогу системну межу.
   * Підтримує фільтрацію за маскою полів на стороні сервісу (Sparse Fieldsets),
   * що дозволяє мінімізувати розмір переданого корисного навантаження.
   */
  public async fetchBatch(
    ids: EntityId[],
    fields?: Set<string>
  ): Promise<{ data: Map<EntityId, ItemRecord>; payloadBytes: number; latencyMs: number }> {
    const resultMap = new Map<EntityId, ItemRecord>();

    for (const id of ids) {
      const rawEntity = this.repository.get(id);
      if (!rawEntity) {
        continue;
      }

      // Якщо маска полів задана, повертаємо тільки запитані поля (плюс id)
      if (fields && fields.size > 0) {
        const filtered: ItemRecord = { id: rawEntity.id };
        for (const field of fields) {
          if (field in rawEntity) {
            filtered[field] = rawEntity[field];
          }
        }
        resultMap.set(id, filtered);
      } else {
        // Повне тіло сутності (надвибірка)
        resultMap.set(id, { ...rawEntity });
      }
    }

    // Обчислюємо розмір серіалізованого корисного навантаження
    const serialized = JSON.stringify(Array.from(resultMap.values()));
    const payloadBytes = Buffer.byteLength(serialized, 'utf8');

    // Розрахунок затримки: фіксована база межі + штраф за байти
    const calculatedLatency = this.config.baseLatencyMs + payloadBytes * this.config.perByteLatencyMs;
    const latencyMs = Math.max(1, Math.round(calculatedLatency));

    // Імітація асинхронного мережевого чи міжпроцесного переходу
    await this.sleep(latencyMs);

    return {
      data: resultMap,
      payloadBytes,
      latencyMs
    };
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private seedSampleData(): void {
    // Наповнюємо сховище репрезентативними записами сутностей із різними полями
    for (let i = 1; i <= 200; i++) {
      this.repository.set(i, {
        id: i,
        name: `Користувач #${i}`,
        email: `user${i}@enterprise-boundary.internal`,
        role: i % 5 === 0 ? 'Admin' : 'Operator',
        department: `Підрозділ-${(i % 10) + 1}`,
        status: i % 7 === 0 ? 'Suspended' : 'Active',
        lastLoginAt: new Date(Date.now() - i * 3600000).toISOString(),
        permissions: ['READ_METRICS', 'EXECUTE_BATCH', 'OVERRIDE_WINDOW'],
        preferences: {
          theme: 'dark',
          locale: 'uk-UA',
          notifications: { email: true, sms: false, webhook: true }
        },
        metadata: {
          region: 'eu-central-1',
          clusterId: `node-${(i % 4) + 1}`,
          complianceVersion: 'v2.4.1'
        }
      });
    }
  }
}
