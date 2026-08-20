# ⚙️ Сховище бездержавних сесій: зовнішній Redis-провайдер із захистом від гонок версій

У монолітному веб-застосунку на одному фізичному сервері збереження стану користувача в локальній оперативній пам'яті здається природним і швидким, але горизонтальне масштабування вимагає перетворення всього обчислювального шару на пул повністю взаємозамінних бездержавних вузлів. Щоб будь-який сервер у кластері міг безперешкодно обробити довільний запит від будь-якого клієнта, сесійні дані виносяться у виділене спільне оперативне сховище (кластер Redis).

Проте наївний підхід до зовнішнього сховища — звичайне зчитування `GET sess:<id>` на початку запиту та неконтрольований запис `SET sess:<id>` наприкінці — створює критичну системну вразливість: **аномалію втраченого оновлення** (*Lost Update*).

Уявіть типовий життєвий сценарій: користувач відкриває інтернет-магазин у двох сусідніх вкладках браузера.
1. Вкладка A завантажує сторінку товару і читає поточний стан кошика: `["книга"]` з версією `v1`.
2. Вкладка B майже одночасно завантажує іншу сторінку і теж читає `["книга"]` з версією `v1`.
3. Користувач у вкладці A додає «навушники». Воркер 1 формує новий стан `["книга", "навушники"]` і записує його в Redis.
4. За кілька мілісекунд у вкладці B користувач натискає «додати кабель». Воркер 2, який усе ще тримає в локальній пам'яті застарілий початковий зліпок `["книга"]`, додає до нього свій товар і сліпо виконує команду `SET sess:<id> ["книга", "кабель"]`.

Результат катастрофічний: товар «навушники» безслідно зникає з кошика покупця. Ні сервер, ні клієнт не зафіксували помилки, але бізнес-стан було зруйновано.

Друга прихована проблема — неефективне керування часом життя сесії (Sliding Expiration). Якщо надсилати команду поновлення TTL `EXPIRE sess:<id> 1800` на кожен запит читання, навантаження на мережу та процесор Redis подвоюється: кожне читання перетворюється на операцію запису в журнал та реплікацію.

Нижче розібрано повну інженерну реалізацію бездержавного сесійного рушія, який усуває ці дефекти на рівні архітектури.

---

## 1. Архітектура сесійного конверта (Session Envelope)

Сесія в зовнішньому сховищі не повинна зберігатися у вигляді «сирого» бізнес-об'єкта. Вона загортається у службовий конверт (*envelope*), що містить суворі метадані версіонування, схеми та часових аудит-міток:

```json
{
  "id": "a8f3b2c1d0e9f8a7b6c5d4e3f2a1b0c9",
  "version": 3,
  "schemaVersion": 1,
  "createdAt": 1700000000000,
  "updatedAt": 1700000120000,
  "lastTouch": 1700000120000,
  "data": {
    "userId": "usr_9941",
    "role": "editor",
    "cart": ["item_101", "item_205"]
  }
}
```

Призначення кожного поля конверта:
- `id` — криптографічно безпечний 128-бітний ідентифікатор сесії, згенерований генератором CSPRNG.
- `version` — цілочисельний лічильник версії документа (починається з `1` і строго інкрементується на кожну операцію модифікації). Саме він є фундаментом механізму Compare-And-Swap (CAS).
- `schemaVersion` — версія схеми даних сесії для забезпечення зворотної сумісності під час безперервного оновлення коду бекенда.
- `createdAt` — незмінна часова мітка створення сесії в мілісекундах (epoch ms) для контролю абсолютного часу життя (Absolute Session Timeout).
- `updatedAt` — часова мітка останньої модифікації бізнес-даних.
- `lastTouch` — часова мітка останнього поновлення часу життя в Redis для алгоритму дросельованого поновлення (Throttled Touch).
- `data` — ізольований словник корисного навантаження сесії, що містить ідентифікатор користувача, роль, права та змінні стану.

---

## 2. Атомарні механізми Redis: Lua-скрипти замість розподілених блокувань

Для запобігання гонкам між паралельними воркерами існують два підходи: песимістичні розподілені блокування (Distributed Mutex на базі Redlock) та оптимістичне блокування (Optimistic Locking з версіонуванням).

Песимістичні блокування вимагають взяття блокування перед читанням сесії, продовження оренди блокування (heartbeat lock renewal) та гарантованого звільнення після завершення HTTP-відповіді. Якщо воркер падає або зависає через довгу паузу збирача сміття (Garbage Collection), сесія залишається заблокованою до вичерпання таймауту, блокуючи всі наступні запити користувача.

Оптимістичне блокування не блокує читання взагалі. Воно перевіряє версію в момент запису. Оскільки Redis є однопотоковим у виконанні команд над даними, вбудований інтерпретатор Lua виконує весь скрипт як єдину неподільну атомарну операцію (Atomic Transaction), унеможливлюючи вклинювання будь-яких проміжних запитів.

### Скрипт 1: Атомарний Compare-And-Swap (CAS)

Скрипт зчитує поточний стан ключа в пам'яті Redis, декодує JSON, порівнює збережену версію з очікуваною версією, яку надав воркер, і лише при збігу перезаписує ключ новим документом із новим TTL:

```lua
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
```

### Скрипт 2: Дросельоване поновлення TTL (Throttled Touch)

Щоб уникнути зайвих операцій запису на кожен запит читання, скрипт поновлення перевіряє, скільки часу минуло від попереднього поновлення `doc.lastTouch`. Якщо минуло менше ніж порогове значення (наприклад, 6 хвилин для 30-хвилинної сесії), операція `SET` не викликається взагалі:

```lua
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

return 2 -- дійсний стан, оновлення TTL наразі не потрібне
```

---

## 3. Повна реалізація сесійного рушія

Нижче наведено повноцінний production-код сховища на мовах TypeScript та Python.

:::tabs
```ts
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
```
```py
import json
import secrets
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import redis.asyncio as aioredis


class VersionConflictError(Exception):
    """Виникає, коли паралельний запит змінив версію сесії раніше."""
    pass


class SessionEnvelope:
    def __init__(self, session_id: str, version: int, created_at: int,
                 updated_at: int, last_touch: int, data: Dict[str, Any],
                 schema_version: int = 1):
        self.id = session_id
        self.version = version
        self.schema_version = schema_version
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_touch = last_touch
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "schemaVersion": self.schema_version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "lastTouch": self.last_touch,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SessionEnvelope":
        return cls(
            session_id=payload["id"],
            version=payload["version"],
            schema_version=payload.get("schemaVersion", 1),
            created_at=payload["createdAt"],
            updated_at=payload["updatedAt"],
            last_touch=payload["lastTouch"],
            data=payload.get("data", {}),
        )


CAS_UPDATE_LUA = """
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
"""

THROTTLED_TOUCH_LUA = """
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
"""


class StatelessRedisSessionStore:
    def __init__(self, redis_client: aioredis.Redis, ttl_seconds: int = 1800,
                 touch_threshold_ratio: float = 0.2, prefix: str = "sess:",
                 schema_version: int = 1):
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds
        self.touch_threshold_ms = int(ttl_seconds * 1000 * touch_threshold_ratio)
        self.prefix = prefix
        self.current_schema_version = schema_version

    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    def _user_key(self, user_id: str) -> str:
        return f"{self.prefix}user:{user_id}"

    def generate_session_id(self) -> str:
        """128 біт криптографічної ентропії (CSPRNG)."""
        return secrets.token_hex(16)

    async def create(self, initial_data: Optional[Dict[str, Any]] = None) -> SessionEnvelope:
        session_id = self.generate_session_id()
        now = int(time.time() * 1000)
        data = initial_data or {}
        envelope = SessionEnvelope(
            session_id=session_id,
            version=1,
            schema_version=self.current_schema_version,
            created_at=now,
            updated_at=now,
            last_touch=now,
            data=data,
        )
        payload = json.dumps(envelope.to_dict())

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(self._key(session_id), payload, ex=self.ttl_seconds)
            if "userId" in data and data["userId"]:
                user_k = self._user_key(data["userId"])
                pipe.sadd(user_k, session_id)
                pipe.expire(user_k, self.ttl_seconds * 2)
            await pipe.execute()

        return envelope

    async def get(self, session_id: str) -> Optional[SessionEnvelope]:
        raw = await self.redis.get(self._key(session_id))
        if not raw:
            return None

        try:
            data_dict = json.loads(raw)
            envelope = SessionEnvelope.from_dict(data_dict)
            
            if envelope.schema_version < self.current_schema_version:
                envelope = self._migrate_schema(envelope)

            await self._touch_throttled(session_id)
            return envelope
        except Exception:
            await self.destroy(session_id)
            return None

    async def update(self, session_id: str, expected_version: int,
                     mutator: Callable[[Dict[str, Any]], Dict[str, Any]]) -> SessionEnvelope:
        key = self._key(session_id)
        raw = await self.redis.get(key)
        if not raw:
            raise KeyError(f"SESSION_NOT_FOUND: session {session_id} not found")

        current_dict = json.loads(raw)
        current_envelope = SessionEnvelope.from_dict(current_dict)
        next_data = mutator(dict(current_envelope.data))
        now = int(time.time() * 1000)

        next_envelope = SessionEnvelope(
            session_id=session_id,
            version=expected_version + 1,
            schema_version=self.current_schema_version,
            created_at=current_envelope.created_at,
            updated_at=now,
            last_touch=now,
            data=next_data,
        )

        result = await self.redis.eval(
            CAS_UPDATE_LUA,
            1,
            key,
            str(expected_version),
            json.dumps(next_envelope.to_dict()),
            str(self.ttl_seconds),
        )

        status, code = result[0], result[1]
        if status == 0:
            if code == "VERSION_CONFLICT":
                actual_v = result[2] if len(result) > 2 else "?"
                raise VersionConflictError(f"Expected version {expected_version}, got {actual_v}")
            raise RuntimeError(f"SESSION_UPDATE_FAILED: {code}")

        return next_envelope

    async def rotate(self, old_id: str) -> SessionEnvelope:
        old_envelope = await self.get(old_id)
        if not old_envelope:
            raise KeyError(f"SESSION_NOT_FOUND: cannot rotate non-existent session {old_id}")

        new_id = self.generate_session_id()
        now = int(time.time() * 1000)
        new_envelope = SessionEnvelope(
            session_id=new_id,
            version=old_envelope.version + 1,
            schema_version=self.current_schema_version,
            created_at=old_envelope.created_at,
            updated_at=now,
            last_touch=now,
            data=old_envelope.data,
        )

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(self._key(new_id), json.dumps(new_envelope.to_dict()), ex=self.ttl_seconds)
            pipe.delete(self._key(old_id))
            if "userId" in old_envelope.data and old_envelope.data["userId"]:
                user_k = self._user_key(old_envelope.data["userId"])
                pipe.srem(user_k, old_id)
                pipe.sadd(user_k, new_id)
            await pipe.execute()

        return new_envelope

    async def destroy(self, session_id: str) -> bool:
        envelope = await self.get(session_id)
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(self._key(session_id))
            if envelope and "userId" in envelope.data and envelope.data["userId"]:
                pipe.srem(self._user_key(envelope.data["userId"]), session_id)
            res = await pipe.execute()
        return res[0] > 0

    async def destroy_all_for_user(self, user_id: str) -> int:
        user_k = self._user_key(user_id)
        session_ids = await self.redis.smembers(user_k)
        if not session_ids:
            return 0

        async with self.redis.pipeline(transaction=True) as pipe:
            for sid in session_ids:
                pipe.delete(self._key(sid.decode() if isinstance(sid, bytes) else sid))
            pipe.delete(user_k)
            await pipe.execute()

        return len(session_ids)

    async def _touch_throttled(self, session_id: str) -> None:
        now = int(time.time() * 1000)
        await self.redis.eval(
            THROTTLED_TOUCH_LUA,
            1,
            self._key(session_id),
            str(now),
            str(self.touch_threshold_ms),
            str(self.ttl_seconds),
        )

    def _migrate_schema(self, envelope: SessionEnvelope) -> SessionEnvelope:
        envelope.schema_version = self.current_schema_version
        return envelope
```
:::

---

## 4. Стратегія автоматичного повтору при колізіях (Optimistic Retry Loop)

Коли два паралельні запити одночасно намагаються оновити стан, один із них успішно збільшує версію (`v1 → v2`), а другий отримує помилку `VersionConflictError`.

Замість повернення користувачеві системної помилки `409 Conflict`, мідлвар або сервісний шар застосовує цикл повторних спроб:
1. Перехоплює помилку `VersionConflictError`;
2. Робить коротку паузу з випадковим відхиленням (Full Jitter Backoff від 5 до 20 мс), щоб розвести конкуруючі воркери в часі;
3. Зчитує з Redis свіжий актуальний стан (`v2`);
4. Накладає функцію модифікації (`mutator`) на щойно отримані дані;
5. Повторює спробу CAS-запису (`v2 → v3`).

:::tabs
```ts
export async function mutateSessionWithRetry(
  store: StatelessRedisSessionStore,
  sessionId: string,
  mutator: (data: SessionData) => SessionData,
  maxRetries = 3
): Promise<SessionEnvelope> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const session = await store.get(sessionId);
    if (!session) {
      throw new Error(`Cannot mutate non-existent session ${sessionId}`);
    }

    try {
      return await store.update(sessionId, session.version, mutator);
    } catch (err: unknown) {
      if ((err as Error).name === "VersionConflictError" && attempt < maxRetries) {
        // Експоненційне затримання з випадковим джитером для запобігання повторним колізіям
        const backoffMs = Math.random() * 15 * attempt;
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
        continue;
      }
      throw err;
    }
  }

  throw new Error(`CONCURRENCY_ERROR: exceeded max retries for session ${sessionId}`);
}
```
```py
import asyncio
import random

async def mutate_session_with_retry(
    store: StatelessRedisSessionStore,
    session_id: str,
    mutator: Callable[[Dict[str, Any]], Dict[str, Any]],
    max_retries: int = 3,
) -> SessionEnvelope:
    """Виконує модифікацію сесії з автоматичним перечитуванням при версійних конфліктах."""
    for attempt in range(1, max_retries + 1):
        session = await store.get(session_id)
        if not session:
            raise KeyError(f"Cannot mutate non-existent session {session_id}")

        try:
            return await store.update(session_id, session.version, mutator)
        except VersionConflictError:
            if attempt < max_retries:
                backoff = random.uniform(0.005, 0.02) * attempt
                await asyncio.sleep(backoff)
                continue
            raise

    raise RuntimeError(f"CONCURRENCY_ERROR: exceeded max retries for session {session_id}")
```
:::

---

## 5. Наскрізне простеження життєвого циклу HTTP-запиту

Розглянемо покроковий шлях запиту крізь бездержавний веб-сервер від моменту отримання TCP-пакета до повернення відповіді клієнту.

```
Клієнт (Браузер)
   │
   │  1. HTTP GET /api/cart (Cookie: __Host-sid=a8f3b2...)
   ▼
[Балансувальник L7] ──(Round-Robin)──► [Воркер 4 (Stateless)]
                                           │
                                           │  2. redis.get("sess:a8f3b2...")
                                           ▼
                                    [Кластер Redis]
                                           │
                                           │  3. JSON: {id, version: 2, data: {cart: [...]}}
                                           ▼
                                    [Воркер 4]
                                           │
                                           │  4. Виконання бізнес-логіки (читання/модифікація)
                                           │  5. При зміні: eval(CAS_UPDATE_LUA, v2 -> v3)
                                           ▼
                                    [Кластер Redis]
                                           │  6. Успіх (OK)
                                           ▼
                                    [Воркер 4]
                                           │
   ◄───────────────────────────────────────┘  7. HTTP 200 OK (Тіло відповіді)
```

1. **Виділення ідентифікатора з cookie:** Мідлвар аналізує заголовок `Cookie`. Якщо cookie `__Host-sid` відсутній або містить неприпустимі символи, мідлвар створює новий об'єкт гостьової сесії.
2. **Асинхронне читання з Redis:** Воркер виконує запит `GET sess:<id>`. Час операції в локальній мережі становить `< 0.5 мс`.
3. **Монтування контексту сесії в об'єкт запиту:** Сесійний конверт десеріалізується і додається до контексту виконання (наприклад, `req.session`).
4. **Виконання бізнес-коду:** Контролери додатку читають дані авторизації та модифікують бізнес-стан.
5. **Фіксація змін (Commit Phase):** Якщо під час запиту дані сесії були змінені, мідлвар виконує CAS-оновлення. Якщо дані не змінювалися, жодних операцій запису в Redis не надсилається.
6. **Встановлення HTTP-заголовків:** Якщо ідентифікатор сесії було створено заново або ротовано (наприклад, після виклику `login`), воркер додає заголовок `Set-Cookie` з обов'язковими прапорцями безпеки: `HttpOnly; Secure; SameSite=Lax; Path=/`.

---

## 6. Безпека передачі cookie: префікси `__Host-` та захист від підміни

Ідентифікатор сесії транспортується у заголовках HTTP-cookie. Для захисту від крадіжки або підміни сесії через сторонні піддомени (атака *Cookie Tossing*) сучасний стандарт RFC 6265bis впроваджує спеціальні префікси імен cookie.

### Префікс `__Host-` (Найвищий рівень захисту)
Cookie з іменем `__Host-sid` накладає на браузер суворі правила:
1. Обов'язковий прапорець `Secure` (передача виключно через HTTPS);
2. Обов'язковий атрибут `Path=/` (доступний для всіх шляхів домену);
3. **Заборонено вказувати атрибут `Domain`:** такий cookie зберігається виключно для поточного точного домену (`example.com`) і недоступний жодному піддомену (`sub.example.com`). Це виключає атаку, коли скомпрометований піддомен записує фальшивий сесійний cookie для основного сайту.

### Атрибут `SameSite` та захист від CSRF
- `SameSite=Lax` — стандартне надійне значення. Cookie надсилається при звичайних кліках за посиланнями з інших сайтів (безпечні GET-переходи), але блокується при міжсайтових POST-запитах форм, скриптах або вбудованих iframe.
- `SameSite=Strict` — максимальна ізоляція. Cookie не додається до жодного міжсайтового переходу, вимагаючи повторного переходу всередині сайту.

---

## 7. Налаштування мережевого пулу з'єднань Redis у високонавантаженому середовищі

Для досягнення мінімальної затримки викликів клієнт Redis на кожному бездержавному воркері налаштовується з урахуванням специфіки асинхронного вводу-виводу:
1. **Підтримка постійних TCP-з'єднань (Persistent Connection Pool):** створення нового TCP-з'єднання на кожен HTTP-запит додає 1–2 мс на тристороннє рукостискання (3-Way Handshake). Клієнт ioredis або redis-py утримує єдиний пул постійно відкритих сокетів.
2. **Параметр TCP Keepalive (`keepAlive: 10000`):** надсилає періодичні зондувальні пакети для запобігання мовчазному розриву з'єднання мережевими екранами (Firewall NAT timeout).
3. **Автоматичне пакетування (Auto-Pipelining):** якщо кілька паралельних запитів одночасно звертаються до Redis, клієнт автоматично об'єднує їхні команди в єдиний мережевий буфер сокета, кардинально скорочуючи кількість системних викликів `write()` та перемикань контексту ядра.

---

## 8. Серіалізація: порівняння форматів та оптимізація пропускної здатності

Сесійний об'єкт повинен трансформуватися в бінарний потік байтів для передачі по мережі в Redis. Вибір формату серіалізації прямо впливає на споживання пам'яті Redis та час роботи збирача сміття у веб-воркерах.

### 1. JSON (JavaScript Object Notation)
- **Переваги:** Текстовий формат, вбудована підтримка у всіх мовах, зручність налагодження (можна прочитати вміст ключа безпосередньо через консоль `redis-cli`).
- **Недоліки:** Надлишковий розмір через повторення текстових ключів (`"createdAt"`, `"updatedAt"` тощо), повільніший парсинг у мовах без C-розширень.

### 2. MessagePack (Двійковий JSON)
- **Переваги:** Бінарний компактний формат, що зберігає ту саму динамічну модель даних, але кодує числа, рядки та ключі компактними бінарними маркерами. Зменшує розмір сесії на 30–45% і прискорює десеріалізацію в 2.5–4 рази.
- **Недоліки:** Вимагає сторонньої бібліотеки на воркерах та додаткового C-модуля для розбору всередині Redis Lua-скриптів.

### 3. Protocol Buffers (Protobuf)
- **Переваги:** Максимально компактний двійковий формат із суворою схемою, нумерацією полів замість імен і найвищою швидкістю серіалізації.
- **Недоліки:** Потребує компіляції `.proto` файлів та суворої дисципліни версіонування полів.

Для переважної більшості високонавантажених веб-систем форматом за замовчуванням залишається оптимізований JSON або MessagePack, оскільки вони забезпечують ідеальний баланс між гнучкістю бізнес-полів та продуктивністю.

---

## 9. Еволюція схеми сесії у живій системі (Zero-Downtime Schema Migration)

При безперервному розгортанні нових релізів (Rolling Deployment) у кластері одночасно працюють воркери нової версії (v2) і старої версії (v1).

Якщо нова версія змінює структуру сесії (наприклад, розбиває поле `name` на `firstName` та `lastName`), виникає ризик пошкодження даних:
- Старий воркер читає новий формат і відкидає невідомі поля;
- Новий воркер читає старий формат і падає через `undefined property error`.

Щоб гарантувати сумісність:
1. **Правило розширення (Additive Changes):** Ніколи не видаляйте та не перейменовуйте старі поля сесії в одному релізі. Додавайте нові поля поруч як необов'язкові (`optional`).
2. **Поле `schemaVersion` у конверті:** Новий код перевіряє `schemaVersion`. Якщо версія старіша за поточну, спрацьовує лінива функція трансформації (`migrateSchema`), яка на льоту доповнює об'єкт новими значеннями за замовчуванням.
3. **Двоетапне розгортання:** У першому релізі додається підтримка читання обох форматів і запис у новому форматі. Лише через тиждень (коли всі старі сесії природно згаснуть за таймаутом) випускається реліз, що видаляє застарілий код підтримки.

---

## 10. Відкликання сесій та індексація за користувачем

Коли користувач натискає «вийти на всіх пристроях» або змінює пароль після підозрілої активності, система повинна миттєво анулювати всі його активні сесії.

Оскільки ідентифікатори сесій генеруються випадково, прямий пошук за допомогою команди `KEYS sess:*` є неприпустимим: у базі з мільйонами ключів команда `KEYS` блокує головний потік Redis на кілька секунд, спричиняючи повний параліч бекенда.

Правильне рішення полягає у підтримці вторинного індексу — множини Redis `sess:user:<userId>`. При створенні нової сесії її ідентифікатор додається до цієї множини. При загальному виході метод `destroyAllForUser` отримує список усіх `sid` користувача однією швидкою командою `SMEMBERS` і видаляє їх через пакетний конвеєр (Pipeline).

---

## 11. Автоматизоване тестування на стійкість до гонок

Для підтвердження надійності CAS-рушія пишуть стрес-тест, який емулює масові паралельні запити до однієї сесії.

:::tabs
```ts
import { StatelessRedisSessionStore, mutateSessionWithRetry } from "./sessionStore";
import Redis from "ioredis";

async function runConcurrencyTest() {
  const redis = new Redis();
  const store = new StatelessRedisSessionStore(redis);

  // Створюємо початкову сесію з порожнім списком товарів
  const session = await store.create({ items: [] });
  const sessionId = session.id;

  const CONCURRENT_REQUESTS = 20;

  // Запускаємо 20 паралельних воркерів, кожен з яких додає свій унікальний товар
  const tasks = Array.from({ length: CONCURRENT_REQUESTS }, (_, i) =>
    mutateSessionWithRetry(store, sessionId, (data) => {
      const items = (data.items as string[]) || [];
      return {
        ...data,
        items: [...items, `item_${i + 1}`],
      };
    })
  );

  await Promise.all(tasks);

  // Перевіряємо фінальний стан сесії в Redis
  const finalSession = await store.get(sessionId);
  const items = (finalSession?.data.items as string[]) || [];

  console.log(`Очікувалось товарів: ${CONCURRENT_REQUESTS}, фактично в сесії: ${items.length}`);
  console.log(`Фінальна версія сесії: ${finalSession?.version}`);

  if (items.length === CONCURRENT_REQUESTS) {
    console.log("ТЕСТ ПРОЙДЕНО: жоден товар не було втрачено завдяки CAS-повторам!");
  } else {
    console.error("ТЕСТ ПРОВАЛЕНО: виявлено втрачені оновлення (Lost Updates)!");
  }

  await store.destroy(sessionId);
  await redis.quit();
}
```
```py
import asyncio
import redis.asyncio as aioredis
from session_store import StatelessRedisSessionStore, mutate_session_with_retry

async def run_concurrency_test():
    redis = aioredis.from_url("redis://localhost:6379")
    store = StatelessRedisSessionStore(redis)

    session = await store.create({"items": []})
    session_id = session.id

    concurrent_requests = 20

    async def append_item(index: int):
        await mutate_session_with_retry(
            store,
            session_id,
            lambda data: {**data, "items": data.get("items", []) + [f"item_{index}"]},
        )

    # Запускаємо 20 паралельних корутин
    await asyncio.gather(*(append_item(i + 1) for i in range(concurrent_requests)))

    final_session = await store.get(session_id)
    items = final_session.data.get("items", []) if final_session else []

    print(f"Очікувалось товарів: ${concurrent_requests}, фактично в сесії: ${len(items)}")
    print(f"Фінальна версія документа: ${final_session.version if final_session else 'None'}")

    assert len(items) == concurrent_requests, "Виявлено втрату оновлень!"
    print("ТЕСТ ПРОЙДЕНО: усі паралельні модифікації збережено успішно!")

    await store.destroy(session_id)
    await redis.aclose()

if __name__ == "__main__":
    asyncio.run(run_concurrency_test())
```
:::

---

## 12. Інженерні пастки та правила надійності

1. **Режим відмови Redis (Fail-Closed проти Fail-Open).**
   Якщо кластер Redis стає тимчасово недоступним через мережеве розділення (Network Partition), система повинна мати чіткий контракт поведінки:
   - Для мутуючих операцій (POST, PUT, DELETE) та маршрутів, що вимагають прав доступу, обов'язковий режим **Fail-Closed** — негайне повернення помилки `503 Service Unavailable`. Виконання операцій без перевірки прав є критичною вразливістю.
   - Для публічних операцій читання (каталог товарів, головна сторінка) застосовується режим **Fail-Open / Anonymous Grace** — запит обробляється так, ніби сесія відсутня, без падіння інтерфейсу для анонімного відвідувача.

2. **Захист від атак на десеріалізацію (Prototype Pollution).**
   При зчитуванні JSON із зовнішнього сховища не можна використовувати сліпе копіювання полів через `Object.assign({}, raw)`. Зловмисник, який зумів змінити значення сесії в Redis, може впорснути властивості `__proto__` або `constructor.prototype`, що скомпрометує весь процес Node.js. Використовуйте сувору типізацію та створюйте нові плоскі словники.

3. **Розділення інстансів Redis під кеш і під сесії.**
   Категорично заборонено використовувати той самий екземпляр Redis для некритичного кешу сторінок і для сесій користувачів з політикою витіснення пам'яті `maxmemory-policy: allkeys-lru`. Під час сплеску трафіку Redis почне витісняти живі сесії користувачів заради збереження кешу відповідей. Сховище сесій має бути окремим сервером або кластером із політикою `noeviction` (помилка при вичерпанні пам'яті замість тихих втрат сесій) або `volatile-lru` (витіснення лише ключів із явним тимчасовим TTL).

4. **Розбіжність системних годинників (NTP Clock Skew).**
   У розподіленому кластері системний час окремих серверів може розходитися на десятки мілісекунд. Тому перевірка закінчення терміну дії сесії виконується не через порівняння локального `Date.now()` на кожному воркері, а безпосередньо в Redis за допомогою вбудованого таймера TTL (`EXPIRE`). Це гарантує єдиний авторитетний часовий вимір для всіх вузлів системи.

5. **Топологія високої доступності (Redis Sentinel проти Redis Cluster).**
   Для продуктивних сесійних сховищ використовують одну з двох топологій:
   - **Redis Sentinel (Master-Replica):** підходить для середнього навантаження (до 100 000 одночасних сесій). Sentinel автоматично підвищує репліку до майстра при падінні основного вузла за 2–5 секунд.
   - **Redis Cluster (Sharding):** для масштабних систем (від 500 000 сесій). Дані розподіляються по 16384 геш-слотах. При використанні Lua-скриптів із декількома ключами (наприклад, сесія та користувацький індекс) обов'язково застосовують геш-теги (`{user:123}:sess` та `{user:123}:user`), щоб обидва ключі гарантовано потрапили на один шардинговий вузол.
