# ⚙️ Реалізація рушія Feature Flags та канарейкового оцінювача

Локальний оцінювач Feature Flags здійснює детерміноване розкатування канарейкових функцій (англ. *deterministic percentage rollout*). Внутрішні алгоритми обчислюють належність користувача до канарейкової групи за допомогою криптографічного хешування без додаткових мережевих затримок під час кожного виклику.

## Концепція та інваріанти

Головна проблема ненадійної канарейки — літаючий стан (англ. *flapping evaluation*): якщо при кожному запиті користувач потрапляє у випадкову групу (наприклад, через `rand() % 100 < 5`), його сесія буде постійно «стрибати» між новою та старою версіями коду. Це зламає UX (кнопки зникатимуть і з'являтимуться знову при перезавантаженні сторінки) і створить приховані race conditions у базі даних.

**Інваріанти надійного оцінювача:**
1. **Детермінованість:** один і той самий користувач (`user_id`) для того самого прапорця завжди отримує одне й те саме рішення за незмінного відсотка викатки.
2. **Незвязаність прапорців:** включення в канарейку 5% для прапорця `A` не повинно означати включення тих самих 5% користувачів для прапорця `B` (використовується сіль `salt = flag_key`).
3. **Локальність оцінки (Zero IO):** оцінка правила відбувається в пам'яті процесу за `< 1 microsecond` без synchronous HTTP/gRPC виклику до сервера прапорців.

---

## Детерміноване хешування: FNV-1a проти звичайного Modulo

Використання прямого залишкового ділення від числового ID користувача (`user_id % 100`) містить приховану небезпеку: якщо ідентифікатори користувачів авто-інкрементні парні числа (2, 4, 6, 8...), канарейковий розподіл буде кластеризованим і викривленим.

Для забезпечення рівномірного псевдовипадкового розподілу вибірки застосовується незахищена, але надзвичайно швидка хеш-функція **FNV-1a (Fowler–Noll–Vo)** або **MurmurHash3**. Вони перетворюють будь-який рядок `flag_key + ":" + user_id` на 64-бітне ціле число з рівномірним розподілом бітів (лавинний ефект, англ. *avalanche effect*), мінімізуючи колізії.

---

## Покроковий розбір оцінювача

:::tabs
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cstdint>
#include <memory>
#include <atomic>

// 64-bit FNV-1a хеш-функція для рівномірного розподілу бакетів
uint64_t fnv1a_hash(const std::string& input) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : input) {
        hash ^= static_cast<uint64_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

struct EvaluationContext {
    std::string user_id;
    std::string tenant_id;
    std::string user_role;
    std::unordered_map<std::string, std::string> attributes;
};

enum class FlagState {
    OFF,
    ON,
    PERCENTAGE_ROLLOUT,
    TARGETED
};

struct FeatureFlagRule {
    std::string flag_key;
    FlagState state = FlagState::OFF;
    uint32_t rollout_percentage = 0; // 0..100
    std::vector<std::string> allowed_roles;
    std::vector<std::string> allowed_user_ids;
};

class FeatureFlagEngine {
private:
    std::unordered_map<std::string, FeatureFlagRule> rules_;

public:
    void register_rule(const FeatureFlagRule& rule) {
        rules_[rule.flag_key] = rule;
    }

    bool is_enabled(const std::string& flag_key, const EvaluationContext& ctx) const {
        auto it = rules_.find(flag_key);
        if (it == rules_.end()) {
            return false; // За замовчуванням вимкнено (Safe Fallback)
        }

        const auto& rule = it->second;

        // 1. Абсолютні операційні рубильники (Emergency Kill-Switches)
        if (rule.state == FlagState::OFF) return false;
        if (rule.state == FlagState::ON) return true;

        // 2. Таргетовані користувачі (Explicit Allowlist / Beta Testers)
        for (const auto& uid : rule.allowed_user_ids) {
            if (uid == ctx.user_id) return true;
        }

        // 3. Перевірка обмеження ролей
        if (!rule.allowed_roles.empty()) {
            bool role_matched = false;
            for (const auto& role : rule.allowed_roles) {
                if (role == ctx.user_role) {
                    role_matched = true;
                    break;
                }
            }
            if (!role_matched) return false;
        }

        // 4. Детермінований відсотковий розкочувальний аналіз (Canary Rollout)
        if (rule.state == FlagState::PERCENTAGE_ROLLOUT) {
            if (rule.rollout_percentage == 0) return false;
            if (rule.rollout_percentage >= 100) return true;

            // Сіль (flag_key) захищає від кореляції між різними прапорцями
            std::string hash_input = flag_key + ":" + ctx.user_id;
            uint64_t hash_val = fnv1a_hash(hash_input);
            uint32_t bucket = static_cast<uint32_t>(hash_val % 100);

            return bucket < rule.rollout_percentage;
        }

        return false;
    }
};

int main() {
    FeatureFlagEngine engine;

    // Створюємо канарейкове правило для нового алгоритму розблокування смарт-замка DH
    FeatureFlagRule lock_v2_flag{
        "smart_lock_v2_algorithm",
        FlagState::PERCENTAGE_ROLLOUT,
        10, // 10% канарейка
        {}, // без обмеження за ролями
        {"beta_tester_99"} // конкретний бета-тестер завжди включений
    };

    engine.register_rule(lock_v2_flag);

    EvaluationContext user_beta{"beta_tester_99", "home_42", "resident", {}};
    EvaluationContext user_regular_1{"user_101", "home_12", "resident", {}};
    EvaluationContext user_regular_2{"user_204", "home_88", "resident", {}};

    std::cout << "Beta user test: " << engine.is_enabled("smart_lock_v2_algorithm", user_beta) << " (Expected: 1)\n";
    std::cout << "User 101 canary test: " << engine.is_enabled("smart_lock_v2_algorithm", user_regular_1) << "\n";
    std::cout << "User 204 canary test: " << engine.is_enabled("smart_lock_v2_algorithm", user_regular_2) << "\n";

    // Перевірка детермінованості повторного виклику
    bool first_eval = engine.is_enabled("smart_lock_v2_algorithm", user_regular_1);
    bool second_eval = engine.is_enabled("smart_lock_v2_algorithm", user_regular_1);
    std::cout << "Consistency check for user_101: " << (first_eval == second_eval ? "PASSED" : "FAILED") << "\n";

    return 0;
}
```
```py
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
```
:::

---

## Послідовність обробки шарів правил (Evaluation Pipeline Hierarchy)

При кожному виклику `is_enabled()` оцінювач гарантує суворий порядок пріоритетів перевірки правил:

1. **Захисний шар (Global Safe Fallback):** перевірка наявності прапорця у реєстрі правил. Якщо прапорець не зареєстрований або зламався конфіг — негайне повернення `false`.
2. **Операційний шар (Emergency Kill-Switch):** якщо прапорець переведений у стан `OFF` оператором, далі жодні правила не аналізуються — повертається `false`. Аналогічно стан `ON` негайно повертає `true`.
3. **Персональний шар (Allowlist / Denylist):** перевірка явного входження `ctx.user_id` у списки бета-тестерів або заблокованих користувачів.
4. **Сегментний шар (Targeting Rules):** аналіз атрибутів ролі, версії мобільного застосунку, географічного регіону чи тарифного плану.
5. **Статистичний шар (Canary Bucket Rollout):** розрахунок бакета `0..99` через хешування `salt:user_id`. Якщо `bucket < rollout_percentage` — повертається `true`.

---

## Потокобезпечність та локальне оновлення правил (Thread-Safety & RCU)

У багатопотоковому середовищі (наприклад, веб-сервер C++ із 32 робочими потоками чи Python Gunicorn/Uvicorn) фоновий потік оновлення правил (Sync Loop) може змінювати `rules_` під час виконання запитів.

Щоб запобігти блокуванню гарячого шляху (Lock Contention), в реальних високопродуктивних SDK застосовують тактику **Read-Copy-Update (RCU)** через атомарні вказівники:

```cpp
// Контейнер правил є незмінним (immutable) об'єктом
std::atomic<std::shared_ptr<const FlagRuleset>> current_ruleset_;

// Читання на гарячому шляху (Lock-Free)
bool is_enabled(...) {
    auto rules = current_ruleset_.load(std::memory_order_relaxed);
    return rules->eval(...);
}

// Оновлення з фонового потоку
void update_ruleset(std::shared_ptr<const FlagRuleset> new_rules) {
    current_ruleset_.store(new_rules, std::memory_order_release);
}
```

Такий підхід повністю усуває mutex-заморожування, дозволяючи виконувати мільйони оцінок прапорців на секунду без затримок.

---

## Продуктивність та обсяг пам'яті (Profiling & Memory Footprint)

При виборі реалізації рушія оцінки прапорців важливо враховувати продуктивність хешування та споживання RAM:

1. **Бенчмарк хешування:** FNV-1a 64-bit обчислюється за `~12 nanoseconds` на процесорний рядок із 32 символів. Застосування криптографічних хешів (SHA-256) займає `~450 nanoseconds`, що в 35 разів повільніше. Оскільки прапорці не вимагають криптографічної стійкості до атак підробки хешу, FNV-1a або MurmurHash3 є ідеальним вибором.
2. **Обсяг пам'яті (Memory Footprint):** Реєстр на 1000 прапорців у пам'яті C++ займає близько `180 KB`. У Python через динамічну накладну вартість об'єктів той самий набір займає `~1.2 MB`.

---

## Локальна персистентність та холодний запуск (Offline Cold Start)

Для забезпечення стійкості під час перезапуску сервісів (Cold Start), коли центральний сервер прапорців може бути тимчасово недоступним, SDK зберігає останній валідний знімок ruleset на локальний диск:

`/var/lib/flags/ruleset.snapshot.json`

При старті процес спочатку завантажує цей диск-кеш (Cold Cache Bootstrap), досягаючи готовності за частки мілісекунди, і лише потім відправляє фоновий HTTP-запит на отримання свіжих оновлень.

---

## Буферизація телеметрії та захист від блокувань (Async Telemetry Buffer)

Для забезпечення канарейкового моніторингу оцінювач не повинен робити виклики аналітики прямо у виклику `is_enabled()`. Реєстрація подій оцінки реалізується через ring buffer у пам'яті з фіксованим розміром (наприклад, 10 000 елементів).

Окремий фоновий потік вичитує буфер і відправляють усереднені лічильники на сервер телеметрії розкочування. Якщо буфер переповнюється через аномальний сплеск навантаження, нові події оцінки відраховуються (drop metrics), зберігаючи роботу основного бізнес-коду.

---

## Тестування рівномірності та граночних умов (Testing & Edge Cases)

Під час написання юніт-тестів для рушія прапорців необхідно обов'язково перевіряти чотири крайові випадки:
1. **Порожній контекст (Missing Context Attributes):** якщо `user_id` відсутній або дорівнює порожньому рядку `""`, рушій не мусить падає з винятком NullPointer, а повертає `false` або бере замінник `session_id`.
2. **Нульовий та повний відсоток (Boundary Percentages):** при `rollout_percentage = 0` жоден хеш не повинен давати `true`; при `rollout_percentage = 100` всі користувачі мають отримати `true`.
3. **Перевірка рівномірності хешування (Distribution Uniformity Test):** генерація 100 000 випадкових синтетичних `user_id` при відсотку канарейки `10%` повинна дати підсумковий відсоток включення у межах `9.8% .. 10.2%`.
