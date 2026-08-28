type Entry = { allow: boolean; home: string; exp: number };

// Кеш САДИТЬСЯ над мережею. Свіжість тут ЧЕСНА: короткий позитив, ще коротший негатив,
// і подія відкликання, що б'є точково — не чекаючи жодного TTL.
class VerdictCache implements PdpClient {
  private byKey  = new Map<string, Entry>();        // (subject|action|resource) → вердикт
  private byHome = new Map<string, Set<string>>();  // home → ключі, що на нього спираються
  constructor(
    private readonly inner: PdpClient,
    private readonly posTtlMs = 30_000, // «дозволено» живе недовго
    private readonly negTtlMs = 3_000,  // «відмовлено» — ще коротше: свіжий член не має застрягти в «ні»
  ) {}

  async check(req: DecisionRequest): Promise<DecisionResponse> {
    const key = `${req.subject}|${req.action}|${req.resource}`;
    const hit = this.byKey.get(key);
    if (hit && hit.exp > Date.now()) return { allow: hit.allow, reason: "cache", home: hit.home };

    const v = await this.inner.check(req);           // проміж — один похід у центр (кине → НЕ кешуємо)
    const home = v.home ?? "";                       // тегуємо АВТОРИТЕТНИМ домом із вердикту, не з context
    const ttl  = v.allow ? this.posTtlMs : this.negTtlMs;
    this.byKey.set(key, { allow: v.allow, home, exp: Date.now() + ttl });
    if (home) {
      let set = this.byHome.get(home);
      if (!set) this.byHome.set(home, (set = new Set()));
      set.add(key);                                  // індекс home → ключі, щоб уміти чистити ЗА ДОМОМ
    }
    return v;
  }

  // Подія «суб'єкта виключено з дому» → викидаємо ВСІ його вердикти, що спиралися на цей дім.
  onRevoked(subject: string, home: string): void {
    const keys = this.byHome.get(home);
    if (!keys) return;
    for (const key of keys) {
      if (key.startsWith(`${subject}|`)) { this.byKey.delete(key); keys.delete(key); }
    }
  }
}
