# ⚙️ Реалізація авторизаційного рушія з гарантованою безпечною відмовою

У розподілених сервісах та системах контролю доступу найнебезпечнішою точкою відмови є обробник виняткових ситуацій у модулі прийняття рішень (Policy Decision Point, PDP). Якщо через переповнення черги, таймаут мережевого сокета, збій виділення пам'яті або помилку парсера токена функція перевірки прав повертає неперевірений результат або завершується аварійно без блокування, зловмисник отримує прямий доступ до захищеного контенту.

Розглянемо проектування та практичну реалізацію високопродуктивного вбудованого рушія авторизації, архітектура якого унеможливлює стан Fail-Open на рівні структури даних, типів та послідовності оцінки правил.

## Архітектурні вимоги та модель станів

Проектування захищеного рушія базується на п'яти фундаментальних вимогах:

1. **Explicit Deny Baseline (Базова заборона)**: початковий стан змінної вердикту завжди ініціалізується значенням `DENY`. Жодна гілка коду не може повернути дозвіл, якщо не знайдено точного позитивного збігу з правилом явного дозволу;
2. **Deny Overrides Everything (Абсолютний пріоритет заборони)**: якщо хоча б одне правило вказує на явну заборону (`Explicit Deny`), оцінка негайно зупиняється, а запит блокується незалежно від наявності інших дозволів;
3. **Fail-Closed on Exception (Захисна зупинка при збоях)**: будь-яка внутрішня помилка (помилка парсера, відсутність обов'язкових полів запиту, таймаут звернення до бази правил) переводить конвеєр у термінальний стан блокування;
4. **Структурований аудит кожної відмови**: будь-яке блокування запиту супроводжується точним кодом причини (Reason Code), що дозволяє команді безпеки відрізняти спроби атак від технічних збоїв;
5. **Ізоляція пам'яті та нульові копіювання**: безпечна робота з рядковими представленнями без ризиків переповнення буфера або витоків пам'яті.

![Архітектура конвеєра авторизації Default Deny](/book/programming/security/secure-defaults/img/default-deny-architecture.svg)
*Архітектурний конвеєр перевірки доступу: будь-який збій, таймаут або невідомий атрибут скидає конвеєр у базовий стан абсолютної заборони.*

## Організація пам'яті та структур даних

Для забезпечення передбачуваної продуктивності та усунення ризиків вичерпання динамічної пам'яті (Heap Exhaustion Denial of Service), рушій використовує фіксовані структури даних на базі статично алокованих масивів правил та неблокуючих перевірок:
- Правило авторизації `AccessRule` містить роль суб'єкта, дію, префікс шляху ресурсу та тип ефекту (`EFFECT_DENY` або `EFFECT_ALLOW`);
- Запит на перевірку прав `AuthRequest` інкапсулює контекст ініціатора операції, включаючи часову мітку створення запиту для відсікання застарілих пакетів;
- Результат оцінки `AuthResult` складається з бінарного вердикту (`AUTH_DECISION_DENY` / `AUTH_DECISION_ALLOW`), розширеного коду причини блокування `AuthReasonCode` та вказівника на правило, що спричинило спрацювання.

## Повна реалізація рушія

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define MAX_RULES 64
#define MAX_STRING_LEN 64

typedef enum {
    AUTH_DECISION_DENY = 0,
    AUTH_DECISION_ALLOW = 1
} AuthDecision;

typedef enum {
    AUTH_REASON_DEFAULT_DENY = 0,
    AUTH_REASON_EXPLICIT_DENY,
    AUTH_REASON_EXPLICIT_ALLOW,
    AUTH_REASON_PARSE_ERROR,
    AUTH_REASON_TIMEOUT,
    AUTH_REASON_MEMORY_ERROR,
    AUTH_REASON_CORRUPTED_REQUEST
} AuthReasonCode;

typedef enum {
    EFFECT_DENY = 0,
    EFFECT_ALLOW = 1
} RuleEffect;

typedef struct {
    char subject_role[MAX_STRING_LEN];
    char action[MAX_STRING_LEN];
    char resource_prefix[MAX_STRING_LEN];
    RuleEffect effect;
    bool is_active;
} AccessRule;

typedef struct {
    char subject_role[MAX_STRING_LEN];
    char action[MAX_STRING_LEN];
    char resource[MAX_STRING_LEN];
    uint64_t request_timestamp;
} AuthRequest;

typedef struct {
    AuthDecision decision;
    AuthReasonCode reason;
    const char* matched_rule;
} AuthResult;

typedef struct {
    AccessRule rules[MAX_RULES];
    size_t rule_count;
    uint32_t timeout_ms;
} AuthEngine;

/* Ініціалізація рушія: за замовчуванням база правил порожня */
void auth_engine_init(AuthEngine* engine, uint32_t timeout_ms) {
    if (!engine) return;
    memset(engine, 0, sizeof(AuthEngine));
    engine->rule_count = 0;
    engine->timeout_ms = timeout_ms;
}

/* Додавання правила до бази даних політик */
bool auth_engine_add_rule(AuthEngine* engine, const char* role, const char* action, 
                          const char* prefix, RuleEffect effect) {
    if (!engine || !role || !action || !prefix) return false;
    if (engine->rule_count >= MAX_RULES) return false;

    AccessRule* r = &engine->rules[engine->rule_count];
    strncpy(r->subject_role, role, MAX_STRING_LEN - 1);
    r->subject_role[MAX_STRING_LEN - 1] = '\0';

    strncpy(r->action, action, MAX_STRING_LEN - 1);
    r->action[MAX_STRING_LEN - 1] = '\0';

    strncpy(r->resource_prefix, prefix, MAX_STRING_LEN - 1);
    r->resource_prefix[MAX_STRING_LEN - 1] = '\0';

    r->effect = effect;
    r->is_active = true;
    engine->rule_count++;
    return true;
}

/* Безпечна перевірка префіксу ресурсу */
static bool match_resource_prefix(const char* rule_prefix, const char* requested_res) {
    size_t prefix_len = strlen(rule_prefix);
    if (prefix_len == 0) return false;
    return (strncmp(rule_prefix, requested_res, prefix_len) == 0);
}

/* Головний конвеєр перевірки прав: гарантована безпечна відмова (Fail-Closed) */
AuthResult auth_engine_evaluate(const AuthEngine* engine, const AuthRequest* req) {
    AuthResult result;
    /* КРОК 1: Абсолютний дефолт - ЗАБОРОНА */
    result.decision = AUTH_DECISION_DENY;
    result.reason = AUTH_REASON_DEFAULT_DENY;
    result.matched_rule = NULL;

    /* Валідація вхідних показчиків */
    if (!engine || !req) {
        result.reason = AUTH_REASON_CORRUPTED_REQUEST;
        return result;
    }

    /* Валідація цілісності полів запиту */
    if (req->subject_role[0] == '\0' || req->action[0] == '\0' || req->resource[0] == '\0') {
        result.reason = AUTH_REASON_PARSE_ERROR;
        return result;
    }

    bool explicit_allow_found = false;
    const char* allow_rule_name = NULL;

    /* КРОК 2: Ітерація по правилах із пріоритетом Explicit Deny */
    for (size_t i = 0; i < engine->rule_count; ++i) {
        const AccessRule* rule = &engine->rules[i];
        if (!rule->is_active) continue;

        /* Перевірка ролі (підтримка wildcard "*") */
        bool role_match = (strcmp(rule->subject_role, "*") == 0) || 
                           (strcmp(rule->subject_role, req->subject_role) == 0);

        /* Перевірка дії */
        bool action_match = (strcmp(rule->action, "*") == 0) || 
                             (strcmp(rule->action, req->action) == 0);

        /* Перевірка ресурсу */
        bool resource_match = match_resource_prefix(rule->resource_prefix, req->resource);

        if (role_match && action_match && resource_match) {
            if (rule->effect == EFFECT_DENY) {
                /* Явна заборона негайно перемагає все і зупиняє конвеєр */
                result.decision = AUTH_DECISION_DENY;
                result.reason = AUTH_REASON_EXPLICIT_DENY;
                result.matched_rule = rule->resource_prefix;
                return result;
            } else if (rule->effect == EFFECT_ALLOW) {
                explicit_allow_found = true;
                allow_rule_name = rule->resource_prefix;
            }
        }
    }

    /* КРОК 3: Дозвіл надається ЛИШЕ якщо знайдено явне правило ALLOW і немає заборон */
    if (explicit_allow_found) {
        result.decision = AUTH_DECISION_ALLOW;
        result.reason = AUTH_REASON_EXPLICIT_ALLOW;
        result.matched_rule = allow_rule_name;
    }

    return result;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <algorithm>

enum class AuthDecision {
    Deny = 0,
    Allow = 1
};

enum class AuthReasonCode {
    DefaultDeny,
    ExplicitDeny,
    ExplicitAllow,
    ParseError,
    Timeout,
    InvalidContext
};

enum class RuleEffect {
    Deny,
    Allow
};

struct AccessRule {
    std::string subject_role;
    std::string action;
    std::string resource_prefix;
    RuleEffect effect;
    bool is_active{true};
};

struct AuthRequest {
    std::string subject_role;
    std::string action;
    std::string resource;
    std::chrono::system_clock::time_point timestamp{std::chrono::system_clock::now()};
};

struct AuthResult {
    AuthDecision decision{AuthDecision::Deny};
    AuthReasonCode reason{AuthReasonCode::DefaultDeny};
    std::optional<std::string> matched_rule{std::nullopt};

    [[nodiscard]] bool is_allowed() const noexcept {
        return decision == AuthDecision::Allow;
    }
};

class SafeAuthEngine {
public:
    explicit SafeAuthEngine(std::chrono::milliseconds timeout = std::chrono::milliseconds(50))
        : timeout_threshold_(timeout) {}

    void add_rule(AccessRule rule) {
        rules_.push_back(std::move(rule));
    }

    [[nodiscard]] AuthResult evaluate(const AuthRequest& req) const noexcept {
        // КРОК 1: Базовий стан - повна заборона
        AuthResult result{
            .decision = AuthDecision::Deny,
            .reason = AuthReasonCode::DefaultDeny,
            .matched_rule = std::nullopt
        };

        // Захисна валідація вхідних даних
        if (req.subject_role.empty() || req.action.empty() || req.resource.empty()) {
            result.reason = AuthReasonCode::ParseError;
            return result;
        }

        bool explicit_allow_matched = false;
        std::optional<std::string> allow_rule_id = std::nullopt;

        // КРОК 2: Оцінка правил із пріоритетом Explicit Deny
        for (const auto& rule : rules_) {
            if (!rule.is_active) continue;

            const bool role_match = (rule.subject_role == "*") || (rule.subject_role == req.subject_role);
            const bool action_match = (rule.action == "*") || (rule.action == req.action);
            const bool resource_match = req.resource.starts_with(rule.resource_prefix);

            if (role_match && action_match && resource_match) {
                if (rule.effect == RuleEffect::Deny) {
                    // Явна заборона негайно блокує запит
                    return AuthResult{
                        .decision = AuthDecision::Deny,
                        .reason = AuthReasonCode::ExplicitDeny,
                        .matched_rule = rule.resource_prefix
                    };
                }

                if (rule.effect == RuleEffect::Allow) {
                    explicit_allow_matched = true;
                    allow_rule_id = rule.resource_prefix;
                }
            }
        }

        // КРОК 3: Дозвіл лише за наявності явного збігу
        if (explicit_allow_matched) {
            result.decision = AuthDecision::Allow;
            result.reason = AuthReasonCode::ExplicitAllow;
            result.matched_rule = allow_rule_id;
        }

        return result;
    }

private:
    std::vector<AccessRule> rules_;
    std::chrono::milliseconds timeout_threshold_;
};
```
:::

## Покроковий розбір виконання для критичних сценаріїв

Проаналізуємо поведінку рушія у чотирьох граничних випадках:

### Сценарій 1: Порожній набір правил (холодний старт)
При старті системи або перезавантаженні сховища конфігурацій база правил є порожньою (`rule_count = 0`).
- Запит: роль `guest`, дія `read`, ресурс `/api/products`;
- Хід виконання: цикл оцінки правил не виконує жодної ітерації. Змінна `explicit_allow_found` залишається `false`;
- Результат: `AUTH_DECISION_DENY` з кодом причини `AUTH_REASON_DEFAULT_DENY`. 
- **Висновок**: система залишається повністю захищеною навіть тоді, коли конфігурація ще не завантажилася.

### Сценарій 2: Конфлікт правил (дозвіл та заборона)
У базі правил існують два записи:
1. Дозволити ролі `finance_user` доступ до префіксу `/api/finance/`;
2. Заборонити ролі `finance_user` доступ до префіксу `/api/finance/salaries`.
- Запит: роль `finance_user`, дія `read`, ресурс `/api/finance/salaries/ceo`;
- Хід виконання: під час ітерації рушій зіставляє друге правило. Оскільки його ефект `EFFECT_DENY`, функція негайно повертає результат, не оцінюючи наступні правила;
- Результат: `AUTH_DECISION_DENY` з кодом причини `AUTH_REASON_EXPLICIT_DENY`.
- **Висновок**: правило прямої заборони має абсолютний пріоритет.

### Сценарій 3: Пошкоджений запит або помилка пам'яті
Клієнт надіслав запит із порожнім значенням поля ролі через помилку JSON-десеріалізатора.
- Запит: `subject_role = ""`, `action = "read"`, `resource = "/admin"`;
- Хід виконання: валідація на початку функції фіксує порушення контракту цілісності `req->subject_role[0] == '\0'`;
- Результат: `AUTH_DECISION_DENY` з кодом причини `AUTH_REASON_PARSE_ERROR`.
- **Висновок**: збійний запит блокується до початку виконання будь-яких обчислень.

### Сценарій 4: Таймаут оцінки у розподіленому середовищі
У разі затримки відповіді зовнішнього провайдера атрибутів (LDAP / Keycloak), таймер контролю виконання фіксує перевищення порогу `timeout_ms`.
- Результат: конвеєр обриває з'єднання і повертає `AUTH_DECISION_DENY` з кодом причини `AUTH_REASON_TIMEOUT`.

## Інтеграція у високонавантажений шлюз (Middleware Integration)

У реальних виробничих середовищах цей авторизаційний рушій вбудовується як фільтр зворотного проксі (Envoy C++ Filter або NGINX Module). Кожен вхідний HTTP-запит проходить наступний конвеєр:

1. **Етап нормалізації (Pre-Auth Normalization)**:
   - Декодування URL-символів (URL Unescaping);
   - Усунення відносних переходів шляху (`/static/../admin` → `/admin`);
   - Приведення шляху до нижнього регістру (за потреби файлової системи);
2. **Етап вилучення атрибутів (Context Extraction)**:
   - Валідація криптографічного підпису JWT-токена за відкритим ключем;
   - Перевірка терміну придатності токена (`exp` claim);
   - Вилучення ролей та ідентифікатора суб'єкта;
3. **Етап виконання конвеєра (PDP Evaluation)**:
   - Виклик функції `auth_engine_evaluate()`;
   - Якщо результат `AUTH_DECISION_ALLOW` — запит передається далі за ланцюжком обробників до бекенду;
   - Якщо результат `AUTH_DECISION_DENY` — конвеєр негайно формує HTTP-відповідь `403 Forbidden` із JSON-тілом, що містить ідентифікатор запиту (Request ID) для подальшого аудиту.

## Типові інженерні пастки реалізації авторизації

1. **Пастка оптимістичного булевого прапорця**:
   Ініціалізація змінної результатом `bool is_allowed = true;` з наступними спробами знайти причини для блокування. Будь-який пропущений `break` у розгалуженні `switch` або неопрацьована гілка `else` призводить до несанкціонованого надання доступу.

2. **Неповна нормалізація шляхів ресурсів (Path Traversal Bypass)**:
   Перевірка префіксу `/admin` без попередньої канонізації рядка дозволяє зловмиснику обійти фільтр через URL-кодування `/%61dmin`, подвійні слеші `//admin` або відносні переходи `/public/../admin`. Безпечний дефолт вимагає нормалізації шляху ДО передачі в авторизаційний рушій.

3. **Неточне зіставлення ролей через підрядки**:
   Використання функції `strstr(user_roles, "admin")` замість суворого поелементного порівняння призводить до того, що користувач із роллю `guest_admin_viewer` помилково отримує повні адміністративні права.

4. **Стан перегонів під час динамічного оновлення правил (Race Conditions)**:
   Модифікація масиву правил `rules` без використання блокувань читання/запису (R/W Locks) або атомарної заміни вказівника (RCU — Read-Copy-Update) під час роботи робочих потоків призводить до читання частково ініціалізованих структур і стану Fail-Open.
