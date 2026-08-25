# ⚙️ Програмна реалізація рушія узгодження стану та детекції дрейфу

Автономний кінцевий вузол або розподілений мікросервіс повинен постійно утримувати свій локальний фізичний чи віртуальний стан у повній відповідності до цільової специфікації, незважаючи на збої мережі, затримки доставки повідомлень та раптові локальні збурення. У цьому проекті наведено робочу реалізацію рушія узгодження (Reconciliation Engine) мовами C та C++, яка реалізує детекцію дрейфу, обчислення дельти, оптимістичне блокування версій, експоненційний відкат із джитером та захист актуаторів від осциляцій.

## Архітектура та структура даних

Рушій узгодження працює за моделлю замкненого циклу зворотного зв'язку (Closed-Loop Feedback Controller). Внутрішній стан системи розділений на три ізольовані структури даних:
1. **Desired State (Бажаний стан):** цільова конфігурація та параметри, отримані з шини керування або хмарного сховища. Задається зовнішніми клієнтами, планувальниками завдань або оператором.
2. **Reported State (Звітований стан):** телеметричні значення, зчитані безпосередньо з локальних сенсорів, регістрів мікроконтролера або системних драйверів. Відображає фізичну реальність об'єкта.
3. **Reconciliation Controller (Контролер узгодження):** незалежний процес або потік виконання, який порівнює `desired` і `reported`, виявляє дрейф (drift detection), формує впорядкований список коригувальних дій та ідемпотентно керує апаратними актуаторами.

Реалізація мовою C розрахована на роботу в умовах жорстких обмежень пам'яті (вбудовані системи, RTOS, bare-metal контролери) і свідомо уникає динамічного виділення пам'яті (`malloc`/`free`) під час роботи циклу, використовуючи статично розміщені буфери фіксованого розміру. Реалізація мовою C++ використовує сучасні ідіоми C++20: типізовані варіанти `std::variant`, безпечну обробку помилок через `std::expected`, асоціативні таблиці та строгі гарантії виняткобезпеки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define MAX_ENTRIES 16
#define MAX_KEY_LEN 32

/* Статус результату операції */
typedef enum {
    RECON_OK = 0,
    RECON_NO_DRIFT = 1,
    RECON_VERSION_CONFLICT = 2,
    RECON_ACTUATION_FAILED = 3,
    RECON_RATE_LIMITED = 4
} ReconStatus;

/* Типи значень у сховищі стану */
typedef enum {
    VAL_TYPE_INT,
    VAL_TYPE_DOUBLE,
    VAL_TYPE_BOOL
} ValueType;

/* Універсальний елемент стану */
typedef struct {
    char key[MAX_KEY_LEN];
    ValueType type;
    union {
        int64_t i_val;
        double  d_val;
        bool    b_val;
    } as;
    bool is_null; /* Tombstone (видалення) */
} StateProperty;

/* Документ стану вузла */
typedef struct {
    StateProperty properties[MAX_ENTRIES];
    size_t count;
    uint64_t version;
    uint64_t timestamp_sec;
} StateDocument;

/* Дельта-запис розбіжності */
typedef struct {
    char key[MAX_KEY_LEN];
    StateProperty desired_val;
    StateProperty reported_val;
    bool requires_action;
} DriftItem;

/* Конфігурація відкату та захисту */
typedef struct {
    uint32_t base_backoff_ms;
    uint32_t max_backoff_ms;
    uint32_t current_attempt;
    double   analog_deadband; /* Зона нечутливості */
} ReconcilerPolicy;

/* Ініціалізація документа стану */
void state_doc_init(StateDocument* doc, uint64_t version) {
    doc->count = 0;
    doc->version = version;
    doc->timestamp_sec = (uint64_t)time(NULL);
}

/* Додавання або оновлення властивості */
void state_doc_set_double(StateDocument* doc, const char* key, double val) {
    for (size_t i = 0; i < doc->count; ++i) {
        if (strncmp(doc->properties[i].key, key, MAX_KEY_LEN) == 0) {
            doc->properties[i].type = VAL_TYPE_DOUBLE;
            doc->properties[i].as.d_val = val;
            doc->properties[i].is_null = false;
            return;
        }
    }
    if (doc->count < MAX_ENTRIES) {
        strncpy(doc->properties[doc->count].key, key, MAX_KEY_LEN - 1);
        doc->properties[doc->count].type = VAL_TYPE_DOUBLE;
        doc->properties[doc->count].as.d_val = val;
        doc->properties[doc->count].is_null = false;
        doc->count++;
    }
}

/* Обчислення експоненційного відкату з повним випадковим джитером (Full Jitter) */
uint32_t calculate_backoff_with_jitter(ReconcilerPolicy* policy) {
    uint32_t exp_limit = (uint32_t)pow(2.0, (double)policy->current_attempt) * policy->base_backoff_ms;
    if (exp_limit > policy->max_backoff_ms) {
        exp_limit = policy->max_backoff_ms;
    }
    if (exp_limit == 0) return 0;
    /* Full Jitter: випадкове число в діапазоні [0, exp_limit] */
    uint32_t jittered = (uint32_t)(rand() % exp_limit);
    return jittered;
}

/* Обчислення дрейфу між бажаним та звітованим станами */
size_t detect_drift(const StateDocument* desired,
                    const StateDocument* reported,
                    const ReconcilerPolicy* policy,
                    DriftItem* out_drifts,
                    size_t max_drifts) {
    size_t drift_count = 0;

    for (size_t i = 0; i < desired->count && drift_count < max_drifts; ++i) {
        const StateProperty* d_prop = &desired->properties[i];
        const StateProperty* r_prop = NULL;

        /* Пошук відповідної властивості у звітованому стані */
        for (size_t j = 0; j < reported->count; ++j) {
            if (strncmp(reported->properties[j].key, d_prop->key, MAX_KEY_LEN) == 0) {
                r_prop = &reported->properties[j];
                break;
            }
        }

        /* Випадок 1: Властивість відсутня у звіті */
        if (!r_prop) {
            strncpy(out_drifts[drift_count].key, d_prop->key, MAX_KEY_LEN - 1);
            out_drifts[drift_count].desired_val = *d_prop;
            out_drifts[drift_count].reported_val.is_null = true;
            out_drifts[drift_count].requires_action = true;
            drift_count++;
            continue;
        }

        /* Випадок 2: Порівняння значень з урахуванням зони нечутливості */
        if (d_prop->type == VAL_TYPE_DOUBLE && r_prop->type == VAL_TYPE_DOUBLE) {
            double diff = fabs(d_prop->as.d_val - r_prop->as.d_val);
            if (diff > policy->analog_deadband) {
                strncpy(out_drifts[drift_count].key, d_prop->key, MAX_KEY_LEN - 1);
                out_drifts[drift_count].desired_val = *d_prop;
                out_drifts[drift_count].reported_val = *r_prop;
                out_drifts[drift_count].requires_action = true;
                drift_count++;
            }
        }
    }
    return drift_count;
}

/* Імітація апаратного актуатора */
bool apply_hardware_actuation(const char* key, double target_val) {
    /* Безпечне встановлення фізичного значення в апаратуру */
    printf("  [Актуватор C] Застосування %s -> %.2f\n", key, target_val);
    return true;
}

/* Основний цикл узгодження (Reconciliation Loop Step) */
ReconStatus reconcile_step(const StateDocument* desired,
                          StateDocument* reported,
                          ReconcilerPolicy* policy,
                          uint64_t expected_version) {
    /* Крок 1: Перевірка оптимістичного блокування */
    if (desired->version < expected_version) {
        printf("  [Помилка C] Застаріла версія бажаного стану: %llu < %llu\n",
               (unsigned long long)desired->version,
               (unsigned long long)expected_version);
        return RECON_VERSION_CONFLICT;
    }

    /* Крок 2: Виявлення дрейфу */
    DriftItem drifts[MAX_ENTRIES];
    size_t num_drifts = detect_drift(desired, reported, policy, drifts, MAX_ENTRIES);

    if (num_drifts == 0) {
        policy->current_attempt = 0;
        return RECON_NO_DRIFT;
    }

    printf("  [Дрейф C] Знайдено розбіжностей: %zu. Початок узгодження...\n", num_drifts);

    /* Крок 3: Застосування дій до актуаторів */
    for (size_t i = 0; i < num_drifts; ++i) {
        if (drifts[i].requires_action) {
            bool ok = apply_hardware_actuation(drifts[i].key, drifts[i].desired_val.as.d_val);
            if (!ok) {
                policy->current_attempt++;
                uint32_t backoff = calculate_backoff_with_jitter(policy);
                printf("  [Збій C] Актуація не вдалася, повтор через %u мс\n", backoff);
                return RECON_ACTUATION_FAILED;
            }
            /* Оновлення локального звітованого стану */
            state_doc_set_double(reported, drifts[i].key, drifts[i].desired_val.as.d_val);
        }
    }

    /* Крок 4: Фіксація звіту та інкремент версії */
    reported->version = desired->version;
    reported->timestamp_sec = (uint64_t)time(NULL);
    policy->current_attempt = 0;
    return RECON_OK;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <variant>
#include <optional>
#include <expected>
#include <chrono>
#include <random>
#include <cmath>

namespace edge::reconciler {

enum class ErrorCode {
    VersionConflict,
    ActuationFailed,
    RateLimited,
    InvalidPayload
};

using PropertyValue = std::variant<std::monostate, int64_t, double, bool, std::string>;

struct StateDocument {
    std::unordered_map<std::string, PropertyValue> properties;
    uint64_t version{0};
    std::chrono::system_clock::time_point timestamp{std::chrono::system_clock::now()};

    [[nodiscard]] std::optional<PropertyValue> get(std::string_view key) const {
        auto it = properties.find(std::string(key));
        if (it != properties.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void set(std::string_view key, PropertyValue val) {
        properties[std::string(key)] = std::move(val);
        timestamp = std::chrono::system_clock::now();
    }
};

struct DriftRecord {
    std::string key;
    PropertyValue desired;
    PropertyValue reported;
};

class ReconcilerEngine {
public:
    struct Policy {
        std::chrono::milliseconds base_backoff{50};
        std::chrono::milliseconds max_backoff{5000};
        double analog_deadband{0.2}; /* Гістерезис 0.2 одиниці */
        uint32_t current_attempt{0};
    };

    explicit ReconcilerEngine(Policy policy) 
        : policy_(policy), rng_(std::random_device{}()) {}

    [[nodiscard]] std::vector<DriftRecord> compute_drift(
        const StateDocument& desired,
        const StateDocument& reported) const 
    {
        std::vector<DriftRecord> drifts;

        for (const auto& [key, d_val] : desired.properties) {
            auto r_opt = reported.get(key);
            if (!r_opt.has_value()) {
                drifts.push_back({key, d_val, std::monostate{}});
                continue;
            }

            const auto& r_val = *r_opt;
            if (std::holds_alternative<double>(d_val) && std::holds_alternative<double>(r_val)) {
                double diff = std::abs(std::get<double>(d_val) - std::get<double>(r_val));
                if (diff > policy_.analog_deadband) {
                    drifts.push_back({key, d_val, r_val});
                }
            } else if (d_val != r_val) {
                drifts.push_back({key, d_val, r_val});
            }
        }
        return drifts;
    }

    std::expected<bool, ErrorCode> reconcile(
        const StateDocument& desired,
        StateDocument& reported,
        uint64_t expected_version) 
    {
        /* Оптимістична перевірка колізій */
        if (desired.version < expected_version) {
            return std::unexpected(ErrorCode::VersionConflict);
        }

        auto drifts = compute_drift(desired, reported);
        if (drifts.empty()) {
            policy_.current_attempt = 0;
            return false; /* Дрейфу немає, система у спокої */
        }

        std::cout << "  [Дрейф C++] Виявлено розбіжностей: " << drifts.size() << '\n';

        for (const auto& drift : drifts) {
            if (!actuate_hardware(drift.key, drift.desired)) {
                policy_.current_attempt++;
                auto wait_time = calculate_backoff();
                std::cout << "  [Збій C++] Помилка актуатора " << drift.key 
                          << ", відкат на " << wait_time.count() << " мс\n";
                return std::unexpected(ErrorCode::ActuationFailed);
            }
            /* Фіксація нового стану локально */
            reported.set(drift.key, drift.desired);
        }

        reported.version = desired.version;
        policy_.current_attempt = 0;
        return true; /* Успішно узгоджено */
    }

private:
    Policy policy_;
    mutable std::mt19937 rng_;

    [[nodiscard]] std::chrono::milliseconds calculate_backoff() const {
        uint64_t multiplier = 1ULL << std::min(policy_.current_attempt, 10U);
        auto raw_limit = policy_.base_backoff * multiplier;
        auto capped = std::min(raw_limit, policy_.max_backoff);
        
        std::uniform_int_distribution<uint64_t> dist(0, capped.count());
        return std::chrono::milliseconds(dist(rng_));
    }

    [[nodiscard]] bool actuate_hardware(const std::string& key, const PropertyValue& val) const {
        std::cout << "  [Актуватор C++] Встановлення параметра " << key << '\n';
        return true;
    }
};

} // namespace edge::reconciler
```
:::

## Детальний розбір механізмів та обробка крайових випадків

Програмна модель циклу узгодження розв'язує комплекс інженерних проблем, що виникають при взаємодії програмного коду з неідеальним фізичним світом та ненадійними каналами передачі даних:

### 1. Зона нечутливості та захист від осциляцій (Analog Deadband)
При зчитуванні фізичних параметрів (температура повітря, оберти двигуна, тиск у магістралі) датчики повертають неперервні дійсні числа. Через тепловий шум, наведення на АЦП та квантування останніх бітів значення постійно коливається (наприклад, між `21.98°C` та `22.02°C`). Якщо алгоритм детекції дрейфу здійснює пряме порівняння `desired == reported`, контролер буде генерувати нескінченний потік мікрокоманд до актуатора.

Це явище називається **флапінгом** (flapping) або **осциляцією стану**. Воно призводить до катастрофічного зносу механічних реле, сервоприводів та перегріву силових ключів. Впровадження параметру `analog_deadband` створює зону гістерезису: дрейф фіксується лише тоді, коли абсолютна різниця перевищує заданий поріг чутливості (`|D - R| > ε`).

### 2. Частковий прогрес та збереження проміжних результатів (Partial Progress Commits)
У розподіленій системі документ бажаного стану може містити оновлення одразу кількох незалежних підсистем (наприклад, увімкнення підсвічування, відкриття клапана та зміна швидкості вентилятора). Якщо під час виконання серії дій відкриття клапана завершилося апаратною помилкою (таймаут шини I2C або блокування штока), контролер не повинен скасовувати вже виконане увімкнення підсвічування.

Рушій фіксує успішно застосовані параметри в локальний `reported` стан негайно після кожної успішної дії. При наступній ітерації циклу узгодження контролер виявить дельту лише для несправного клапана, не виконуючи повторних дій над уже налаштованим підсвічуванням. Це забезпечує строгу **ідемпотентність** на рівні окремих полів.

### 3. Математика експоненційного відкату з випадковим джитером (Full Jitter)
Коли актуатор тимчасово недоступний або шина передачі даних перебуває під навантаженням, сліпі повторні спроби (busy retry) призводять до вичерпання процесорного часу та перегріву системи. Експоненційний відкат збільшує інтервал очікування у два рази після кожної невдалої спроби:

```
t_exp = min(t_max, t_base · 2^attempt)
```

Однак якщо в парку пристроїв трапляється масштабний мережевий збій (наприклад, перезавантаження центрального маршрутизатора), тисячі контролерів синхронізують свої таймери спроб і атакують брокер повідомлень одночасно у фазі `t_exp`. Для руйнування фазової синхронізації застосовується алгоритм **Full Jitter**: фактичний час затримки обирається як рівномірно розподілене випадкове число від `0` до `t_exp`:

```
t_sleep = random(0, t_exp)
```

Це рівномірно розмазує навантаження на систему керування у часі та запобігає виникненню шторму узгодження (Thundering Herd Problem).

### 4. Обробка надгробків (Tombstone Handling) та видалення ключів
У реальних протоколах синхронізації (наприклад, AWS IoT Device Shadow або Kubernetes API) видалення параметра з конфігурації позначається явним записом значення `null` у бажаний стан: `{"filter_alert": null}`.

Коли контролер детекції дрейфу зустрічає надгробок (`is_null == true` або `std::monostate`), він зобов'язаний:
1. Викликати специфічний деструктор або метод скидання апаратного ресурсу (наприклад, скинути аварійний тригер, вимкнути додатковий нагрівач і повернути регістр до безпечного заводського стану).
2. Видалити відповідний ключ зі свого локального `reported` сховища або позначити його як відсутній.
3. Опублікувати підтвердження у звіті, щоб серверне сховище стану також остаточно видалило дану властивість із загального документа цифрового двійника.

### 5. Потокова безпека та синхронізація (Thread Safety & Concurrency)
У багатопотокових вбудованих додатках мережевий стек MQTT/HTTP працює в окремому низькопріоритетному потоці введення-виведення, тоді як цикл узгодження виконується у високопріоритетному керуючому циклі реального часу. Прямий доступ до структури `StateDocument` без синхронізації спричиняє гонку даних (Data Race) і спотворення покажчиків.

Для забезпечення безпеки застосовуються дві стратегії:
- **У середовищах C (Embedded/RTOS):** подвійна буферизація (Double Buffering) зі статичними м'ютексами або lock-free кільцевим буфером команд для передачі ревізій без блокування апаратних переривань.
- **У середовищах C++20:** використання семантики незмінних знімків стану з атомарною підміною покажчика (`std::atomic<std::shared_ptr<const StateDocument>>`), що дозволяє контролеру читати незмінний знімок без блокування мережевого потоку під час прийому нових пакетів.
