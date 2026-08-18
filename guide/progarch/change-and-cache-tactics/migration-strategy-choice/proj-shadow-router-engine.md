# ⚙️ Практична реалізація роутера тіньового трафіку та звіряння результатів (Dark Launch / Dual Run Engine)

У цій практичній вставці викладено готову інженерну реалізацію асинхронного роутера трафіку, який підтримує два ключових режими безпечної міграції живих систем: **Dark Launch (темний запуск / тіньове дублювання)** та **Parallel Run (паралельне виконання зі звірянням відповідей)**. Програмний модуль призначений для вбудовування на рівні API-шлюзу або всередині сервісного шару. Він асинхронно перехоплює вхідні користувацькі запити, спрямовує їх на первинну (стару) та тіньову (нову) системи, гарантує повну ізоляцію побічних ефектів для клієнтів і фіксує статистику розбіжностей у реальному часі.

---

## 1. Архітектура роутера, гарантії продуктивності та ізоляція побічних ефектів

Під час розгортання асинхронного дублювання або паралельного виконання трафіку головною інженерною небезпекою є **виникнення незапланованих побічних ефектів** (Unintended Side Effects). Якщо нова версія сервісу під час виконання тіньового запиту зателефонує до зовнішнього платіжного шлюзу, відправить повторне SMS-повідомлення клієнту або запише дублюючий рядок у продакшн-базу даних, тіньовий запуск миттєво перетвориться на критичний інцидент псування даних.

Для усунення цих ризиків роутер реалізує суворе розділення виконавчих контурів:

```
                          +-------------------------------+
                          |    Вхідний HTTP/gRPC Запит    |
                          +-------------------------------+
                                          |
                        +-----------------------------------+
                        |   Shadow / Dual Traffic Router    |
                        +-----------------------------------+
                                   /             \
                   (Синхронно)    /               \   (Асинхронно / Воркер)
                                 /                 \
                 +-----------------------+   +-----------------------+
                 | Primary System (v1)   |   | Shadow System (v2)    |
                 | (Обслуговує клієнта)  |   | (Тіньовий запуск)     |
                 +-----------------------+   +-----------------------+
                             |                           |
                             v                           v
                     +---------------+           +---------------+
                     |  Response v1  |           |  Response v2  |
                     +---------------+           +---------------+
                             |                           |
                             +-----------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         | Reconciler & Diff Engine      |
                         | (Запис latency & розбіжностей)|
                         +-------------------------------+
```

Роутер гарантує такі три фундаментальні властивості:

1. **Захист затримки первинної відповіді (Primary Latency Isolation):** Основний потік обробки запиту викликає службу `Primary` синхронно і повертає відповідь клієнту негайно після її отримання. Виклики до служб `Shadow` виконуються у неблокуючих воркер-потоках або фонових горутинах. Будь-які затримки, тупикові стани (deadlocks) або падіння у тіньовій службі не позначаються на часі відповіді для користувача.
2. **Нівелювання побічних мутацій (Mutation Muting):** У режимі Dark Launch тіньова служба підключається до ізольованого тестового контуру або запускається із прапорцем `READ_ONLY_MODE=true`. Якщо запит містить мутуючий HTTP-метод (`POST`, `PUT`, `DELETE`), тіньовий шар перехоплює зовнішні виклики та замінює їх на ідемпотентні заглушки (Stubs/Mocks).
3. **Атомарний аналіз розбіжностей (Atomic Reconciliation):** У режимі Parallel Run результати роботи обох систем передаються до модуля звіряння, який обчислює хеш або структурну різницю відповідей і збільшує метрики розбіжностей.

---

## 2. Код роутера на C, C++ та Go (:::tabs)

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    char request_id[64];
    char payload[512];
    int user_id;
} request_t;

typedef struct {
    int status_code;
    char data[256];
    double latency_ms;
} response_t;

/* Контракт сервісу */
typedef response_t (*service_fn)(const request_t* req);

typedef struct {
    service_fn primary;
    service_fn shadow;
    bool enable_parallel_run;
    long total_processed;
    long diff_count;
    pthread_mutex_t lock;
} shadow_router_t;

typedef struct {
    shadow_router_t* router;
    request_t req;
    response_t primary_resp;
} shadow_task_t;

/* Імітація старої та нової систем */
response_t primary_service_v1(const request_t* req) {
    response_t resp = {200, "", 12.5};
    snprintf(resp.data, sizeof(resp.data), "USER_%d_BALANCE_100", req->user_id);
    return resp;
}

response_t shadow_service_v2(const request_t* req) {
    response_t resp = {200, "", 14.1};
    /* Імітація дрібної розбіжності для перевірки роботоздатності Reconciler */
    snprintf(resp.data, sizeof(resp.data), "USER_%d_BALANCE_100", req->user_id);
    return resp;
}

void* async_shadow_worker(void* arg) {
    shadow_task_t* task = (shadow_task_t*)arg;
    response_t shadow_resp = task->router->shadow(&task->req);

    pthread_mutex_lock(&task->router->lock);
    task->router->total_processed++;

    if (task->router->enable_parallel_run) {
        if (task->primary_resp.status_code != shadow_resp.status_code ||
            strcmp(task->primary_resp.data, shadow_resp.data) != 0) {
            task->router->diff_count++;
            fprintf(stderr, "[RECONCILER ALERT] Diff detected for ID %s! Primary: '%s', Shadow: '%s'\n",
                    task->req.request_id, task->primary_resp.data, shadow_resp.data);
        }
    }
    pthread_mutex_unlock(&task->router->lock);

    free(task);
    return NULL;
}

shadow_router_t* shadow_router_create(service_fn primary, service_fn shadow, bool enable_parallel_run) {
    shadow_router_t* router = (shadow_router_t*)malloc(sizeof(shadow_router_t));
    if (!router) return NULL;
    router->primary = primary;
    router->shadow = shadow;
    router->enable_parallel_run = enable_parallel_run;
    router->total_processed = 0;
    router->diff_count = 0;
    pthread_mutex_init(&router->lock, NULL);
    return router;
}

response_t shadow_router_dispatch(shadow_router_t* router, const request_t* req) {
    /* 1. Синхронний виклик основної системи для клієнта */
    response_t primary_resp = router->primary(req);

    /* 2. Асинхронне відгалуження тіньового виклику */
    shadow_task_t* task = (shadow_task_t*)malloc(sizeof(shadow_task_t));
    if (task) {
        task->router = router;
        task->req = *req;
        task->primary_resp = primary_resp;

        pthread_t thread;
        pthread_create(&thread, NULL, async_shadow_worker, task);
        pthread_detach(thread);
    }

    return primary_resp;
}

void shadow_router_free(shadow_router_t* router) {
    if (!router) return;
    pthread_mutex_destroy(&router->lock);
    free(router);
}
```
```cpp
// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <functional>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <expected>

struct Request {
    std::string request_id;
    std::string payload;
    int user_id;
};

struct Response {
    int status_code{200};
    std::string data;
    double latency_ms{0.0};

    bool operator==(const Response& other) const {
        return status_code == other.status_code && data == other.data;
    }
};

enum class MigrationError {
    Timeout,
    InternalError,
    ServiceUnavailable
};

using ServiceHandler = std::function<std::expected<Response, MigrationError>(const Request&)>;

class ShadowRouter {
public:
    ShadowRouter(ServiceHandler primary, ServiceHandler shadow, bool enable_parallel_run)
        : primary_service_(std::move(primary)),
          shadow_service_(std::move(shadow)),
          enable_parallel_run_(enable_parallel_run) {}

    ~ShadowRouter() = default;

    std::expected<Response, MigrationError> dispatch(const Request& req) {
        // 1. Синхронний виклик первинної системи (повертається клієнту)
        auto start = std::chrono::high_resolution_clock::now();
        auto primary_res = primary_service_(req);
        auto end = std::chrono::high_resolution_clock::now();

        if (!primary_res.has_value()) {
            return primary_res;
        }

        // 2. Асинхронний тіньовий прогон (Dark Launch / Dual Run)
        std::jthread([this, req, primary_resp = primary_res.value()]() {
            auto shadow_res = shadow_service_(req);
            total_processed_++;

            if (enable_parallel_run_ && shadow_res.has_value()) {
                if (primary_resp != shadow_res.value()) {
                    diff_count_++;
                    std::lock_guard<std::mutex> lock(log_mutex_);
                    std::cerr << "[RECONCILER ALERT] ID: " << req.request_id
                              << " | Primary: '" << primary_resp.data
                              << "' | Shadow: '" << shadow_res.value().data << "'\n";
                }
            } else if (!shadow_res.has_value()) {
                diff_count_++;
            }
        }).detach();

        return primary_res;
    }

    uint64_t total_processed() const { return total_processed_.load(); }
    uint64_t diff_count() const { return diff_count_.load(); }

private:
    ServiceHandler primary_service_;
    ServiceHandler shadow_service_;
    bool enable_parallel_run_;

    std::atomic<uint64_t> total_processed_{0};
    std::atomic<uint64_t> diff_count_{0};
    std::mutex log_mutex_;
};
```
```go
// go
package main

import (
	"fmt"
	"log"
	"sync/atomic"
	"time"
)

type Request struct {
	RequestID string
	Payload   string
	UserID    int
}

type Response struct {
	StatusCode int
	Data       string
	LatencyMS  float64
}

type ServiceFunc func(req Request) (Response, error)

type ShadowRouter struct {
	primary           ServiceFunc
	shadow            ServiceFunc
	enableParallelRun bool
	totalProcessed    uint64
	diffCount         uint64
}

func NewShadowRouter(primary, shadow ServiceFunc, enableParallelRun bool) *ShadowRouter {
	return &ShadowRouter{
		primary:           primary,
		shadow:            shadow,
		enableParallelRun: enableParallelRun,
	}
}

func (r *ShadowRouter) Dispatch(req Request) (Response, error) {
	// 1. Первинне виконання для клієнта
	resp, err := r.primary(req)
	if err != nil {
		return resp, err
	}

	// 2. Асинхронне тіньове дублювання
	go func(primaryResp Response) {
		atomic.AddUint64(&r.totalProcessed, 1)

		shadowResp, err := r.shadow(req)
		if err != nil || shadowResp.StatusCode != primaryResp.StatusCode || shadowResp.Data != primaryResp.Data {
			if r.enableParallelRun {
				atomic.AddUint64(&r.diffCount, 1)
				log.Printf("[RECONCILER ALERT] ID %s: Primary='%s', Shadow='%s', Err=%v",
					req.RequestID, primaryResp.Data, shadowResp.Data, err)
			}
		}
	}(resp)

	return resp, nil
}
```
:::

---

## 3. Глибокий розбір реалізацій та аналіз пам'яті

### 3.1. Реалізація мовою C: управління пам'яттю та POSIX-потоки

У реалізації на C ключовим питанням є забезпечення неблокуючої передачі структур даних між потоком обробки вхідного HTTP-запиту та фоновим тіньовим воркером:

1. **Динамічне виділення та відворот кучі:** Для кожного тіньового завдання виділяється екземпляр `shadow_task_t` через `malloc()`. Потік-первинний запис заповнює поля завдання, копіює структуру `request_t` та еталонну відповідь `primary_resp`, після чого передає вказівник у `pthread_create()`.
2. **Від'єднання потоку (Thread Detaching):** Застосування `pthread_detach(thread)` звільняє первинний потік від необхідності викликати `pthread_join()`. Потік обробки клієнтського запиту завершується негайно після створення воркера, а ОС автоматично повертає ресурси фоного потоку після його виходу.
3. **Захист системних лічильників:** М'ютекс `pthread_mutex_t lock` захищає оновлення системних метрик `total_processed` та `diff_count`. У високонавантажених C-сервісах замість глобального м'ютекса застосовують атомарні інструкції GCC/Clang (`__atomic_fetch_add`).

### 3.2. Реалізація мовою C++: RAII, std::jthread та безпечні типи

Реалізація C++20 демонструє сучасний ідіоматичний підхід до розробки асинхронних системних модулів:

1. **Типобезпечні помилки через `std::expected`:** Замість повернення оманових від'ємних цілочисельних кодів помилок або використання повільних винятків (Exceptions), функція `dispatch()` повертає `std::expected<Response, MigrationError>`. Це змушує викликаючий код явно обробити варіант помилки на етапі компіляції.
2. **Автономне управління потоками через `std::jthread`:** Застосування `std::jthread` спрощує роботу з асинхронністю. Конструктор створює потік виконання, а виклик `.detach()` явно передає володіння потоком системному планувальнику.
3. **Безблокувальні лічильники через `std::atomic`:** Лічильники `total_processed_` та `diff_count_` реалізовано через `std::atomic<uint64_t>`. Це усуває потребу в блокуванні м'ютекса при оновленні статистики у 99.9% випадків, залишаючи `std::mutex` виключно для синхронізації консольного виводу логів при виявленні розбіжностей.

### 3.3. Реалізація мовою Go: горутини та атомарні операції

У мові Go реалізація спирається на нативну підтримку легких потоків (Goroutines):

1. **Мінімальні накладні витрати на стек:** Запуск тіньового прогону через `go func(...)` вимагає всього 2–4 КБ початкового стека горутини порівняно з 1–8 МБ системного стека `pthread` у C/C++. Це дозволяє підтримувати сотні тисяч одночасних тіньових запитів на одному сервері.
2. **Атомарний моніторинг без каналів:** Оновлення лічильників через `atomic.AddUint64` гарантує мінімальну затримку на гарячому шляху виконання, не створюючи додаткового навантаження на планувальник Go (Go Scheduler).

---

## 4. Обробка крайових випадків та виклики експлуатації

Під час впровадження роутера тіньового трафіку у високонавантаженому продакшн-середовищі інженерна команда зобов'язана вирішити три фундаментальні виклики:

### 4.1. Захист від каскадного виснаження ресурсів (Backpressure & Thread Exhaustion)

При стихійному створенні фонових потоків (наприклад, `pthread_create` у C або неконтрольовані горутини у Go) сповільнення тіньової системи `v2` здатне паралізувати роботу всієї платформи. Якщо служба `v2` почне повертати відповіді не за 10 мс, а за 10 000 мс, кількість фонових потоків зросте експоненціально, що призведе до вичерпання RAM або таблиці дескрипторів процесу.

Рекомендована протидія: використання **обмеженого пулу воркерів (Bounded Thread Pool)** із фіксованою чергою. Якщо черга тіньових запитів заповнена на 100%, роутер повинен безболісно відкидати нові тіньові запити (Drop Policy), не зупиняючи обробку первинного трафіку.

```
                          +-----------------------------------+
                          |  Вхідний запит роутера            |
                          +-----------------------------------+
                                            |
                          +-----------------------------------+
                          |  Bounded Queue (Макс. 5000 елементів) |
                          +-----------------------------------+
                                     /             \
                 (Черга Вільна)     /               \  (Черга Повна: 100%)
                                   /                 \
            +---------------------------+       +---------------------------+
            | Передано воркеру Shadow   |       |  DROP POLICY (Відкидання) |
            | (Обробка у тіньовому контурі)|   |  (0% впливу на первинний) |
            +---------------------------+       +---------------------------+
```

### 4.2. Очищення та маскування персональних даних (PII Redaction)

Дублювання вхідних запитів означає, що персональні дані користувачів (паролі, номери карт, секрети) передаються у тіньовий контур. Якщо тіньове середовище є менш захищеним або використовує розширене логування, виникає ризик витоку конфіденційної інформації.

Перед відправкою запиту в службу `Shadow` роутер проводити обробку полів за допомогою правил маскування (Sanitizer), замінюючи чутливі значення на бекграунд-токени або хеші:

:::tabs
```c
/* c */
void sanitize_shadow_request(request_t* req) {
    if (strstr(req->payload, "password=")) {
        /* Заміна значення пароля на незворотний маскований токен */
        char* pos = strstr(req->payload, "password=");
        memset(pos + 9, '*', 8);
    }
}
```
```cpp
// cpp
void sanitize_shadow_request(Request& req) {
    auto pos = req.payload.find("password=");
    if (pos != std::string::npos) {
        if (pos + 9 + 8 <= req.payload.size()) {
            req.payload.replace(pos + 9, 8, "********");
        }
    }
}
```
:::

### 4.3. Порівняння плаваючих чисел та плаваючих штампів часу (Floating Point & Timestamp Diffs)

Під час реалізації модуля звіряння (Reconciler Engine) пряме порівняння рядків чи JSON-документів часто дає хибнопозитивні алерти (False Positives). Причинами є:
- Різниця у сортуванні ключів JSON в двох мовах чи бібліотеках.
- Незначні розбіжності округлення чисел з плаваючою крапкою (`100.000001` vs `100.00`).
- Генерація поточного часу (`created_at: 2026-08-18T09:40:01.002Z` vs `.003Z`).

Кастомний Reconciler повинен використовувати нормалізатор JSON-структур (Canonical JSON) та семантичне порівняння полів із допуском `epsilon` для числових величин.

### 4.4. Професійне профілювання затримок та ресурсів (Production Latency Profiling)

При проведенні тіньового запуску інженери збирають квантилі затримок (p50, p95, p99) тіньової системи порівняно з первинною. Нижче наведено схему збору та аналізу метрик у Prometheus:

```prometheus
# Метрика затримки обробки первинного трафіку
shadow_router_primary_latency_seconds_bucket{le="0.01"} 12450
shadow_router_primary_latency_seconds_bucket{le="0.05"} 15200

# Метрика затримки обробки тіньового трафіку
shadow_router_shadow_latency_seconds_bucket{le="0.01"} 11100
shadow_router_shadow_latency_seconds_bucket{le="0.05"} 14800

# Кількість виявлених розбіжностей Reconciler
shadow_router_reconciler_diff_total 0
```

Якщо метрика `shadow_router_shadow_latency_seconds_bucket` показує зростання затримки p99 більш ніж на 20% порівняно з первинною службою, реліз призупиняється для проведення відлагодження профілів виділення пам'яті (Heap Profiling) та аналізу GC pauses.
