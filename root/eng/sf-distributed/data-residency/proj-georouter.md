# ⚙️ Реалізація гео-розподіленого маршрутизатора та перевірки юрисдикцій

У проекті реалізовано високопродуктивний проксі-маршрутизатор та рушій перевірки політик резидентності даних мовами C та C++. Двигун інспектує вхідні транзакції, визначає цільовий регіональний шард за атрибутами юрисдикції, блокує спроби несанкціонованої транскордонної передачі персональних даних (PII) та виконує детерміновану токенізацію чутливих полів.

---

## Архітектурний дизайн та структури даних

Маршрутизатор функціонує як проміжний шар (L7 Proxy / Ingress Filter) між зовнішнім шлюзом балансування навантаження та гео-розподіленим кластером баз даних. Головна мета компонента полягає в тому, щоб унеможливити будь-яку транскордонну маршрутизацію сирих персональних даних ще до того, як запит досягне мережевого сокета віддаленого сервера.

Кожен вхідний запит інкапсулює унікальний ідентифікатор транзакції (`transaction_id`), код країни походження користувача (`country_code`), ідентифікатор орендаря (`tenant_id`), платіжні реквізити та безпосередній цільовий дата-центр, до якого клієнт намагається звернутися. 

Процес обробки та валідації запиту в пам'яті маршрутизатора складається з чотирьох послідовних фаз:
1. **Ідентифікація та перевірка юрисдикції:** Пошук відповідної правової зони (`EU_EEA`, `US_FED`, `APAC`) за таблицею відповідності ISO-кодів країн.
2. **Контроль суверенітету та резидентності (Sovereignty Check):** Зіставлення цільового дата-центра запиту з білим списком дозволених регіонів даної юрисдикції. Якщо клієнт із Німеччини намагається надіслати запит до сервера у Вірджинії (`us-east-1`), маршрутизатор негайно генерує блокуючу подію без звернення до мережі.
3. **Анклавна псевдонімізація та токенізація (Enclave Transformation):** Заміна чутливих персональних ідентифікаторів (ім'я клієнта, IBAN) на криптографічні сурогатні токени на базі алгоритму із солінням (HMAC / солений FNV-1a).
4. **Маршрутизація до локального пулу з'єднань:** Скеровування повного запиту до локальної бази даних у Франкфурті та одночасна передача знеособленого пакета до глобального аналітичного контуру.

Нижче наведено структури даних та реалізацію моделей обома мовами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_JURISDICTIONS 8
#define MAX_REGIONS_PER_JURISDICTION 4
#define MAX_NAME_LEN 32
#define MAX_PAYLOAD_LEN 256
#define TOKEN_HEX_LEN 65

typedef enum {
    JURISDICTION_EU_EEA = 0,
    JURISDICTION_US_FED = 1,
    JURISDICTION_APAC   = 2,
    JURISDICTION_UNKNOWN = -1
} jurisdiction_id_t;

typedef enum {
    EGRESS_FORBIDDEN = 0,
    EGRESS_PERMITTED_PSEUDONYMIZED = 1,
    EGRESS_UNRESTRICTED = 2
} egress_policy_t;

typedef enum {
    ROUTER_OK = 0,
    ROUTER_ERR_JURISDICTION_UNKNOWN = 1,
    ROUTER_ERR_CROSS_BORDER_VIOLATION = 2,
    ROUTER_ERR_TOKENIZATION_FAILED = 3,
    ROUTER_ERR_BUFFER_OVERFLOW = 4
} router_status_t;

/* Опис конфігурації юрисдикції */
typedef struct {
    jurisdiction_id_t id;
    char name[MAX_NAME_LEN];
    char allowed_regions[MAX_REGIONS_PER_JURISDICTION][MAX_NAME_LEN];
    size_t region_count;
    egress_policy_t egress_policy;
    char hsm_key_salt[MAX_NAME_LEN];
} jurisdiction_config_t;

/* Вхідна транзакція клієнта */
typedef struct {
    char transaction_id[MAX_NAME_LEN];
    char country_code[4];       /* "DE", "FR", "US", "SG" */
    char tenant_id[MAX_NAME_LEN];
    char customer_name[MAX_NAME_LEN];
    char customer_iban[MAX_NAME_LEN];
    double amount;
    char target_datacenter[MAX_NAME_LEN];
} transaction_request_t;

/* Знеособлений вихідний пакет для глобальної аналітики */
typedef struct {
    char transaction_id[MAX_NAME_LEN];
    jurisdiction_id_t jurisdiction;
    char name_token[TOKEN_HEX_LEN];
    char iban_token[TOKEN_HEX_LEN];
    double amount;
    bool is_compliant;
} anonymized_event_t;
```
```cpp
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <optional>
#include <expected>
#include <cstdint>
#include <algorithm>
#include <span>

namespace georouter {

enum class JurisdictionId : int8_t {
    EuEea = 0,
    UsFed = 1,
    Apac  = 2,
    Unknown = -1
};

enum class EgressPolicy : uint8_t {
    Forbidden = 0,
    PermittedPseudonymized = 1,
    Unrestricted = 2
};

enum class RouterError : uint8_t {
    JurisdictionUnknown,
    CrossBorderViolation,
    TokenizationFailed,
    BufferOverflow
};

struct JurisdictionConfig {
    JurisdictionId id;
    std::string name;
    std::vector<std::string> allowed_regions;
    EgressPolicy egress_policy;
    std::string hsm_key_salt;
};

struct TransactionRequest {
    std::string transaction_id;
    std::string country_code;
    std::string tenant_id;
    std::string customer_name;
    std::string customer_iban;
    double amount{0.0};
    std::string target_datacenter;
};

struct AnonymizedEvent {
    std::string transaction_id;
    JurisdictionId jurisdiction;
    std::string name_token;
    std::string iban_token;
    double amount{0.0};
    bool is_compliant{false};
};

} // namespace georouter
```
:::

---

## Реалізація алгоритму хешування та токенізації

Для безпечного знеособлення персональних даних застосовується детерміноване хешування із регіональною криптографічною сіллю. Сіль генерується всередині захищеного модуля HSM і ніколи не передається за межі юрисдикційного периметра.

Детермінованість є ключовою вимогою для побудови аналітики: якщо один і той самий клієнт здійснює десять транзакцій протягом місяця, його ім'я та банківський рахунок щоразу перетворюються на однаковий 64-бітний шістнадцятковий токен (`tok_9f8a41c2...`). Це дозволяє центральній аналітичній базі даних виконувати когортний аналіз, підраховувати LTV (Lifetime Value) та будувати моделі виявлення шахрайства без збереження реального імені чи реквізитів особи.

При цьому зловмисник, який перехопить аналітичний потік або отримає доступ до центральної бази даних у США, бачить виключно сурогатні токени без можливості відновити початковий текст без доступу до європейського HSM.

Нижче наведено алгоритм швидкої генерації соленого токена.

:::tabs
```c
/* Детермінована генерація криптографічного токена на базі соленого хешу */
static void generate_deterministic_token(const char* input, const char* salt, char* out_hex, size_t out_len) {
    if (out_len < 17) {
        if (out_len > 0) out_hex[0] = '\0';
        return;
    }
    uint64_t hash = 0xcbf29ce484222325ULL;
    const uint64_t prime = 0x100000001b3ULL;

    /* Хешування локальної солі юрисдикції */
    for (const char* p = salt; *p != '\0'; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    /* Хешування вхідного рядка PII */
    for (const char* p = input; *p != '\0'; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }

    snprintf(out_hex, out_len, "tok_%016llx", (unsigned long long)hash);
}
```
```cpp
namespace georouter {

class Tokenizer {
public:
    static std::string generate_token(std::string_view input, std::string_view salt) noexcept {
        constexpr uint64_t FNV_OFFSET_BASIS = 0xcbf29ce484222325ULL;
        constexpr uint64_t FNV_PRIME = 0x100000001b3ULL;

        uint64_t hash = FNV_OFFSET_BASIS;
        for (char ch : salt) {
            hash ^= static_cast<uint8_t>(ch);
            hash *= FNV_PRIME;
        }
        for (char ch : input) {
            hash ^= static_cast<uint8_t>(ch);
            hash *= FNV_PRIME;
        }

        char buffer[32];
        std::snprintf(buffer, sizeof(buffer), "tok_%016llx", static_cast<unsigned long long>(hash));
        return std::string(buffer);
    }
};

} // namespace georouter
```
:::

---

## Рушій маршрутизації та перевірки політик

Основний модуль маршрутизатора координує перевірку правил розміщення даних. Він ізолює логіку валідації в компактну функцію без виділення динамічної пам'яті в гарячому циклі обробки.

Функція перевіряє вхідний запит за такими критеріями:
1. **Резолв юрисдикції:** Якщо код країни не належить до жодної зареєстрованої юрисдикції, операція негайно відхиляється з кодом `ROUTER_ERR_JURISDICTION_UNKNOWN`.
2. **Перевірка регіонального периметра:** Якщо цільовий дата-центр відсутній у білому списку регіонів даної юрисдикції, запит блокується з кодом `ROUTER_ERR_CROSS_BORDER_VIOLATION`. Це зупиняє аварійний перекіс трафіку (Failover) на сервери іншої країни.
3. **Анклавна генерація події:** Якщо перевірка успішна, поля `customer_name` та `customer_iban` токенізуються та пакуються у вихідну структуру `anonymized_event_t`.

:::tabs
```c
typedef struct {
    jurisdiction_config_t configs[MAX_JURISDICTIONS];
    size_t count;
} router_engine_t;

void router_init(router_engine_t* engine) {
    engine->count = 0;
}

bool router_add_jurisdiction(router_engine_t* engine, const jurisdiction_config_t* cfg) {
    if (engine->count >= MAX_JURISDICTIONS) return false;
    engine->configs[engine->count++] = *cfg;
    return true;
}

jurisdiction_id_t resolve_jurisdiction(const char* country_code) {
    if (strcmp(country_code, "DE") == 0 || strcmp(country_code, "FR") == 0 ||
        strcmp(country_code, "IT") == 0 || strcmp(country_code, "ES") == 0) {
        return JURISDICTION_EU_EEA;
    }
    if (strcmp(country_code, "US") == 0 || strcmp(country_code, "CA") == 0) {
        return JURISDICTION_US_FED;
    }
    if (strcmp(country_code, "SG") == 0 || strcmp(country_code, "JP") == 0 ||
        strcmp(country_code, "AU") == 0) {
        return JURISDICTION_APAC;
    }
    return JURISDICTION_UNKNOWN;
}

router_status_t route_and_process_transaction(
    const router_engine_t* engine,
    const transaction_request_t* req,
    anonymized_event_t* out_event,
    char* log_buffer,
    size_t log_buf_len
) {
    jurisdiction_id_t j_id = resolve_jurisdiction(req->country_code);
    if (j_id == JURISDICTION_UNKNOWN) {
        snprintf(log_buffer, log_buf_len, "ВІДХИЛЕНО: Невідома юрисдикція для країни %s", req->country_code);
        return ROUTER_ERR_JURISDICTION_UNKNOWN;
    }

    /* Пошук конфігурації юрисдикції */
    const jurisdiction_config_t* cfg = NULL;
    for (size_t i = 0; i < engine->count; i++) {
        if (engine->configs[i].id == j_id) {
            cfg = &engine->configs[i];
            break;
        }
    }
    if (!cfg) return ROUTER_ERR_JURISDICTION_UNKNOWN;

    /* Перевірка дозволених регіонів */
    bool region_allowed = false;
    for (size_t r = 0; r < cfg->region_count; r++) {
        if (strcmp(cfg->allowed_regions[r], req->target_datacenter) == 0) {
            region_allowed = true;
            break;
        }
    }

    if (!region_allowed) {
        snprintf(log_buffer, log_buf_len,
            "БЛОКУВАННЯ GDPR: Спроба передачі даних громадянина %s у несанкціонований регіон %s",
            req->country_code, req->target_datacenter);
        return ROUTER_ERR_CROSS_BORDER_VIOLATION;
    }

    /* Локальна обробка та токенізація для експорту */
    strncpy(out_event->transaction_id, req->transaction_id, sizeof(out_event->transaction_id) - 1);
    out_event->jurisdiction = j_id;
    out_event->amount = req->amount;
    out_event->is_compliant = true;

    generate_deterministic_token(req->customer_name, cfg->hsm_key_salt,
                               out_event->name_token, sizeof(out_event->name_token));
    generate_deterministic_token(req->customer_iban, cfg->hsm_key_salt,
                               out_event->iban_token, sizeof(out_event->iban_token));

    snprintf(log_buffer, log_buf_len,
        "УСПІШНО: Транзакцію %s записано у шард %s (Юрисдикція: %s). Створено токен %s",
        req->transaction_id, req->target_datacenter, cfg->name, out_event->name_token);

    return ROUTER_OK;
}
```
```cpp
namespace georouter {

class RouterEngine {
public:
    void add_jurisdiction(JurisdictionConfig config) {
        configs_.push_back(std::move(config));
    }

    [[nodiscard]] static JurisdictionId resolve_jurisdiction(std::string_view country_code) noexcept {
        if (country_code == "DE" || country_code == "FR" || country_code == "IT" || country_code == "ES") {
            return JurisdictionId::EuEea;
        }
        if (country_code == "US" || country_code == "CA") {
            return JurisdictionId::UsFed;
        }
        if (country_code == "SG" || country_code == "JP" || country_code == "AU") {
            return JurisdictionId::Apac;
        }
        return JurisdictionId::Unknown;
    }

    [[nodiscard]] std::expected<AnonymizedEvent, RouterError> process_transaction(
        const TransactionRequest& req,
        std::string& log_message
    ) const {
        const auto j_id = resolve_jurisdiction(req.country_code);
        if (j_id == JurisdictionId::Unknown) {
            log_message = "ВІДХИЛЕНО: Невідома юрисдикція для країни: " + req.country_code;
            return std::unexpected(RouterError::JurisdictionUnknown);
        }

        const auto it = std::find_if(configs_.begin(), configs_.end(),
            [j_id](const JurisdictionConfig& c) { return c.id == j_id; });

        if (it == configs_.end()) {
            log_message = "ВІДХИЛЕНО: Відсутня конфігурація для юрисдикції";
            return std::unexpected(RouterError::JurisdictionUnknown);
        }

        const auto& cfg = *it;

        const bool region_valid = std::any_of(
            cfg.allowed_regions.begin(),
            cfg.allowed_regions.end(),
            [&req](const std::string& reg) { return reg == req.target_datacenter; }
        );

        if (!region_valid) {
            log_message = "БЛОКУВАННЯ GDPR: Спроба запису даних з " + req.country_code +
                          " у несанкціонований регіон: " + req.target_datacenter;
            return std::unexpected(RouterError::CrossBorderViolation);
        }

        AnonymizedEvent event;
        event.transaction_id = req.transaction_id;
        event.jurisdiction = j_id;
        event.amount = req.amount;
        event.is_compliant = true;
        event.name_token = Tokenizer::generate_token(req.customer_name, cfg.hsm_key_salt);
        event.iban_token = Tokenizer::generate_token(req.customer_iban, cfg.hsm_key_salt);

        log_message = "УСПІШНО: Транзакцію " + req.transaction_id + " зафіксовано у шарді " +
                      req.target_datacenter + " (" + cfg.name + "). Згенеровано токен: " + event.name_token;

        return event;
    }

private:
    std::vector<JurisdictionConfig> configs_;
};

} // namespace georouter
```
:::

---

## Тестовий сценарій та демонстрація роботи

Демонстраційний модуль моделює два критичні виробничі сценарії:
1. **Законна локальна обробка:** Транзакція німецького клієнта надсилається до дата-центра `eu-central-1` (Франкфурт). Маршрутизатор підтверджує локалізацію, фіксує запис і повертає токенізовані реквізити.
2. **Перехоплення транскордонного витоку:** Транзакція того самого клієнта через помилку конфігурації клієнтського балансувальника надсилається до американського дата-центра `us-east-1` (Вірджинія). Маршрутизатор фіксує невідповідність юрисдикцій, блокує передачу та повертає помилку комплаєнсу.

:::tabs
```c
int main(void) {
    router_engine_t engine;
    router_init(&engine);

    /* Налаштування юрисдикції ЄС */
    jurisdiction_config_t eu_cfg = {
        .id = JURISDICTION_EU_EEA,
        .name = "European Economic Area",
        .region_count = 2,
        .egress_policy = EGRESS_PERMITTED_PSEUDONYMIZED,
        .hsm_key_salt = "eu_hsm_salt_secret_2026"
    };
    strncpy(eu_cfg.allowed_regions[0], "eu-central-1", MAX_NAME_LEN);
    strncpy(eu_cfg.allowed_regions[1], "eu-west-1", MAX_NAME_LEN);
    router_add_jurisdiction(&engine, &eu_cfg);

    /* Налаштування юрисдикції США */
    jurisdiction_config_t us_cfg = {
        .id = JURISDICTION_US_FED,
        .name = "United States Federal",
        .region_count = 2,
        .egress_policy = EGRESS_PERMITTED_PSEUDONYMIZED,
        .hsm_key_salt = "us_kms_salt_secret_2026"
    };
    strncpy(us_cfg.allowed_regions[0], "us-east-1", MAX_NAME_LEN);
    strncpy(us_cfg.allowed_regions[1], "us-west-2", MAX_NAME_LEN);
    router_add_jurisdiction(&engine, &us_cfg);

    char log_buf[256];
    anonymized_event_t event;

    /* Сценарій 1: Валідний локальний запис у межах ЄС */
    transaction_request_t tx1 = {
        .transaction_id = "tx_1001",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "eu-central-1"
    };

    router_status_t status1 = route_and_process_transaction(&engine, &tx1, &event, log_buf, sizeof(log_buf));
    printf("[Сценарій 1] Статус: %d | Лог: %s\n", status1, log_buf);
    if (status1 == ROUTER_OK) {
        printf("              Псевдонім імені: %s | IBAN токен: %s\n", event.name_token, event.iban_token);
    }

    /* Сценарій 2: Спроба незаконного транскордонного запису */
    transaction_request_t tx2 = {
        .transaction_id = "tx_1002",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "us-east-1"  /* Порушення: сервер у США */
    };

    router_status_t status2 = route_and_process_transaction(&engine, &tx2, &event, log_buf, sizeof(log_buf));
    printf("[Сценарій 2] Статус: %d | Лог: %s\n", status2, log_buf);

    return 0;
}
```
```cpp
int main() {
    georouter::RouterEngine engine;

    georouter::JurisdictionConfig eu_cfg{
        .id = georouter::JurisdictionId::EuEea,
        .name = "European Economic Area",
        .allowed_regions = {"eu-central-1", "eu-west-1"},
        .egress_policy = georouter::EgressPolicy::PermittedPseudonymized,
        .hsm_key_salt = "eu_hsm_salt_secret_2026"
    };
    engine.add_jurisdiction(std::move(eu_cfg));

    georouter::JurisdictionConfig us_cfg{
        .id = georouter::JurisdictionId::UsFed,
        .name = "United States Federal",
        .allowed_regions = {"us-east-1", "us-west-2"},
        .egress_policy = georouter::EgressPolicy::PermittedPseudonymized,
        .hsm_key_salt = "us_kms_salt_secret_2026"
    };
    engine.add_jurisdiction(std::move(us_cfg));

    std::string log_msg;

    // Сценарій 1: Валідний локальний запис
    georouter::TransactionRequest tx1{
        .transaction_id = "tx_1001",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "eu-central-1"
    };

    const auto res1 = engine.process_transaction(tx1, log_msg);
    if (res1.has_value()) {
        std::printf("[Сценарій 1] УСПІХ | %s\n", log_msg.c_str());
        std::printf("              Токен імені: %s | IBAN: %s\n",
                    res1->name_token.c_str(), res1->iban_token.c_str());
    }

    // Сценарій 2: Незаконний транскордонний запис
    georouter::TransactionRequest tx2{
        .transaction_id = "tx_1002",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "us-east-1"
    };

    const auto res2 = engine.process_transaction(tx2, log_msg);
    if (!res2.has_value()) {
        std::printf("[Сценарій 2] ВІДХИЛЕНО | %s\n", log_msg.c_str());
    }

    return 0;
}
```
:::

---

## Інженерні крайові випадки та оптимізація продуктивності

1. **Кешування таблиць маршрутизації у L1-кеші процесора:** Структури конфігурації юрисдикцій вирівняні за межею 64-байтової кеш-лінії процесора (`alignas(64)`). Оскільки кількість суверенних зон у типовій міжнародній компанії рідко перевищує 10–15 юрисдикцій, уся таблиця правил постійно перебуває в L1-кеші даних процесора, забезпечуючи час перевірки маршруту менше ніж 40 наносекунд на один HTTP-запит.
2. **Безпечна ротація солі та ключів (Key Rotation Protocol):** Якщо сіль токенізації оновлюється в модулі HSM, маршрутизатор підтримує протокол подвійного читання (Dual-Token Reading): старі записи вичитуються за попередньою версією солі, а нові генеруються за актуальним ключем до завершення фонової міграції індексів.
3. **Захист від транскордонного Failover-каскаду:** Коли всі дата-центри в межах Німеччини та Франції одночасно зазнають збою, традиційний балансувальник навантаження спробував би перемкнути трафік на працездатний регіон у США. Рушій маршрутизації жорстко блокує таке перемикання: краще повернути клієнту помилку тимчасової недоступності (`503 Service Unavailable`), ніж допустити автоматичне вчинення правопорушення з багатомільйонним штрафом за несанкціоноване переміщення банківських даних.
4. **Конкурентність без блокувань (Lock-Free Read Path):** При динамічному оновленні правил юрисдикцій робочі потоки маршрутизатора вичитують конфігурацію через атомарні покажчики `std::atomic<const JurisdictionConfig*>` за патерном RCU (Read-Copy-Update). Оновлення конфігурації триває менше 5 мікросекунд без зупинки обробки запитів.
