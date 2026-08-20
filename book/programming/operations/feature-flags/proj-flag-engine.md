# ⚙️ Двигунець обчислення прапорців з атомарним оновленням правил

На виробничих серверах з високим навантаженням (десятки тисяч HTTP-запитів на секунду на один інстанс) перевірка прапорців функцій виконується сотні разів під час обробки кожного окремого запиту. Прапорець опитується на рівні маршрутизатора API, у шарі бізнес-домену для вибору алгоритму знижки, у клієнті бази даних для перемикання репліки читання та у форматтері вихідного JSON.

Якщо рушій обчислення звертається по мережі до зовнішнього сховища (Redis, Consul чи SaaS-сервісу) або блокує спільний м'ютекс на кожне читання конфігурації, це створює катастрофічну затримку (англ. *latency*) та вузьке місце масштабування.

Інженерна мета цього проєкту — побудувати високоефективний потокобезпечний рушій обчислення прапорців у пам'яті (англ. *In-Memory Evaluation Engine*), який:
1. Виконує обчислення в гарячому шляху за час **менше 1 мікросекунди** без виділення пам'яті на купі (*zero-allocation evaluation*);
2. Підтримує **неблокуюче атомарне оновлення правил** на льоту без зупинки читаючих потоків;
3. Реалізує повний конвеєр правил: перевизначення за ID, таргетинг за атрибутами та детерміноване хеш-бакетування (MurmurHash3);
4. Надає точки розширення для телеметрії та збору метрик спрацьовування.

## 1. Архітектурна проблема та аналіз навантаження

У класичному веб-сервері з пулом потоків (наприклад, 32 або 64 робочих потоки, що обробляють чергу запитів) кожен потік виконує незалежні транзакції. Якщо всі ці потоки одночасно звертаються до спільного стану конфігурації прапорців, наївне використання блокувань (`std::mutex` або `std::shared_mutex`) призводить до деградації пропускної здатності через явище **конкуренції за блокування** (англ. *lock contention*).

Коли потік намагається захопити м'ютекс, який утримується іншим ядром процесора, операційна система переводить потік у стан сну (блокування ядра через системний виклик `futex` у Linux). Це спричиняє перемикання контексту процесора (вартістю 1–3 мікросекунди), скидання кешу інструкцій L1/L2 та різке зростання хвостової затримки навантаження (99-й та 99.9-й перцентилі часу відповіді сервісу).

Крім того, виклик прапорця не може бути мережевим RPC-запитом: навіть запит до локального Redis через Unix-сокет додає 0.3–0.8 мікросекунди на кожен прапорець. Якщо один HTTP-запит перевіряє 20 прапорців, сервіс витратить 16 мілісекунд суто на очікування відповідей про прапорці.

Тому єдиним життєздатним рішенням для критичних сервісів є **повна реплікація правил у локальну оперативну пам'ять процесу (In-Memory Engine)**.

## 2. Архітектурна ідея: атомарна заміна знімка (Atomic Pointer Swap)

Для забезпечення абсолютно неблокуючого паралельного читання застосовують патерн **копіювання при записі з атомарною підміною вказівника** (англ. *Atomic Pointer Swap* / RCU-подібний механізм).

Суть підходу полягає у суворому розділенні структур даних на дві неперетинні ролі:
1. **Незмінний знімок конфігурації (`RuleSet`):** структура даних, що містить розпарсені правила для всіх прапорців. Після створення цей об'єкт є абсолютно незмінним (*immutable*). Читаючі потоки мають право тільки читати поля цього об'єкта, тому операції читання є повністю безпечними без жодних блокувань і м'ютексів.
2. **Атомарне посилання на актуальний знімок:** глобальний стан рушія зводиться до єдиного атомарного розумного вказівника (`std::atomic<std::shared_ptr<RuleSet>>`).

Коли фоновий потік отримує свіжі правила від контрольної панелі через SSE або опитування, він не змінює наявний об'єкт. Натомість він повністю створює новий екземпляр `RuleSet` в окремій області пам'яті, валідує його цілісність і в одну атомарну операцію (інструкція CPU `LOCK CMPXCHG` або атомарний запис з семантикою `std::memory_order_release`) підміняє глобальний вказівник.

Читаючі потоки, які в цей момент виконували запит за старим знімком, спокійно дочитують старі дані завдяки лічильнику посилань `std::shared_ptr`. Як тільки останній читач завершує обробку запиту, лічильник падає до нуля і стара пам'ять автоматично звільняється без блокування нових читачів.

## 3. Порівняльний аналіз стратегій синхронізації

Щоб зрозуміти перевагу атомарної заміни вказівника, зіставимо три основні підходи синхронізації стану при 64 паралельних потоках читання:

| Стратегія | Механізм читання | Затримка читання (p99) | Пропускна здатність | Поведінка при оновленні |
|---|---|---|---|---|
| Ексклюзивний м'ютекс (`std::mutex`) | Блокування на кожен виклик | ~12.5 мкс | ~1.8 млн оп/сек | Блокує всіх читачів на час парсингу |
| Читач-письменник (`std::shared_mutex`) | `shared_lock` (атомарні лічильники) | ~3.8 мкс | ~8.5 млн оп/сек | Письменник чекає завершення всіх читачів |
| **Atomic Pointer Swap (`std::atomic<shared_ptr>`)** | **Копіювання адреси (`acquire`)** | **~0.08 мкс (80 нс)** | **> 120 млн оп/сек** | **Нуль очікувань, миттєвий swap** |

Як свідчить порівняння, атомарна заміна вказівника випереджає традиційні блокування за швидкістю більш ніж на порядок завдяки відсутності перезапису кеш-ліній між ядрами процесора при читанні.

## 4. Запобігання помилковому розділенню кеш-ліній (False Sharing)

У сучасних багатоядерних процесорах кеш-пам'ять L1/L2 оперує блоками по 64 байти (кеш-лінії). Якщо атомарний вказівник на правила знаходиться в одній кеш-лінії з часто змінюваними змінними (наприклад, лічильником запитів фонового потоку), операції запису цього лічильника будуть інвалідувати кеш-лінію у всіх 64 процесорних ядер, що виконують читання.

Для усунення цього ефекту поле атомарного вказівника вирівнюють за розміром кеш-лінії за допомогою специфікатора `alignas(64)`:

```cpp
// Вирівнювання за розміром кеш-лінії x86/ARM64 (64 байти)
alignas(64) std::shared_ptr<RuleSet> ruleset_;
```

Це гарантує, що лінія кешу, яка містить адресу актуального знімка правил, ніколи не скидається сусідніми операціями запису, забезпечуючи максимальну швидкість читання з кешу L1D процесора.

## 5. Реалізація рушія

Розглянемо повну промислову реалізацію рушія мовами C++ та TypeScript.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <variant>
#include <memory>
#include <atomic>
#include <cstdint>
#include <algorithm>
#include <cstring>

// Атрибути користувача: підтримуємо рядки, числа та булеві значення
using AttributeValue = std::variant<std::string, double, bool>;

struct EvaluationContext {
    std::string targeting_key;
    std::unordered_map<std::string, AttributeValue> attributes;
};

// Реалізація алгоритму MurmurHash3_x86_32 для детермінованого бакетування
uint32_t murmur3_32(std::string_view key, uint32_t seed = 0) {
    uint32_t h = seed;
    const size_t nblocks = key.size() / 4;
    const uint32_t* blocks = reinterpret_cast<const uint32_t*>(key.data());

    for (size_t i = 0; i < nblocks; ++i) {
        uint32_t k = blocks[i];
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;

        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }

    const uint8_t* tail = reinterpret_cast<const uint8_t*>(key.data() + nblocks * 4);
    uint32_t k1 = 0;
    switch (key.size() & 3) {
        case 3: k1 ^= static_cast<uint32_t>(tail[2]) << 16; [[fallthrough]];
        case 2: k1 ^= static_cast<uint32_t>(tail[1]) << 8;  [[fallthrough]];
        case 1: k1 ^= static_cast<uint32_t>(tail[0]);
                k1 *= 0xcc9e2d51;
                k1 = (k1 << 15) | (k1 >> 17);
                k1 *= 0x1b873593;
                h ^= k1;
    }

    h ^= static_cast<uint32_t>(key.size());
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

// Правило таргетингу за атрибутом (наприклад, country == "UA")
struct TargetingRule {
    std::string attribute_name;
    std::string expected_string_value;
    bool enabled_value;
};

// Конфігурація окремого прапорця
struct FlagDefinition {
    std::string key;
    bool default_value = false;
    uint32_t rollout_percentage = 0; // 0 - 100%
    std::vector<std::string> whitelist_users;
    std::vector<TargetingRule> rules;
};

// Незмінний набір усіх правил системи
struct RuleSet {
    std::unordered_map<std::string, FlagDefinition> flags;
};

// Результат обчислення прапорця
struct EvaluationResult {
    bool value;
    std::string_view reason; // "OVERRIDE", "RULE_MATCH", "PERCENTAGE_ROLLOUT", "DEFAULT"
};

// Двигунець обчислення в пам'яті з атомарним оновленням
class FlagEngine {
public:
    FlagEngine() : ruleset_(std::make_shared<RuleSet>()) {}

    // Неблокуюче обчислення значення (гарячий шлях)
    EvaluationResult evaluate(std::string_view flag_key, const EvaluationContext& ctx) const {
        // Атомарно захоплюємо поточний знімок конфігурації (acquire semantics)
        auto current_rules = std::atomic_load_explicit(&ruleset_, std::memory_order_acquire);
        
        auto it = current_rules->flags.find(std::string(flag_key));
        if (it == current_rules->flags.end()) {
            return { false, "FLAG_NOT_FOUND" };
        }

        const auto& flag = it->second;

        // 1. Перевірка списку індивідуальних перевизначень (Whitelist)
        for (const auto& user_id : flag.whitelist_users) {
            if (user_id == ctx.targeting_key) {
                return { true, "OVERRIDE" };
            }
        }

        // 2. Перевірка правил таргетингу за контекстними атрибутами
        for (const auto& rule : flag.rules) {
            auto attr_it = ctx.attributes.find(rule.attribute_name);
            if (attr_it != ctx.attributes.end()) {
                if (const auto* str_val = std::get_if<std::string>(&attr_it->second)) {
                    if (*str_val == rule.expected_string_value) {
                        return { rule.enabled_value, "RULE_MATCH" };
                    }
                }
            }
        }

        // 3. Перевірка відсоткової розкатки за MurmurHash3
        if (flag.rollout_percentage > 0 && !ctx.targeting_key.empty()) {
            // Формуємо ключ: flag_key + ":" + targeting_key
            std::string hash_input = std::string(flag_key) + ":" + ctx.targeting_key;
            uint32_t hash_val = murmur3_32(hash_input);
            uint32_t bucket = hash_val % 100;

            if (bucket < flag.rollout_percentage) {
                return { true, "PERCENTAGE_ROLLOUT" };
            }
        }

        // 4. Повернення значення за замовчуванням
        return { flag.default_value, "DEFAULT" };
    }

    // Фонове атомарне оновлення конфігурації правил
    void update_rules(std::shared_ptr<RuleSet> new_rules) {
        std::atomic_store_explicit(&ruleset_, std::move(new_rules), std::memory_order_release);
    }

private:
    alignas(64) std::shared_ptr<RuleSet> ruleset_;
};
```
```ts
// TypeScript / Node.js реалізація In-Memory рушія
import * as crypto from "crypto";

export interface EvaluationContext {
  targetingKey: string;
  attributes?: Record<string, string | number | boolean>;
}

export interface TargetingRule {
  attributeName: string;
  expectedValue: string | number | boolean;
  enabledValue: boolean;
}

export interface FlagDefinition {
  key: string;
  defaultValue: boolean;
  rolloutPercentage: number; // 0 - 100
  whitelistUsers: string[];
  rules: TargetingRule[];
}

export interface EvaluationResult {
  value: boolean;
  reason: "OVERRIDE" | "RULE_MATCH" | "PERCENTAGE_ROLLOUT" | "DEFAULT" | "FLAG_NOT_FOUND";
}

export class FlagEngine {
  private ruleset: Map<string, FlagDefinition> = new Map();

  // Неблокуюче обчислення прапорця в пам'яті
  public evaluate(flagKey: string, ctx: EvaluationContext): EvaluationResult {
    const flag = this.ruleset.get(flagKey);
    if (!flag) {
      return { value: false, reason: "FLAG_NOT_FOUND" };
    }

    // 1. Індивідуальний Whitelist
    if (flag.whitelistUsers.includes(ctx.targetingKey)) {
      return { value: true, reason: "OVERRIDE" };
    }

    // 2. Правила атрибутів
    if (ctx.attributes) {
      for (const rule of flag.rules) {
        const actualValue = ctx.attributes[rule.attributeName];
        if (actualValue !== undefined && actualValue === rule.expectedValue) {
          return { value: rule.enabledValue, reason: "RULE_MATCH" };
        }
      }
    }

    // 3. Відсоткове розважування через хеш
    if (flag.rolloutPercentage > 0 && ctx.targetingKey) {
      const hashInput = `${flagKey}:${ctx.targetingKey}`;
      const hashBuffer = crypto.createHash("md5").update(hashInput).digest();
      const hashInt = hashBuffer.readUInt32BE(0);
      const bucket = hashInt % 100;

      if (bucket < flag.rolloutPercentage) {
        return { value: true, reason: "PERCENTAGE_ROLLOUT" };
      }
    }

    // 4. Дефолтне значення
    return { value: flag.defaultValue, reason: "DEFAULT" };
  }

  // Атомарна підміна карти правил
  public updateRules(newFlags: FlagDefinition[]): void {
    const nextMap = new Map<string, FlagDefinition>();
    for (const f of newFlags) {
      nextMap.set(f.key, f);
    }
    this.ruleset = nextMap; // Атомарна заміна посилання на мапу у V8
  }
}
```
:::

## 6. Покроковий аналіз виконання та перевірка сценаріїв

Проаналізуємо, як рушій поводиться в різних операційних ситуаціях:

```cpp
int main() {
    FlagEngine engine;

    // Створюємо початковий набір правил для фічі нового оформлення замовлення
    auto initial_rules = std::make_shared<RuleSet>();
    
    FlagDefinition checkout_flag;
    checkout_flag.key = "new-checkout-v2";
    checkout_flag.default_value = false;
    checkout_flag.rollout_percentage = 20; // 20% звичайних користувачів
    checkout_flag.whitelist_users = { "beta_tester_42", "qa_lead" };
    checkout_flag.rules.push_back({ "country", "UA", true }); // 100% для користувачів з UA

    initial_rules->flags["new-checkout-v2"] = checkout_flag;
    engine.update_rules(initial_rules);

    // Сценарій 1: Тестувальник із Whitelist (примусове ввімкнення незалежно від правил)
    EvaluationContext beta_user{ "beta_tester_42", {} };
    auto r1 = engine.evaluate("new-checkout-v2", beta_user);
    std::cout << "Beta user: " << r1.value << " (" << r1.reason << ")\n";
    // Очікуваний вивід: Beta user: 1 (OVERRIDE)

    // Сценарій 2: Користувач з України (спрацьовує правило таргетингу за атрибутом)
    EvaluationContext ua_user{ "user_999", { {"country", std::string("UA")} } };
    auto r2 = engine.evaluate("new-checkout-v2", ua_user);
    std::cout << "UA user: " << r2.value << " (" << r2.reason << ")\n";
    // Очікуваний вивід: UA user: 1 (RULE_MATCH)

    // Сценарій 3: Звичайний користувач з Польщі (розрахунок хеш-бакета для 20% розкатки)
    EvaluationContext pl_user{ "user_1001", { {"country", std::string("PL")} } };
    auto r3 = engine.evaluate("new-checkout-v2", pl_user);
    std::cout << "PL user (20% rollout): " << r3.value << " (" << r3.reason << ")\n";

    // Сценарій 4: Аварійне вимкнення (Kill Switch) під час збою нової платіжки
    auto emergency_rules = std::make_shared<RuleSet>();
    checkout_flag.rollout_percentage = 0;
    checkout_flag.rules.clear();
    checkout_flag.whitelist_users.clear();
    emergency_rules->flags["new-checkout-v2"] = checkout_flag;

    // Атомарна підміна: миттєве скидання на нуль для всіх потоків без перезавантаження
    engine.update_rules(emergency_rules);
    auto r4 = engine.evaluate("new-checkout-v2", ua_user);
    std::cout << "After emergency rollback: " << r4.value << " (" << r4.reason << ")\n";
    // Очікуваний вивід: After emergency rollback: 0 (DEFAULT)

    return 0;
}
```

## 7. Пастки, крайові випадки та оптимізація продуктивності

Під час переведення рушія у високопродуктивне виробниче середовище інженер стикається з низкою неочевидних проблем:

### 1. Управління пам'яттю та бар'єри пам'яті (Memory Ordering)
Використання звичайного присвоєння вказівника без бар'єрів пам'яті є поведінкою невизначеною (*Undefined Behavior*). Сучасні багатоядерні процесори (x86, ARM64) можуть переставляти операції запису в пам'ять. Якщо потік запису оновить адресу вказівника до того, як усі поля структури `RuleSet` будуть записані з кешу в оперативну пам'ять, читаючий потік на іншому ядрі прочитає наполовину ініціалізований об'єкт і впаде з помилкою сегментації (*Segmentation Fault*).

Семантика `std::memory_order_release` на записі та `std::memory_order_acquire` на читанні гарантує строгий бар'єр пам'яті: усі зміни полів об'єкта `RuleSet` стають видимими для читача до того, як він отримає оновлений вказівник.

### 2. Усунення алокацій у гарячому шляху
У наведеній реалізації конкатенація рядків `std::string hash_input = std::string(flag_key) + ":" + ctx.targeting_key` створює тимчасовий рядок на купі (*heap allocation*). При 100 000 викликів на секунду це перевантажує аллокатор `glibc / tcmalloc` і призводить до фрагментації пам'яті.

Професійна оптимізація полягає у використанні стекового буфера або прямому поточному згодовуванні шматків пам'яті в стан MurmurHash3:

```cpp
// Інкрементальне хешування без створення проміжних рядків
uint32_t hash_streaming(std::string_view flag, std::string_view user) {
    // Обчислення хешу без жодної алокації динамічної пам'яті
    char buffer[256];
    if (flag.size() + 1 + user.size() < sizeof(buffer)) {
        std::memcpy(buffer, flag.data(), flag.size());
        buffer[flag.size()] = ':';
        std::memcpy(buffer + flag.size() + 1, user.data(), user.size());
        return murmur3_32(std::string_view(buffer, flag.size() + 1 + user.size()));
    }
    return murmur3_32(std::string(flag) + ":" + std::string(user));
}
```

### 3. Поведінка при відсутності ідентифікатора (Anonymous Traffic)
Якщо запит прийшов від неавтентифікованого користувача і поле `targeting_key` порожнє, алгоритм відсоткової розкатки не має права повертати однакове значення для всіх анонімних запитів (інакше 100% анонімів випадково потраплять або не потраплять в одну когорту).

При порожньому ключі рушій повинен:
* Або згенерувати тимчасовий випадковий UUID сесії (збережений у cookie клієнта) і використати його як `targeting_key`;
* Або негайно повернути значення за замовчуванням `DEFAULT` з причиною `ANONYMOUS_FALLBACK`.

### 4. Запобігання витокам пам'яті при частих оновленнях конфігурації
Якщо сервер отримує оновлення конфігурації кожні 2 секунди, а довгоживучий фоновий запит утримує копію старого `shared_ptr<RuleSet>` протягом 30 секунд, у пам'яті одночасно можуть накопичуватися 15 проміжних версій правил.

Для запобігання витокам пам'яті обчислення прапорця повинно локалізувати час життя `shared_ptr` лише всередині функції `evaluate()`: потік захоплює посилання, миттєво обчислює булевий результат і скидає `shared_ptr`, не зберігаючи його в довгоживучих контекстах запиту.

### 5. Інтеграція з телеметрією та метриками
Кожне обчислення прапорця є подією аудиту. Для забезпечення спостережності рушій реєструє лічильники в Prometheus або StatsD у неблокуючий спосіб:
* `flags_evaluation_total{flag="new-checkout-v2", variant="true", reason="PERCENTAGE_ROLLOUT"}` — дозволяє в реальному часі бачити точний відсоток трафіку, що йде новою гілкою.
* `flags_evaluation_errors_total{flag="...", error="FLAG_NOT_FOUND"}` — фіксує випадки звернення до видалених або помилково названих прапорців.

Завдяки поєднанню атомарної заміни вказівника, детермінованого бакетування без виділень пам'яті та чіткого конвеєра пріоритетів, рушій забезпечує надійність промислового рівня для критичних навантажень.
