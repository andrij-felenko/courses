// UserRepository.ts — Подвійне читання з відкатом на TypeScript
export interface KeyValueStore {
  get(key: string): Promise<string | null>;
}

export interface Telemetry {
  recordPrimaryHit(): void;
  recordFallbackHit(): void;
}

export class UserRepository {
  constructor(
    private readonly store: KeyValueStore,
    private readonly telemetry: Telemetry
  ) {}

  async fetchUser(tenantId: string, userId: string): Promise<string> {
    // 1. Пріоритетне читання з нового багатоорендного сховища (v2)
    const v2Key = `tenant:${tenantId}:user:${userId}`;
    const v2Data = await this.store.get(v2Key);
    if (v2Data !== null) {
      this.telemetry.recordPrimaryHit();
      return v2Data;
    }

    // 2. Резервне читання зі старого формату (якщо бекфіл ще не завершився)
    const v1Key = `user:${userId}`;
    const v1Data = await this.store.get(v1Key);
    if (v1Data !== null) {
      this.telemetry.recordFallbackHit();
      return v1Data;
    }

    throw new Error(`User not found: ${userId} in tenant ${tenantId}`);
  }
}
