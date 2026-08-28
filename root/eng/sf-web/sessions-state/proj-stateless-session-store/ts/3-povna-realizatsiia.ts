import { randomBytes } from "node:crypto";
import Redis from "ioredis";

export interface SessionData {
  userId?: string;
  role?: string;
  [key: string]: unknown;
}

export interface SessionEnvelope {
  id: string;
  version: number;
  schemaVersion: number;
  createdAt: number;
  updatedAt: number;
  lastTouch: number;
  data: SessionData;
}

export interface StoreOptions {
  ttlSeconds?: number;
  touchThresholdRatio?: number; // частка TTL для поновлення (за замовчуванням 0.2 = 20%)
  prefix?: string;
  schemaVersion?: number;
}

const CAS_UPDATE_LUA = `
local raw = redis.call('GET', KEYS[1])
if not raw then
  return {0, 'NOT_FOUND'}
end

local current = cjson.decode(raw)
local expected_version = tonumber(ARGV[1])

if current.version ~= expected_version then
  return {0, 'VERSION_CONFLICT', tostring(current.version)}
end

redis.call('SET', KEYS[1], ARGV[2], 'EX', tonumber(ARGV[3]))
return {1, 'OK'}
`;

const THROTTLED_TOUCH_LUA = `
local raw = redis.call('GET', KEYS[1])
if not raw then
  return 0
end

local doc = cjson.decode(raw)
local now = tonumber(ARGV[1])
local threshold = tonumber(ARGV[2])

if (now - doc.lastTouch) >= threshold then
  doc.lastTouch = now
  local updated_json = cjson.encode(doc)
  redis.call('SET', KEYS[1], updated_json, 'EX', tonumber(ARGV[3]))
  return 1
end

return 2
`;

export class StatelessRedisSessionStore {
  private redis: Redis;
  private ttlSeconds: number;
  private touchThresholdMs: number;
  private prefix: string;
  private currentSchemaVersion: number;

  constructor(redisClient: Redis, options: StoreOptions = {}) {
    this.redis = redisClient;
    this.ttlSeconds = options.ttlSeconds ?? 1800; // 30 хвилин
    const ratio = options.touchThresholdRatio ?? 0.2; // 20% від TTL (6 хвилин)
    this.touchThresholdMs = this.ttlSeconds * 1000 * ratio;
    this.prefix = options.prefix ?? "sess:";
    this.currentSchemaVersion = options.schemaVersion ?? 1;
  }

  private key(id: string): string {
    return `${this.prefix}${id}`;
  }

  private userSessionsKey(userId: string): string {
    return `${this.prefix}user:${userId}`;
  }

  /**
   * Генерація криптографічно безпечного ідентифікатора сесії (128 біт ентропії).
   */
  public generateSessionId(): string {
    return randomBytes(16).toString("hex");
  }

  /**
   * Створення нової сесії з прив'язкою до користувача (за наявності userId).
   */
  public async create(initialData: SessionData = {}): Promise<SessionEnvelope> {
    const id = this.generateSessionId();
    const now = Date.now();
    const envelope: SessionEnvelope = {
      id,
      version: 1,
      schemaVersion: this.currentSchemaVersion,
      createdAt: now,
      updatedAt: now,
      lastTouch: now,
      data: initialData,
    };

    const payload = JSON.stringify(envelope);
    const pipeline = this.redis.pipeline();
    pipeline.set(this.key(id), payload, "EX", this.ttlSeconds);

    if (initialData.userId) {
      const userKey = this.userSessionsKey(initialData.userId);
      pipeline.sadd(userKey, id);
      pipeline.expire(userKey, this.ttlSeconds * 2);
    }

    await pipeline.exec();
    return envelope;
  }

  /**
   * Отримання сесії з автоматичним дросельованим поновленням TTL.
   */
  public async get(id: string): Promise<SessionEnvelope | null> {
    const raw = await this.redis.get(this.key(id));
    if (!raw) return null;

    try {
      let envelope: SessionEnvelope = JSON.parse(raw);
      
      // Лінива міграція застарілих версій схеми даних
      if (envelope.schemaVersion < this.currentSchemaVersion) {
        envelope = this.migrateSchema(envelope);
      }

      // Фоновий асинхронний виклик поновлення без затримки основного потоку
      this.touchThrottled(id).catch(() => {
        // Логування помилки без порушення поточної відповіді
      });

      return envelope;
    } catch {
      // Пошкоджені дані сесії — захисне очищення невалідного ключа
      await this.destroy(id);
      return null;
    }
  }

  /**
   * Атомарне оновлення сесії з перевіркою версії (CAS).
   */
  public async update(
    id: string,
    expectedVersion: number,
    mutator: (current: SessionData) => SessionData
  ): Promise<SessionEnvelope> {
    const key = this.key(id);
    const raw = await this.redis.get(key);
    if (!raw) {
      throw new Error(`SESSION_NOT_FOUND: session ${id} does not exist`);
    }

    const currentEnvelope: SessionEnvelope = JSON.parse(raw);
    const nextData = mutator({ ...currentEnvelope.data });
    const now = Date.now();

    const nextEnvelope: SessionEnvelope = {
      id,
      version: expectedVersion + 1,
      schemaVersion: this.currentSchemaVersion,
      createdAt: currentEnvelope.createdAt,
      updatedAt: now,
      lastTouch: now,
      data: nextData,
    };

    const result = (await this.redis.eval(
      CAS_UPDATE_LUA,
      1,
      key,
      expectedVersion.toString(),
      JSON.stringify(nextEnvelope),
      this.ttlSeconds.toString()
    )) as [number, string, string?];

    const [status, code, actualVersion] = result;

    if (status === 0) {
      if (code === "VERSION_CONFLICT") {
        const err = new Error(`VERSION_CONFLICT: expected ${expectedVersion}, got ${actualVersion}`);
        err.name = "VersionConflictError";
        throw err;
      }
      throw new Error(`SESSION_UPDATE_FAILED: ${code}`);
    }

    return nextEnvelope;
  }

  /**
   * Ротація ідентифікатора сесії (наприклад, після входу або підвищення прав).
   */
  public async rotate(oldId: string): Promise<SessionEnvelope> {
    const oldEnvelope = await this.get(oldId);
    if (!oldEnvelope) {
      throw new Error(`SESSION_NOT_FOUND: cannot rotate non-existent session ${oldId}`);
    }

    const newId = this.generateSessionId();
    const now = Date.now();
    const newEnvelope: SessionEnvelope = {
      id: newId,
      version: oldEnvelope.version + 1,
      schemaVersion: this.currentSchemaVersion,
      createdAt: oldEnvelope.createdAt,
      updatedAt: now,
      lastTouch: now,
      data: oldEnvelope.data,
    };

    const pipeline = this.redis.pipeline();
    pipeline.set(this.key(newId), JSON.stringify(newEnvelope), "EX", this.ttlSeconds);
    pipeline.del(this.key(oldId));

    if (oldEnvelope.data.userId) {
      const userKey = this.userSessionsKey(oldEnvelope.data.userId);
      pipeline.srem(userKey, oldId);
      pipeline.sadd(userKey, newId);
    }

    await pipeline.exec();
    return newEnvelope;
  }

  /**
   * Знищення однієї сесії (вихід на поточному пристрої).
   */
  public async destroy(id: string): Promise<boolean> {
    const envelope = await this.get(id);
    const pipeline = this.redis.pipeline();
    pipeline.del(this.key(id));

    if (envelope?.data.userId) {
      pipeline.srem(this.userSessionsKey(envelope.data.userId), id);
    }

    const results = await pipeline.exec();
    return (results?.[0]?.[1] as number) > 0;
  }

  /**
   * Глобальне завершення всіх сесій користувача (наприклад, при зміні пароля).
   */
  public async destroyAllForUser(userId: string): Promise<number> {
    const userKey = this.userSessionsKey(userId);
    const sessionIds = await this.redis.smembers(userKey);
    if (!sessionIds.length) return 0;

    const pipeline = this.redis.pipeline();
    for (const sid of sessionIds) {
      pipeline.del(this.key(sid));
    }
    pipeline.del(userKey);
    await pipeline.exec();

    return sessionIds.length;
  }

  private async touchThrottled(id: string): Promise<void> {
    const now = Date.now();
    await this.redis.eval(
      THROTTLED_TOUCH_LUA,
      1,
      this.key(id),
      now.toString(),
      this.touchThresholdMs.toString(),
      this.ttlSeconds.toString()
    );
  }

  private migrateSchema(envelope: SessionEnvelope): SessionEnvelope {
    const migratedData = { ...envelope.data };
    envelope.schemaVersion = this.currentSchemaVersion;
    envelope.data = migratedData;
    return envelope;
  }
}
