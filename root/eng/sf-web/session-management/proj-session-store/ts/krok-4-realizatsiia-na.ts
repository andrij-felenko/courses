import { randomBytes } from "node:crypto";
import type Redis from "ioredis";

const KEY = (sid: string) => `sess:${sid}`;
const IDLE_S = 30 * 60;
const ABSOLUTE_S = 12 * 3600;

export class RedisStore implements Store {
  constructor(private redis: Redis) {}

  async create(userId: string): Promise<string> {
    const sid = randomBytes(18).toString("base64url");
    const value = JSON.stringify({ userId, createdAt: Date.now() });
    // NX — на випадок (астрономічно рідкої) колізії; EX — idle-TTL одразу на ключі
    await this.redis.set(KEY(sid), value, "EX", IDLE_S, "NX");
    return sid;
  }

  async lookup(sid: string): Promise<Session | null> {
    const raw = await this.redis.get(KEY(sid));
    if (!raw) return null;                       // ключа немає — Redis уже згасив за idle
    const s: Session = JSON.parse(raw);
    const absLeft = s.createdAt / 1000 + ABSOLUTE_S - Date.now() / 1000;
    if (absLeft <= 0) {                          // впала абсолютна стеля
      await this.redis.del(KEY(sid));
      return null;
    }
    // ковзання, ОБМЕЖЕНЕ абсолютом: idle ніколи не проб'є стелю
    await this.redis.expire(KEY(sid), Math.floor(Math.min(IDLE_S, absLeft)));
    return s;
  }

  async rotate(sid: string): Promise<string | null> {
    const next = randomBytes(18).toString("base64url");
    // атомарно одним скриптом: прочитати, покласти під новим ключем, знищити старий
    const ok = await this.redis.eval(ROTATE_LUA, 2, KEY(sid), KEY(next), String(IDLE_S));
    return ok ? next : null;
  }

  async destroy(sid: string): Promise<void> {
    await this.redis.del(KEY(sid));              // відкликання — один DEL
  }
}

// KEYS[1] старий ключ, KEYS[2] новий, ARGV[1] idle-TTL
const ROTATE_LUA = `
  local v = redis.call('GET', KEYS[1])
  if not v then return nil end
  redis.call('SET', KEYS[2], v, 'EX', ARGV[1])
  redis.call('DEL', KEYS[1])
  return 1`;
