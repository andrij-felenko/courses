// Абстрактний порт (Нейтральний до вендора)
export interface TelemetryRepository {
  save(reading: SensorReading): Promise<void>;
  getByHome(homeId: string): Promise<SensorReading[]>;
}

// Адаптер #1 (AWS DynamoDB Implementation)
export class DynamoDBTelemetryAdapter implements TelemetryRepository {
  constructor(private client: DynamoDBClient) {}
  async save(reading: SensorReading): Promise<void> { /* AWS specific logic */ }
  async getByHome(homeId: string): Promise<SensorReading[]> { /* AWS specific query */ }
}

// Адаптер #2 (PostgreSQL Implementation — Створений для евакуації)
export class PostgresTelemetryAdapter implements TelemetryRepository {
  constructor(private pool: PgPool) {}
  async save(reading: SensorReading): Promise<void> { /* SQL INSERT */ }
  async getByHome(homeId: string): Promise<SensorReading[]> { /* SQL SELECT */ }
}
