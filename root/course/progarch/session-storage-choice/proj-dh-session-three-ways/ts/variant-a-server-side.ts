import { randomBytes } from "node:crypto";

interface Store {                                   // рівно те, що дає Redis
  get(k: string): Promise<string | null>;
  set(k: string, v: string, ttlSec: number): Promise<void>;
  del(k: string): Promise<void>;
}

class ServerStoreSeam implements SessionSeam {
  constructor(private store: Store) {}

  // холодний шлях: логін кладе правду в стор, клієнтові дає лише непрозорий sid
  async login(p: Principal): Promise<string> {
    const sid = randomBytes(32).toString("base64url"); // сам собою нічого не значить
    await this.store.set(`sess:${sid}`, JSON.stringify(p), 30 * 24 * 3600);
    return sid;
  }

  // гарячий шлях: правду шукаємо в сторі на КОЖЕН запит
  async validate(sid: string): Promise<Principal | null> {
    if (!sid) return null;
    const raw = await this.store.get(`sess:${sid}`);   // ← похід у Redis
    return raw ? (JSON.parse(raw) as Principal) : null; // нема запису — нема сесії
  }

  // орган відкликання: видалив рядок — сесія мертва в ту ж мить, на всіх інстансах
  async revoke(sid: string): Promise<void> {
    await this.store.del(`sess:${sid}`);
  }
}
