import { randomBytes } from "node:crypto";

type Rec = { userId: string; createdAt: number; lastSeen: number };

export class MemoryStore implements Store {
  private map = new Map<string, Rec>();

  constructor() {
    // без прибирання Map тече, а згаслі сесії живуть далі — тож підмітаємо
    setInterval(() => this.sweep(), 60_000).unref();
  }

  async create(userId: string): Promise<string> {
    const sid = randomBytes(18).toString("base64url");
    const now = Date.now();
    this.map.set(sid, { userId, createdAt: now, lastSeen: now });
    return sid;
  }

  async lookup(sid: string): Promise<Session | null> {
    const r = this.map.get(sid);
    if (!r) return null;
    const now = Date.now();
    if (now - r.lastSeen > IDLE_MS || now - r.createdAt > ABSOLUTE_MS) {
      this.map.delete(sid);              // згасла за простоєм АБО впала абсолютна стеля
      return null;
    }
    r.lastSeen = now;                     // ковзання: посунули дедлайн простою вперед
    return { userId: r.userId, createdAt: r.createdAt };
  }

  async rotate(sid: string): Promise<string | null> {
    const r = this.map.get(sid);
    if (!r) return null;
    const next = randomBytes(18).toString("base64url");
    this.map.set(next, { ...r, lastSeen: Date.now() });
    this.map.delete(sid);                 // старий номер мертвий тієї ж миті
    return next;
  }

  async destroy(sid: string): Promise<void> {
    this.map.delete(sid);                 // відкликання — просто викидаємо запис
  }

  private sweep(): void {
    const now = Date.now();
    for (const [sid, r] of this.map)
      if (now - r.lastSeen > IDLE_MS || now - r.createdAt > ABSOLUTE_MS)
        this.map.delete(sid);
  }
}
