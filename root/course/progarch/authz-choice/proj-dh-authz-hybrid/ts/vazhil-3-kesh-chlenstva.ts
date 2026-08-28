interface RelationshipStore {                            // центр зв'язків: мережевий виклик
  isMemberOf(userId: string, homeId: string): Promise<boolean>;
}

type Entry = { member: boolean; exp: number };

class RelationshipCache {
  private cache = new Map<string, Entry>();

  constructor(
    private store: RelationshipStore,
    private now: () => number = Date.now,
    private posTtlMs = 60_000,   // позитив живе довше — членство змінюється рідко
    private negTtlMs = 5_000,    // негатив — коротко, щоб свіжий член не застряг у «ні»
  ) {}

  async isMemberOf(userId: string, homeId: string): Promise<boolean> {
    const key = `${userId}:${homeId}`;
    const hit = this.cache.get(key);
    if (hit && hit.exp > this.now()) return hit.member;    // свіжий кеш — жодного стрибка

    let member: boolean;
    try {
      member = await this.store.isMemberOf(userId, homeId); // один похід у центр
    } catch {
      // FAIL-CLOSED: не підтвердили членство → «ні». Збій НЕ кешуємо — щоб не залипнути в deny.
      return false;
    }
    const ttl = member ? this.posTtlMs : this.negTtlMs;
    this.cache.set(key, { member, exp: this.now() + ttl });
    return member;
  }

  // Push-інвалідація: подія «виключено» з центру зв'язків викидає запис ОДРАЗУ.
  onRevoked(userId: string, homeId: string): void {
    this.cache.delete(`${userId}:${homeId}`);              // вікно застарілості на відкликанні → ≈0
  }
}
