class CachedMemberships implements Memberships {
  private cache = new Map<string, { role?: Role; exp: number }>();
  constructor(private readonly inner: Memberships, private readonly ttlMs = 60_000) {}

  async roleIn(userId: string, homeId: string): Promise<Role | undefined> {
    const key = `${userId}:${homeId}`;
    const hit = this.cache.get(key);
    if (hit && hit.exp > Date.now()) return hit.role;      // свіжий кеш — без стрибка
    const role = await this.inner.roleIn(userId, homeId);  // проміж — один похід у джерело
    this.cache.set(key, { role, exp: Date.now() + this.ttlMs });
    return role;
  }

  // Подія «мешканця виключено» з сервісу домогосподарств → викидаємо запис ОДРАЗУ.
  onRevoked(userId: string, homeId: string): void {
    this.cache.delete(`${userId}:${homeId}`);              // вікно застарілості на відкликанні → ~0
  }
}
