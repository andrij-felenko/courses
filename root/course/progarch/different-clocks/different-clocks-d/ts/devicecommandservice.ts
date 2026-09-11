import { randomUUID } from "crypto";

// ============================================================================
// 1. КОНСЕРВАТИВНЕ ТРАНЗАКЦІЙНЕ ЯДРО (ПОВІЛЬНИЙ ГОДИННИК)
// ============================================================================

/** Інтерфейс транзакційного контексту бази даних */
export interface IDbTransaction {
  query(sql: string, params: unknown[]): Promise<void>;
}

/** Сутність пристрою в ядрі */
export interface DeviceRecord {
  id: string;
  homeId: string;
  targetTemperature: number;
  updatedAt: Date;
}

/** Сервіс ядра: гарантує атомарність стану пристрою та вихідного повідомлення */
export class DeviceCommandService {
  /**
   * Змінює цільову температуру пристрою.
   * Запис бізнес-стану та запис події в Outbox відбуваються в ОДНІЙ транзакції.
   */
  public async setTargetTemperature(
    tx: IDbTransaction,
    deviceId: string,
    homeId: string,
    targetTemp: number
  ): Promise<void> {
    if (targetTemp < 5 || targetTemp > 35) {
      throw new Error("Цільова температура виходить за безпечні межі комфорту (5-35°C)");
    }

    const now = new Date();

    // 1. Оновлення нормалізованої таблиці бізнес-стану
    await tx.query(
      `UPDATE devices 
       SET target_temperature = $1, updated_at = $2 
       WHERE id = $3 AND home_id = $4`,
      [targetTemp, now, deviceId, homeId]
    );

    // 2. Формування доменної події
    const domainEvent = {
      eventId: randomUUID(),
      eventType: "DeviceTemperatureAdjusted",
      aggregateId: deviceId,
      homeId: homeId,
      occurredAt: now.toISOString(),
      payload: {
        newTargetTemperature: targetTemp,
      },
    };

    // 3. Запис у таблицю Transactional Outbox тією самою локальною транзакцією
    await tx.query(
      `INSERT INTO outbox_messages (id, aggregate_type, aggregate_id, event_type, payload, created_at, published_at)
       VALUES ($1, $2, $3, $4, $5, $6, NULL)`,
      [
        domainEvent.eventId,
        "Device",
        deviceId,
        domainEvent.eventType,
        JSON.stringify(domainEvent),
        now,
      ]
    );
  }
}

// ============================================================================
// 2. ПРОЦЕС ПЕРЕНЕСЕННЯ (OUTBOX RELAY / CDC): АСИНХРОННИЙ ТРАНСПОРТ
// ============================================================================

export interface IMessageBroker {
  publish(topic: string, routingKey: string, message: string): Promise<void>;
}

export class OutboxRelayProcessor {
  private readonly broker: IMessageBroker;

  constructor(broker: IMessageBroker) {
    this.broker = broker;
  }

  /**
   * Фонове завдання: вичитує неповідомлені рядки, публікує в брокер
   * і позначає їх опрацьованими. Ядро в цей час не блокується.
   */
  public async processBatch(
    fetchPendingBatch: () => Promise<Array<{ id: string; payload: string; aggregateId: string }>>,
    markAsPublished: (id: string, publishedAt: Date) => Promise<void>
  ): Promise<void> {
    const pendingMessages = await fetchPendingBatch();

    for (const msg of pendingMessages) {
      // Публікація в брокер повідомлень (Kafka, RabbitMQ)
      await this.broker.publish("digitalhomes.devices", msg.aggregateId, msg.payload);
      // Позначення факту публікації
      await markAsPublished(msg.id, new Date());
    }
  }
}

// ============================================================================
// 3. ШВИДКОЗМІННА ВІТРИНА ЧИТАННЯ (ШВИДКИЙ ГОДИННИК КЛІЄНТСЬКОГО СЕРВІСУ)
// ============================================================================

/** Денормалізована вітрина, готова для миттєвої віддачі на головний екран смартфона */
export interface MobileHomeDashboardProjection {
  homeId: string;
  deviceTemperatures: Record<string, number>;
  lastUpdatedLabel: string;
  comfortIndex: "ECONOMY" | "OPTIMAL" | "MAX_HEAT";
}

/** Сховище вітрини читання (наприклад, Redis або документна база) */
export interface IDashboardReadStore {
  get(homeId: string): Promise<MobileHomeDashboardProjection | null>;
  save(projection: MobileHomeDashboardProjection): Promise<void>;
}

/** Обробник подій: споживає потік подій і формує вітрину у власному темпі */
export class MobileDashboardProjectionHandler {
  private readonly readStore: IDashboardReadStore;

  constructor(readStore: IDashboardReadStore) {
    this.readStore = readStore;
  }

  public async onDeviceTemperatureAdjusted(eventJson: string): Promise<void> {
    const event = JSON.parse(eventJson);
    const { homeId, aggregateId: deviceId, payload, occurredAt } = event;

    // Читаємо наявну вітрину або створюємо порожню
    let projection = await this.readStore.get(homeId);
    if (!projection) {
      projection = {
        homeId: homeId,
        deviceTemperatures: {},
        lastUpdatedLabel: "",
        comfortIndex: "OPTIMAL",
      };
    }

    // Оновлюємо готову денормалізовану модель без жодних запитів до ядра
    projection.deviceTemperatures[deviceId] = payload.newTargetTemperature;
    projection.lastUpdatedLabel = new Date(occurredAt).toLocaleTimeString("uk-UA");

    // Швидка підсистема може експериментувати з формулами індексу комфорту щодня
    const temp = payload.newTargetTemperature;
    projection.comfortIndex = temp > 24 ? "MAX_HEAT" : temp < 19 ? "ECONOMY" : "OPTIMAL";

    await this.readStore.save(projection);
  }
}
