# ⚙️ Реалізація адаптивного захисту від метастабільних петель

Захист розподіленого сервісу від метастабільних відмов вимагає розриву петель позитивного зворотного зв'язку на двох рівнях:
1. **На стороні клієнта:** жорсткий бюджет повторних спроб (Retry Budget), який забороняє клієнтам посилювати вхідний трафік більш ніж на 10% від загального обсягу запитів;
2. **На стороні сервера:** відстеження дедлайнів (Deadline Propagation), перевірка живості сокета клієнта перед початком важких обчислень та активне скидання черги (CoDel / LIFO Shedding).

## 1. Архітектура та принцип роботи бар'єрів

Коли розподілена система перебуває під загрозою колапсу, кожен запит повинен проходити через багаторівневий конвеєр валідації до того, як для нього буде виділено дорогі ресурси процесора, пам'яті або з'єднання з базою даних.

```
Клієнт (Client)                                          Сервер (Server Worker)
┌────────────────────────┐                             ┌───────────────────────────────┐
│ 1. Token Bucket        │                             │ 3. Deadline Check             │
│    Retry Budget (≤10%) │ ──── HTTP/gRPC Запит ─────> │    T_remain = Deadline - now  │
│ 2. Exponential Backoff │      + X-Request-Deadline   │    Якщо T_remain < T_exec     │
│    + Full Jitter       │                             │    -> Негайне скидання (429)  │
└────────────────────────┘                             ├───────────────────────────────┤
                                                       │ 4. Client Liveness Check      │
                                                       │    poll(EPOLLRDHUP)           │
                                                       │    Якщо сокет закрито         │
                                                       │    -> Відміна запиту до БД    │
                                                       ├───────────────────────────────┤
                                                       │ 5. CoDel Sojourn Tracker      │
                                                       │    Контроль часу в черзі      │
                                                       └───────────────────────────────┘
```

Конвеєр захисту спирається на три фундаментальні принципи:
* **Клієнтське самообмеження:** клієнтський SDK використовує модифікований токен-бакет (Token Bucket), де токени генеруються виключно в момент успішного отримання відповіді на первинний запит. Це гарантує, що у разі масового падіння бекенду генерація токенів миттєво припиняється, а клієнтський пул повторів вичерпується за лічені мілісекунди.
* **Раннє відсікання нежиттєздатних дедлайнів:** якщо запит провів у черзі занадто багато часу, його залишковий бюджет часу стає меншим за мінімально необхідний час виконання операції. Сервер не повинен навіть починати обробку такого виклику.
* **Неблокуюча діагностика розриву зв'язку:** якщо клієнт розірвав TCP-з'єднання через локальний таймаут, сокет переходить у стан очікування закриття. Сервер зобов'язаний виявити цей стан перед кожним блокуючим зверненням до бази даних або зовнішнього API.

## 2. Реалізація клієнтського та серверного захисту

Нижче наведено повністю робочі реалізації клієнтського регулятора бюджету повторів та серверного фільтра запобігання марній роботі мовами C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <time.h>
#include <poll.h>
#include <unistd.h>
#include <errno.h>

/* =========================================================================
 * 1. Клієнтський рівень: Регулятор бюджету повторних спроб (Retry Budget)
 * ========================================================================= */

typedef struct {
    atomic_int_fast64_t total_tokens;    /* Баланс доступних токенів */
    atomic_int_fast64_t max_tokens;      /* Максимальна місткість кошика */
    double retry_fraction;               /* Дозволена частка повторів (0.1 = 10%) */
} retry_budget_t;

void retry_budget_init(retry_budget_t *b, int64_t max_capacity, double fraction) {
    atomic_init(&b->total_tokens, max_capacity);
    atomic_init(&b->max_tokens, max_capacity);
    b->retry_fraction = fraction;
}

/* Викликається перед кожним звичайним первинним запитом */
void retry_budget_record_success(retry_budget_t *b) {
    int64_t tokens_to_add = (int64_t)(100.0 * b->retry_fraction);
    int64_t cur = atomic_load_explicit(&b->total_tokens, memory_order_relaxed);
    int64_t max_cap = atomic_load_explicit(&b->max_tokens, memory_order_relaxed);
    
    while (cur < max_cap) {
        int64_t next = (cur + tokens_to_add > max_cap) ? max_cap : cur + tokens_to_add;
        if (atomic_compare_exchange_weak_explicit(&b->total_tokens, &cur, next,
                                                 memory_order_release,
                                                 memory_order_relaxed)) {
            break;
        }
    }
}

/* Перевіряє, чи дозволено клієнту виконати повторний запит */
bool retry_budget_acquire(retry_budget_t *b) {
    const int64_t retry_cost = 100;
    int64_t cur = atomic_load_explicit(&b->total_tokens, memory_order_relaxed);
    
    while (cur >= retry_cost) {
        if (atomic_compare_exchange_weak_explicit(&b->total_tokens, &cur, cur - retry_cost,
                                                 memory_order_acq_rel,
                                                 memory_order_relaxed)) {
            return true; /* Дозвіл надано: списано вартість одного повтору */
        }
    }
    return false; /* Відмовлено: ліміт повторів вичерпано, захист від шторму */
}

/* =========================================================================
 * 2. Серверний рівень: Контролер дедлайнів та перевірки активності клієнта
 * ========================================================================= */

typedef struct {
    int client_socket_fd;       /* Файловий дескриптор сокета клієнта */
    uint64_t deadline_epoch_ms; /* Абсолютний дедлайн у мілісекундах */
    uint64_t min_exec_ms;       /* Мінімальний час, необхідний для обробки */
} request_guard_t;

/* Отримання поточного монотонного часу в мілісекундах */
static inline uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

void request_guard_init(request_guard_t *g, int fd, uint64_t timeout_ms, uint64_t min_exec_ms) {
    g->client_socket_fd = fd;
    g->deadline_epoch_ms = get_monotonic_ms() + timeout_ms;
    g->min_exec_ms = min_exec_ms;
}

/* Перевірка 1: Чи встигне сервер виконати операцію до дедлайну */
bool request_guard_is_deadline_viable(const request_guard_t *g) {
    uint64_t now = get_monotonic_ms();
    if (now >= g->deadline_epoch_ms) {
        return false; /* Дедлайн уже минув */
    }
    uint64_t remaining = g->deadline_epoch_ms - now;
    return (remaining >= g->min_exec_ms);
}

/* Перевірка 2: Чи не розірвав клієнт TCP-з'єднання під час очікування */
bool request_guard_is_client_alive(const request_guard_t *g) {
    if (g->client_socket_fd < 0) {
        return false;
    }
    struct pollfd pfd;
    pfd.fd = g->client_socket_fd;
    pfd.events = POLLIN | POLLHUP | POLLERR;
    pfd.revents = 0;

    int res = poll(&pfd, 1, 0); /* Миттєвий опитування без блокування */
    if (res < 0) {
        return false;
    }
    if (res > 0) {
        /* Якщо на сокеті виявлено закриття каналу або помилку */
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return false;
        }
        /* Якщо сокет сигналізує POLLIN, перевіримо чи це не EOF від клієнта */
        char peek_buf;
        ssize_t bytes = recv(g->client_socket_fd, &peek_buf, 1, MSG_PEEK | MSG_DONTWAIT);
        if (bytes == 0) {
            return false; /* Клієнт надіслав FIN-пакет (сокет закрито) */
        }
    }
    return true;
}

/* =========================================================================
 * 3. Серверний воркер з захистом від виконання марної роботи
 * ========================================================================= */

typedef enum {
    EXEC_SUCCESS = 0,
    EXEC_SHED_DEADLINE = 1,
    EXEC_SHED_CLIENT_ABORT = 2
} exec_status_t;

exec_status_t server_execute_work(request_guard_t *guard) {
    /* Етап 1: Перевірка залишкового бюджету часу перед стартом */
    if (!request_guard_is_deadline_viable(guard)) {
        return EXEC_SHED_DEADLINE; /* Миттєво відхиляємо, не витрачаючи CPU */
    }

    /* Етап 2: Перевірка сокета перед початком важкого звернення до сховища */
    if (!request_guard_is_client_alive(guard)) {
        return EXEC_SHED_CLIENT_ABORT; /* Клієнт уже відключився, робота марна */
    }

    /* Етап 3: Виконання корисної роботи (імітація звернення до БД) */
    usleep(20000); /* 20 мілісекунд корисної обробки */

    /* Етап 4: Повторна перевірка сокета перед формуванням важкої відповіді */
    if (!request_guard_is_client_alive(guard)) {
        return EXEC_SHED_CLIENT_ABORT;
    }

    return EXEC_SUCCESS;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <atomic>
#include <expected>
#include <algorithm>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

namespace resilience {

using MonotonicClock = std::chrono::steady_clock;
using TimePoint = MonotonicClock::time_point;
using Milliseconds = std::chrono::milliseconds;

/* =========================================================================
 * 1. Клієнтський рівень: Регулятор бюджету повторних спроб (Retry Budget)
 * ========================================================================= */

class RetryBudget {
public:
    explicit RetryBudget(int64_t max_tokens = 1000, double retry_fraction = 0.1)
        : total_tokens_(max_tokens),
          max_tokens_(max_tokens),
          retry_fraction_(retry_fraction) {}

    // Викликається після успішного первинного запиту для наповнення бюджету
    void record_success() noexcept {
        const int64_t add = static_cast<int64_t>(100.0 * retry_fraction_);
        int64_t cur = total_tokens_.load(std::memory_order_relaxed);
        while (cur < max_tokens_) {
            const int64_t next = std::min(max_tokens_, cur + add);
            if (total_tokens_.compare_exchange_weak(cur, next, 
                                                    std::memory_order_release, 
                                                    std::memory_order_relaxed)) {
                break;
            }
        }
    }

    // Спроба отримати дозвіл на повторний запит (списання 100 токенів)
    [[nodiscard]] bool try_acquire_retry() noexcept {
        constexpr int64_t kRetryCost = 100;
        int64_t cur = total_tokens_.load(std::memory_order_relaxed);
        while (cur >= kRetryCost) {
            if (total_tokens_.compare_exchange_weak(cur, cur - kRetryCost, 
                                                    std::memory_order_acq_rel, 
                                                    std::memory_order_relaxed)) {
                return true; // Дозвіл надано
            }
        }
        return false; // Бюджет вичерпано, блокуємо каскадне множення навантаження
    }

private:
    std::atomic<int64_t> total_tokens_;
    int64_t max_tokens_;
    double retry_fraction_;
};

/* =========================================================================
 * 2. Серверний рівень: RAII-вартовий дедлайну та стану з'єднання
 * ========================================================================= */

enum class ShedReason {
    DeadlineExceeded,
    ClientDisconnected
};

class RequestGuard {
public:
    RequestGuard(int socket_fd, Milliseconds timeout, Milliseconds min_exec_time)
        : socket_fd_(socket_fd),
          deadline_(MonotonicClock::now() + timeout),
          min_exec_time_(min_exec_time) {}

    // Перевірка 1: Чи достатньо часу залишається до закінчення дедлайну
    [[nodiscard]] bool is_viable() const noexcept {
        const auto now = MonotonicClock::now();
        if (now >= deadline_) {
            return false;
        }
        return (deadline_ - now) >= min_exec_time_;
    }

    // Перевірка 2: Неблокуюча діагностика відключення клієнта
    [[nodiscard]] bool is_client_connected() const noexcept {
        if (socket_fd_ < 0) {
            return false;
        }
        pollfd pfd{socket_fd_, POLLIN | POLLHUP | POLLERR, 0};
        int res = ::poll(&pfd, 1, 0);
        if (res < 0) return false;

        if (res > 0) {
            if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
                return false;
            }
            char peek_byte;
            ssize_t n = ::recv(socket_fd_, &peek_byte, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return false; // Отримано EOF (FIN-пакет)
            }
        }
        return true;
    }

    [[nodiscard]] Milliseconds remaining_time() const noexcept {
        const auto now = MonotonicClock::now();
        if (now >= deadline_) return Milliseconds{0};
        return std::chrono::duration_cast<Milliseconds>(deadline_ - now);
    }

private:
    int socket_fd_;
    TimePoint deadline_;
    Milliseconds min_exec_time_;
};

/* =========================================================================
 * 3. Серверний обробник з використанням std::expected
 * ========================================================================= */

struct ExecutionResult {
    uint64_t processed_items;
    Milliseconds time_taken;
};

std::expected<ExecutionResult, ShedReason> 
process_client_request(const RequestGuard& guard) {
    // 1. Бар'єр дедлайну на вході
    if (!guard.is_viable()) {
        return std::unexpected(ShedReason::DeadlineExceeded);
    }

    // 2. Бар'єр відключення перед зверненням до бази даних
    if (!guard.is_client_connected()) {
        return std::unexpected(ShedReason::ClientDisconnected);
    }

    // 3. Імітація корисної роботи
    const auto start = MonotonicClock::now();
    ::usleep(20000); // 20 ms
    const auto duration = std::chrono::duration_cast<Milliseconds>(MonotonicClock::now() - start);

    // 4. Повторна верифікація перед фіксацією стану
    if (!guard.is_client_connected()) {
        return std::unexpected(ShedReason::ClientDisconnected);
    }

    return ExecutionResult{
        .processed_items = 42,
        .time_taken = duration
    };
}

} // namespace resilience
```
:::

## 3. Покрокове трасування обробки запиту

Розглянемо послідовність дій під час проходження запиту крізь серверний фільтр стійкості:

1. **Ініціалізація та парсинг дедлайну:** під час прийняття з'єднання або вичитування HTTP/gRPC заголовків сервер витягує заголовок `X-Request-Deadline-Ms` або `grpc-timeout`. Структура `RequestGuard` фіксує абсолютний час дедлайну за допомогою системного таймера `CLOCK_MONOTONIC`.
2. **Фаза ранньої фільтрації (Pre-execution Gate):** воркер витягує завдання з черги. Якщо час очікування в черзі з'їв майже весь бюджет (`T_remain < T_min_exec`), метод `is_viable()` повертає `false`. Запит негайно завершується з кодом HTTP 504 або gRPC `DEADLINE_EXCEEDED` без виділення пулів пам'яті чи потоків бази даних.
3. **Неблокуючий зріз сокета (Socket Liveness Probe):** виклик `poll()` з нульовим таймаутом перевіряє стан файлового дескриптора. Якщо клієнт розірвав зв'язок за таймаутом, стек TCP надсилає пакет `FIN` або `RST`. Прапорець `POLLHUP` або виклик `recv(..., MSG_PEEK)` з нульовим результатом фіксує обрив, що дозволяє миттєво скасувати виконання.
4. **Контроль стану після тривалих операцій:** у розподілених транзакціях між окремими кроками (наприклад, між читанням з кешу та записом у базу даних) вартовий повторно викликає перевірку активності сокета, гарантуючи, що мутації стану не виконуються для відкинутих запитів.

## 4. Типові інженерні пастки та крайові випадки

1. **Ігнорування `MSG_PEEK` при опитуванні дескриптора сокета:** якщо сервер викликає `poll()` і бачить подію `POLLIN`, це може свідчити як про надходження нових даних, так і про закриття каналу клієнтом. Коли віддалена сторона викликає `close()`, ядро Linux переводить сокет у стан `CLOSE_WAIT` та записує в буфер ознаку кінця файлу (`EOF`). Простий `poll()` повертає готовність до читання, і лише виклик `recv(..., MSG_PEEK)` з результатом `0` однозначно вказує на розрив сесії.
2. **Неатомарне поповнення токенів у Retry Budget:** за умов високої паралельності сотні потоків одночасно намагаються збільшити лічильник доступних токенів. Використання звичайного додавання замість атомарного циклу `compare_exchange` призводить до стану гонки (Race Condition). В результаті баланс токенів може перевищити максимальний ліміт `max_tokens`, дозволяючи клієнтам згенерувати руйнівний шторм повторів.
3. **Використання системного годинника `CLOCK_REALTIME` замість `CLOCK_MONOTONIC`:** реальний астрономічний час операційної системи може зазнавати стрибків вперед або назад через коригування демоном NTP або високоточні стрибки секунд (Leap Seconds). Якщо системний час стрибне назад на 1 секунду, всі дедлайни подовжаться, заблокувавши скидання навантаження; якщо вперед — система безпідставно відхилить усі живі клієнтські запити.
4. **Проблема напівзакритих з'єднань (TCP Half-Closed Connections):** у разі падіння проміжного балансувальника або маршрутизатора сокет на сервері може залишатися у стані `ESTABLISHED` без надходження пакетів `FIN` або `RST`. Для виявлення таких мертвих з'єднань обов'язково налаштовуються опції ядра `SO_KEEPALIVE`, `TCP_KEEPIDLE` (наприклад, 5 секунд) та `TCP_KEEPINTVL` (1 секунда).
5. **Вкрадений час у віртуалізованих середовищах (vCPU Steal Time):** у хмарних віртуальних машинах (AWS EC2, GCP Compute Engine) гіпервізор може тимчасово забирати фізичні процесорні такти для обслуговування сусідніх віртуальних машин (Noisy Neighbor). Це призводить до раптового локального стрибка часу виконання операції. Параметр `min_exec_time` повинен враховувати 95-й перцентиль затримки, а не ідеальний час виконання на виділеному залізі.
