import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class EvaluationContext:
    user_id: str
    tenant_id: str
    user_role: str
    attributes: Dict[str, str] = field(default_factory=dict)

class FlagState:
    OFF = "OFF"
    ON = "ON"
    PERCENTAGE_ROLLOUT = "PERCENTAGE_ROLLOUT"

@dataclass
class FeatureFlagRule:
    flag_key: str
    state: str = FlagState.OFF
    rollout_percentage: int = 0  # 0..100
    allowed_roles: List[str] = field(default_factory=list)
    allowed_user_ids: List[str] = field(default_factory=list)

class FeatureFlagEngine:
    def __init__(self):
        self._rules: Dict[str, FeatureFlagRule] = {}

    def register_rule(self, rule: FeatureFlagRule) -> None:
        self._rules[rule.flag_key] = rule

    def _hash_bucket(self, flag_key: str, user_id: str) -> int:
        """Детермінований розрахунок бакета 0..99 за допомогою MD5/SHA256 хешу."""
        seed_str = f"{flag_key}:{user_id}".encode("utf-8")
        digest = hashlib.md5(seed_str).hexdigest()
        # Беремо останні 8 символів хешу як ціле число
        val = int(digest[-8:], 16)
        return val % 100

    def is_enabled(self, flag_key: str, ctx: EvaluationContext) -> bool:
        rule = self._rules.get(flag_key)
        if not rule:
            return False

        if rule.state == FlagState.OFF:
            return False
        if rule.state == FlagState.ON:
            return True

        # 1. Пряма перевірка дозволених ID (Explicit Allowlist)
        if ctx.user_id in rule.allowed_user_ids:
            return True

        # 2. Перевірка відповідності ролі
        if rule.allowed_roles and ctx.user_role not in rule.allowed_roles:
            return False

        # 3. Детермінований бакет відсоткового розкочування
        if rule.state == FlagState.PERCENTAGE_ROLLOUT:
            if rule.rollout_percentage <= 0:
                return False
            if rule.rollout_percentage >= 100:
                return True

            bucket = self._hash_bucket(flag_key, ctx.user_id)
            return bucket < rule.rollout_percentage

        return False


if __name__ == "__main__":
    engine = FeatureFlagEngine()
    engine.register_rule(FeatureFlagRule(
        flag_key="climate_ai_v2",
        state=FlagState.PERCENTAGE_ROLLOUT,
        rollout_percentage=25,
        allowed_user_ids=["vip_admin_1"]
    ))

    ctx1 = EvaluationContext(user_id="vip_admin_1", tenant_id="h1", user_role="admin")
    ctx2 = EvaluationContext(user_id="user_777", tenant_id="h2", user_role="resident")

    print(f"VIP user: {engine.is_enabled('climate_ai_v2', ctx1)}")
    print(f"Canary user_777: {engine.is_enabled('climate_ai_v2', ctx2)}")
