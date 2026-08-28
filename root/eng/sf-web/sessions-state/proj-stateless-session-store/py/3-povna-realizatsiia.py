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
