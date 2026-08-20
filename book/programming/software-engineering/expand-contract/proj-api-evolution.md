# ⚙️ Промислова еволюція API: покрокова реалізація трифазного переходу

Цей проєкт демонструє наскрізну реалізацію еволюції контракту інтерфейсу сервісу користувачів: від простого пошуку за рядковим ідентифікатором до багатоорендної моделі з контекстом організації, динамічними прапорцями та повною підтримкою телеметрії міграції. Кожен крок показує точний стан коду, механізми сумісності (перехідні шими), захист від гонитви даних при подвійному читанні та фінальне очищення.

Головна мета проєкту — показати, як уникнути пастки зламаної збірки та несподіваного простою, перетворивши зміну сигнатури функцій та структур даних на повністю контрольовану послідовність сумісних кроків.

---

## Задача та вихідний стан (Фаза 0: Baseline)

Початковий контракт надає функцію отримання профілю користувача за унікальним рядковим `user_id`. Бізнес-вимога: система переходить на багатоорендну (англ. *multi-tenant*) архітектуру, де користувач однозначно визначається парою `(tenant_id, user_id)`, а запит може містити додаткові прапорці доступу та налаштування фільтрації.

Зміна сигнатури є прямою ламкою зміною: якщо одночасно змінити функцію, всі споживачі, які передають лише `user_id`, перестануть збиратися або завершаться аварійно під час виконання. У розподіленій системі, де сервіси розгортаються незалежно різними командами, одночасна заміна неможлива через часовий розрив між випуском бібліотеки та її підключенням у клієнтських модулях.

---

## Крок 1. Фаза розширення (Phase 1: Expand)

На першому кроці постачальник впроваджує нову структуру параметрів та новий розширений метод. Старий метод **не видаляється**, а перетворюється на перехідний адаптер (англ. *backward-compatibility shim*), який делегує виконання новому методу, підставляючи безпечне значення орендаря за замовчуванням (`default_tenant`).

Кожен виклик через застарілий інтерфейс перенаправляється до центральної точки обробки, завдяки чому бізнес-логіка залишається строго в одному місці й не дублюється. Старі клієнти можуть продовжувати викликати первинну функцію, навіть не підозрюючи про внутрішнє розширення архітектури.

Зверніть увагу на керування пам'яттю: у C-реалізації структура `user_lookup_request_t` розміщується на стеку викликача, що запобігає фрагментації динамічної пам'яті (купи). У C++ варіанті використовуються легковагі неволодіючі представлення `std::string_view`, які виключають зайве копіювання рядків.

:::tabs
```c
/* user_service.h — Фаза 1: Expand */
#ifndef USER_SERVICE_H
#define USER_SERVICE_H

#include <stddef.h>
#include <stdbool.h>

#define MAX_NAME_LEN 128
#define DEFAULT_TENANT_ID "tenant_default"

typedef struct {
    const char* user_id;
    const char* tenant_id;   /* Нове поле багатоорендності */
    unsigned int flags;       /* Додаткові прапорці доступу */
} user_lookup_request_t;

typedef struct {
    char name[MAX_NAME_LEN];
    char email[MAX_NAME_LEN];
    bool is_active;
} user_profile_t;

/* Старий інтерфейс v1: залишається повністю працездатним для існуючих клієнтів */
int user_service_get_by_id(const char* user_id, user_profile_t* out_profile);

/* Новий розширений інтерфейс v2: приймає повну структуру контексту */
int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile);

#endif /* USER_SERVICE_H */
```
```cpp
// user_service.hpp — Фаза 1: Expand
#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>

struct UserLookupRequest {
    std::string_view user_id;
    std::string_view tenant_id{"tenant_default"};
    uint32_t flags{0};
};

struct UserProfile {
    std::string name;
    std::string email;
    bool is_active{true};
};

enum class ServiceError {
    InvalidArgument,
    UserNotFound,
    TenantNotFound,
    InternalStorageError
};

class UserService {
public:
    // Старий інтерфейс: повертає результат через типізований std::expected
    std::expected<UserProfile, ServiceError> get_user_by_id(std::string_view user_id);

    // Новий розширений інтерфейс: повна багатоорендна модель
    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req);
};
```
:::

Реалізація на стороні постачальника зв'язує обидва методи, гарантуючи єдину точку бізнес-логіки та коректну ініціалізацію буферів. Якщо вхідний запит не містить ідентифікатора орендаря, рушій автоматично підставляє системне замовчування:

:::tabs
```c
/* user_service.c — Реалізація Фази 1 (Expand) */
#include "user_service.h"
#include <string.h>

/* Внутрішній рушій пошуку у сховищі */
static int storage_find_internal(const char* tenant, const char* uid, unsigned int flags, user_profile_t* out) {
    if (!tenant || !uid || !out) return -1;
    (void)flags; /* Прапорці зарезервовані для майбутньої фільтрації */
    
    /* Імітація читання даних користувача */
    if (strcmp(uid, "usr_101") == 0) {
        strncpy(out->name, "Тарас Шевченко", MAX_NAME_LEN - 1);
        strncpy(out->email, "taras@example.ua", MAX_NAME_LEN - 1);
        out->name[MAX_NAME_LEN - 1] = '\0';
        out->email[MAX_NAME_LEN - 1] = '\0';
        out->is_active = true;
        return 0;
    }
    return -2; /* Запис не знайдено */
}

int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile) {
    if (!req || !req->user_id) return -1;
    const char* tenant = req->tenant_id ? req->tenant_id : DEFAULT_TENANT_ID;
    return storage_find_internal(tenant, req->user_id, req->flags, out_profile);
}

/* Старий метод трансформується у тонкий адаптер (Shim) */
int user_service_get_by_id(const char* user_id, user_profile_t* out_profile) {
    user_lookup_request_t req;
    req.user_id = user_id;
    req.tenant_id = DEFAULT_TENANT_ID;
    req.flags = 0;
    return user_service_find(&req, out_profile);
}
```
```cpp
// user_service.cpp — Реалізація Фази 1 (Expand)
#include "user_service.hpp"

std::expected<UserProfile, ServiceError> UserService::find_user(UserLookupRequest const& req) {
    if (req.user_id.empty()) {
        return std::unexpected(ServiceError::InvalidArgument);
    }
    
    std::string_view const tenant = req.tenant_id.empty() ? "tenant_default" : req.tenant_id;

    // Імітація доступу до бази даних
    if (req.user_id == "usr_101") {
        return UserProfile{
            .name = "Тарас Шевченко",
            .email = "taras@example.ua",
            .is_active = true
        };
    }
    return std::unexpected(ServiceError::UserNotFound);
}

// Старий метод перенаправляє виклик у новий інтерфейс із замовчуваним контекстом
std::expected<UserProfile, ServiceError> UserService::get_user_by_id(std::string_view user_id) {
    UserLookupRequest req{
        .user_id = user_id,
        .tenant_id = "tenant_default",
        .flags = 0
    };
    return find_user(req);
}
```
:::

---

## Крок 2. Фаза міграції та застарівання (Phase 2: Transition & Deprecation)

Після випуску нової версії бібліотеки старий метод маркується як застарілий за допомогою атрибутів компілятора та інструментується потокобезпечними лічильниками телеметрії. Це змушує клієнтські команди бачити діагностичні попередження під час збірки своїх сервісів, а команда постачальника отримує точний графік згасання старого трафіку.

Використання атомарних операцій на рівні пам'яті (`std::atomic` з моделлю пам'яті `std::memory_order_relaxed`) гарантує точність обліку трафіку під інтенсивним багатопотоковим навантаженням без використання важких м'ютексів та блокувань ядра операційної системи.

У C-реалізації функція `user_service_get_metrics` дозволяє збирачу метрик періодично опитувати внутрішній стан лічильників та відправляти дані до централізованої системи Prometheus чи OpenTelemetry Collector.

:::tabs
```c
/* user_service_v2.h — Фаза 2: Застарівання */
#ifndef USER_SERVICE_V2_H
#define USER_SERVICE_V2_H

#include "user_service.h"

#if defined(__GNUC__) || defined(__clang__)
#  define DEPRECATED_MSG(msg) __attribute__((deprecated(msg)))
#elif defined(_MSC_VER)
#  define DEPRECATED_MSG(msg) __declspec(deprecated(msg))
#else
#  define DEPRECATED_MSG(msg)
#endif

/* Атрибут сигналізує розробнику під час збірки клієнтського проєкту */
DEPRECATED_MSG("user_service_get_by_id is deprecated. Migrate to user_service_find. Removal in v3.0.")
int user_service_get_by_id(const char* user_id, user_profile_t* out_profile);

int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile);

/* Структура для аудиту міграції через телеметрію */
typedef struct {
    unsigned long legacy_calls_count;
    unsigned long v2_calls_count;
} migration_metrics_t;

void user_service_get_metrics(migration_metrics_t* out_metrics);

#endif
```
```cpp
// user_service_v2.hpp — Фаза 2: Застарівання та телеметрія
#pragma once
#include "user_service.hpp"
#include <atomic>

class UserServiceV2 {
private:
    inline static std::atomic<uint64_t> s_legacy_calls{0};
    inline static std::atomic<uint64_t> s_v2_calls{0};

public:
    [[deprecated("get_user_by_id is deprecated. Use find_user(UserLookupRequest) instead. Removal in v3.0.")]]
    std::expected<UserProfile, ServiceError> get_user_by_id(std::string_view user_id) {
        s_legacy_calls.fetch_add(1, std::memory_order_relaxed);
        UserLookupRequest req{.user_id = user_id, .tenant_id = "tenant_default", .flags = 0};
        return find_user(req);
    }

    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req) {
        s_v2_calls.fetch_add(1, std::memory_order_relaxed);
        if (req.user_id.empty()) {
            return std::unexpected(ServiceError::InvalidArgument);
        }
        if (req.user_id == "usr_101") {
            return UserProfile{.name = "Тарас Шевченко", .email = "taras@example.ua", .is_active = true};
        }
        return std::unexpected(ServiceError::UserNotFound);
    }

    static uint64_t legacy_call_count() noexcept {
        return s_legacy_calls.load(std::memory_order_relaxed);
    }

    static uint64_t v2_call_count() noexcept {
        return s_v2_calls.load(std::memory_order_relaxed);
    }
};
```
:::

---

## Крок 3. Реалізація подвійного читання у вебсервісі (Dual-Read Fallback)

Коли зміна стосується розподіленого сховища даних (наприклад, перехід зі старого ключа Redis `user:{id}` на складний ключ `tenant:{t}:user:{id}`), клієнтський шар застосовує стратегію читання з резервним відкатом (англ. *Read New with Fallback to Old*).

Цей механізм вирішує фундаментальну проблему асинхронності: неможливо миттєво скопіювати мільярди записів у нову структуру без перевантаження бази даних. Завдяки подвійному читанню сервіс починає негайно обслуговувати нові та вже мігровані записи через нове сховище, а для немігрованих прозоро звертається до старого ключа.

Особливу увагу слід звернути на обробку помилок: якщо сховище повертає системну помилку з'єднання (мережевий таймаут або збій кластера), сервіс зобов'язаний негайно повернути помилку клієнту, а не переходити до резервного джерела, щоб не маскувати аварійний стан інфраструктури.

Інженери також повинні враховувати поведінку при видаленні записів (англ. *tombstone handling*): якщо сутність видаляється через новий інтерфейс, ключ у старому сховищі також повинен маркуватися як видалений або видалятися атомарно, щоб резервне читання випадково не воскресило застарілі дані.

:::tabs
```go
// user_repository.go — Подвійне читання з відкатом на Go
package repository

import (
	"context"
	"fmt"
)

type UserStore interface {
	Get(ctx context.Context, key string) (string, error)
}

type MetricsCollector interface {
	IncLegacyFallback()
	IncPrimaryHit()
}

type UserRepository struct {
	store   UserStore
	metrics MetricsCollector
}

func (r *UserRepository) FetchUser(ctx context.Context, tenantID, userID string) (string, error) {
	// 1. Спроба вичитати за новим багатоорендним ключем (v2)
	newKey := fmt.Sprintf("tenant:%s:user:%s", tenantID, userID)
	data, err := r.store.Get(ctx, newKey)
	if err == nil && data != "" {
		r.metrics.IncPrimaryHit()
		return data, nil
	}

	// 2. Fallback: якщо запис ще не мігровано бекфілом, читаємо за старим ключем v1
	legacyKey := fmt.Sprintf("user:%s", userID)
	legacyData, legErr := r.store.Get(ctx, legacyKey)
	if legErr == nil && legacyData != "" {
		r.metrics.IncLegacyFallback() // Фіксуємо факт роботи через застаріле сховище
		return legacyData, nil
	}

	return "", fmt.Errorf("user not found: %s", userID)
}
```
```typescript
// UserRepository.ts — Подвійне читання з відкатом на TypeScript
export interface KeyValueStore {
  get(key: string): Promise<string | null>;
}

export interface Telemetry {
  recordPrimaryHit(): void;
  recordFallbackHit(): void;
}

export class UserRepository {
  constructor(
    private readonly store: KeyValueStore,
    private readonly telemetry: Telemetry
  ) {}

  async fetchUser(tenantId: string, userId: string): Promise<string> {
    // 1. Пріоритетне читання з нового багатоорендного сховища (v2)
    const v2Key = `tenant:${tenantId}:user:${userId}`;
    const v2Data = await this.store.get(v2Key);
    if (v2Data !== null) {
      this.telemetry.recordPrimaryHit();
      return v2Data;
    }

    // 2. Резервне читання зі старого формату (якщо бекфіл ще не завершився)
    const v1Key = `user:${userId}`;
    const v1Data = await this.store.get(v1Key);
    if (v1Data !== null) {
      this.telemetry.recordFallbackHit();
      return v1Data;
    }

    throw new Error(`User not found: ${userId} in tenant ${tenantId}`);
  }
}
```
:::

---

## Крок 4. Фаза звуження (Phase 3: Contract)

Щойно показник `legacy_call_count()` або лічильник `legacy_fallback` стабільно дорівнює нулю протягом контрольного вікна (наприклад, 7 повних діб під робочим навантаженням), постачальник випускає мажорне оновлення (SemVer v3.0.0), у якому старий метод та адаптери повністю видаляються.

Кодова база звільняється від проміжних перевірок та перехідних адаптерів, повертаючись до чистого, зрозумілого і високопродуктивного стану. Компілятор гарантує відсутність мертвого коду, а розробники отримують чіткий інтерфейс без застарілих рудиментів.

Таке очищення є обов'язковим завершальним акордом: без нього архітектура системи з часом деградує під тягарем нескінченних нашарувань перехідних перехідників.

:::tabs
```c
/* user_service_v3.h — Фаза 3: Чистий контракт v3.0 */
#ifndef USER_SERVICE_V3_H
#define USER_SERVICE_V3_H

#include <stddef.h>
#include <stdbool.h>

#define MAX_NAME_LEN 128

typedef struct {
    const char* user_id;
    const char* tenant_id;
    unsigned int flags;
} user_lookup_request_t;

typedef struct {
    char name[MAX_NAME_LEN];
    char email[MAX_NAME_LEN];
    bool is_active;
} user_profile_t;

/* Єдиний цільовий метод: старий user_service_get_by_id вилучено повністю */
int user_service_find(const user_lookup_request_t* req, user_profile_t* out_profile);

#endif /* USER_SERVICE_H */
```
```cpp
// user_service_v3.hpp — Фаза 3: Чистий контракт v3.0
#pragma once

#include <string>
#include <string_view>
#include <expected>
#include <cstdint>

struct UserLookupRequest {
    std::string_view user_id;
    std::string_view tenant_id;
    uint32_t flags{0};
};

struct UserProfile {
    std::string name;
    std::string email;
    bool is_active{true};
};

enum class ServiceError {
    InvalidArgument,
    UserNotFound,
    TenantNotFound,
    InternalStorageError
};

class UserService {
public:
    // Старий метод get_user_by_id вилучено з кодової бази.
    // Залишився лише чистий, оптимізований цільовий контракт:
    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req);
};
```
:::

У результаті виконання трифазного циклу система досягла повної трансформації бізнес-моделі без жодної хвилини простою сервісу, без конфліктів у командній роботі та з нульовим ризиком несподіваної деградації виробничого середовища.
