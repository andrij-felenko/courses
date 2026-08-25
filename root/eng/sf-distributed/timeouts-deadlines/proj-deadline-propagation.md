# ⚙️ Реалізація наскрізного прокидання дедлайну та бюджету часу

Коли мікросервіс отримує запит і викликає кілька залежних служб, використання статичних сокетних таймаутів призводить до неконтрольованого роздуття часу та «зомбі-обчислень». Надійна система вимагає наскрізного контексту дедлайну: від моменту отримання HTTP/gRPC заголовка час невпинно тане на монотонному годиннику, кожен підвиклик затискається в залишок загального бюджету, а при спливі строку виконання скасовується негайно на всіх рівнях.

## Задача: наскрізний часовий контекст для розподіленого клієнта й сервера

Побудуємо закінчену бібліотеку розподіленого бюджетування часу, яка забезпечує:
1. **Фіксацію дедлайну на монотонному годиннику:** захист від стрибків настінного системного часу при синхронізації NTP.
2. **Серіалізацію та розбір заголовка:** читання й формування стандартного заголовка `X-Request-Deadline-Ms` (або `grpc-timeout`).
3. **Ранній контроль черги (Admission Check):** миттєву відмову (`Fail Fast`), якщо час вичерпано ще до виходу запиту з черги обробника.
4. **Затискання підзапитів (Subcall Clamping):** розрахунок `min(налаштований_ліміт, залишок − запас)` для дочірніх RPC.
5. **Неблокуюче встановлення з'єднання з дедлайном:** захист від 75-секундного зависання на системному виклику `connect()`.
6. **Сокетні операції з дедлайном:** читання та запис через системний виклик `poll()` із динамічним таймаутом, що зменшується в міру отримання байтів.
7. **Зворотне скасування (Cancellation Signaling):** сповіщення віддаленого сервера про обрив через кадри скасування або закриття каналу.
8. **Прокидання дедлайну в базу даних:** динамічне налаштування `statement_timeout` та `lock_timeout` для запобігання дедлокам.

## Чому контекст дедлайну має бути незмінним і легковажним

У розподілених серверах обробка запиту проходить крізь десятки функцій та асинхронних задач. Якщо контекст дедлайну вимагає динамічного виділення пам'яті в купі (`malloc` / `heap allocation`) при кожному виклику, навантаження на алокатор пам'яті та збирач сміття стає відчутним вузьким місцем.

Тому фундаментальна вимога до структури контексту дедлайну — **повне розміщення на стеку (Zero-Allocation Value Semantics)**:
- У мові C структура `deadline_context_t` займає лише 24 байти (два 64-бітних цілих і прапорець) і передається у функції за константним вказівником або копіюванням у регістрах процесора.
- У мові C++ клас `DeadlineContext` інкапсулює часову точку `std::chrono::steady_clock::time_point` та джерело скасування `std::stop_source` (введене у стандарті C++20), що дозволяє неблокуюче сповіщення кількох потоків без важких м'ютексів.

### Вибір системного годинника: монотонний проти настінного

Для вимірювання дедлайнів усередині операційної системи Linux існують кілька таймерів:
1. `CLOCK_REALTIME` (настінний час): повертає астрономічний час від 1 січня 1970 року (Unix Epoch). Цей годинник **категорично заборонено** використовувати для таймаутів: служба NTP може перевести його назад, через що віднімання `deadline - now` дасть від'ємне або надто велике значення.
2. `CLOCK_MONOTONIC`: монотонний таймер, що лінійно зростає від моменту завантаження системи. Він не стрибає назад за жодних умов, хоча швидкість його ходу може плавно коригуватися демоном `chrony` чи `ntpd`.
3. `CLOCK_MONOTONIC_RAW`: апаратний таймер, який не піддається жодним програмним коригуванням частоти.
4. `CLOCK_BOOTTIME`: монотонний таймер, який на відміну від `CLOCK_MONOTONIC` продовжує рахувати час навіть тоді, коли ядро операційної системи перебуває в стані сну (suspend).

У більшості серверних застосунків стандартом є `CLOCK_MONOTONIC` (або `std::chrono::steady_clock`), який забезпечує субмікросекундну точність без ризику часових стрибків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>

/* Отримання поточного монотонного часу в мілісекундах */
static inline int64_t monotonic_now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (int64_t)(ts.tv_nsec / 1000000);
}

/* Структура контексту дедлайну */
typedef struct {
    int64_t deadline_ms;       /* Абсолютна часова мітка на монотонному годиннику */
    int64_t safety_margin_ms;  /* Запас на серіалізацію та зворотну передачу */
    bool is_cancelled;         /* Прапорець явного скасування */
} deadline_context_t;

/* Створення кореневого контексту з тривалістю в мілісекундах */
deadline_context_t context_with_timeout(int64_t timeout_ms, int64_t margin_ms) {
    deadline_context_t ctx;
    ctx.deadline_ms = monotonic_now_ms() + timeout_ms;
    ctx.safety_margin_ms = margin_ms;
    ctx.is_cancelled = false;
    return ctx;
}

/* Отримання залишку доступного часу в мілісекундах */
int64_t context_remaining_ms(const deadline_context_t *ctx) {
    if (ctx->is_cancelled) {
        return 0;
    }
    int64_t now = monotonic_now_ms();
    if (now >= ctx->deadline_ms) {
        return 0;
    }
    return ctx->deadline_ms - now;
}

/* Перевірка, чи не вичерпано дедлайн */
bool context_is_expired(const deadline_context_t *ctx) {
    return context_remaining_ms(ctx) <= 0;
}

/* Ручне скасування контексту */
void context_cancel(deadline_context_t *ctx) {
    ctx->is_cancelled = true;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <optional>
#include <string_view>
#include <charconv>
#include <stop_token>
#include <cstdint>
#include <span>
#include <mutex>
#include <condition_variable>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

class DeadlineContext {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;
    using Milliseconds = std::chrono::milliseconds;

    /* Створення кореневого контексту з таймаутом і запасом */
    explicit DeadlineContext(Milliseconds timeout, Milliseconds margin = Milliseconds(10))
        : deadline_(Clock::now() + timeout), margin_(margin), stop_source_() {}

    /* Контекст із готовим абсолютним дедлайном */
    explicit DeadlineContext(TimePoint deadline, Milliseconds margin = Milliseconds(10))
        : deadline_(deadline), margin_(margin), stop_source_() {}

    /* Залишок часу до спливу дедлайну */
    [[nodiscard]] Milliseconds remaining() const noexcept {
        if (stop_source_.stop_requested()) {
            return Milliseconds::zero();
        }
        const auto now = Clock::now();
        if (now >= deadline_) {
            return Milliseconds::zero();
        }
        return std::chrono::duration_cast<Milliseconds>(deadline_ - now);
    }

    [[nodiscard]] bool is_expired() const noexcept {
        return remaining() <= Milliseconds::zero();
    }

    [[nodiscard]] TimePoint deadline() const noexcept { return deadline_; }
    [[nodiscard]] Milliseconds margin() const noexcept { return margin_; }
    [[nodiscard]] std::stop_token stop_token() const noexcept { return stop_source_.get_token(); }

    void cancel() noexcept {
        stop_source_.request_stop();
    }

private:
    TimePoint deadline_;
    Milliseconds margin_;
    std::stop_source stop_source_;
};
```
:::

## Серіалізація та відновлення дедлайну на межі мережі

При передачі інформації про дедлайн через кордони сервісів мережевий протокол має дотримуватися трьох критичних вимог:
1. **Передавати відносну тривалість, а не абсолютний час:** годинники двох серверів мають неминуче зміщення (NTP clock skew). Передача абсолютного часу призвела б до спотворення дедлайну на величину цього зміщення. Передача відносного залишку (наприклад, `200` мс) дозволяє кожному вузлу прив'язати дедлайн до власного монотонного годинника.
2. **Враховувати час транзиту (Network Flight Time):** якщо запит летів через завантажену мережу 15 мс, сервер після розбору має зменшити отриманий залишок на оцінку половини RTT.
3. **Захищатися від переповнення цілих чисел:** некоректний або шкідливий заголовок (наприклад, `X-Request-Deadline-Ms: 999999999999999999`) при додаванні до поточного часу процесора може спричинити переповнення знакового 64-бітного числа (`signed integer overflow`), що в мовах C і C++ є невизначеною поведінкою (UB) і призводить до від'ємного часу.

У специфікації gRPC для цього використовується заголовок `grpc-timeout` із суфіксами одиниць виміру (`H` — години, `M` — хвилини, `S` — секунди, `m` — мілісекунди, `u` — мікросекунди, `n` — наносекунди). У нашому прикладі реалізовано надійний розбір числового мілісекундного заголовка з перевіркою меж і помилок перетворення.

:::tabs
```c
/* Формування HTTP-заголовка з залишком бюджету */
int serialize_deadline_header(const deadline_context_t *ctx, char *out_buf, size_t buf_size) {
    int64_t remain = context_remaining_ms(ctx);
    if (remain <= 0) {
        return -1; /* Бюджет вичерпано */
    }
    return snprintf(out_buf, buf_size, "X-Request-Deadline-Ms: %lld", (long long)remain);
}

/* Розбір заголовка на боці сервера та ініціалізація серверного контексту */
bool parse_deadline_header(const char *header_value, int64_t network_rtt_est_ms,
                           int64_t default_timeout_ms, deadline_context_t *out_ctx) {
    if (!header_value || *header_value == '\0') {
        /* Заголовка немає — застосовуємо дефолтний таймаут */
        *out_ctx = context_with_timeout(default_timeout_ms, 10);
        return true;
    }

    char *endptr = NULL;
    errno = 0;
    long long remain_ms = strtoll(header_value, &endptr, 10);
    if (errno != 0 || endptr == header_value || remain_ms <= 0) {
        return false;
    }

    /* Віднімаємо оцінку половини RTT на час польоту пакета */
    int64_t effective_remain = (int64_t)remain_ms - (network_rtt_est_ms / 2);
    if (effective_remain <= 0) {
        /* Запит летів довше, ніж жив дедлайн */
        out_ctx->deadline_ms = monotonic_now_ms();
        out_ctx->safety_margin_ms = 10;
        out_ctx->is_cancelled = true;
        return true;
    }

    out_ctx->deadline_ms = monotonic_now_ms() + effective_remain;
    out_ctx->safety_margin_ms = 10;
    out_ctx->is_cancelled = false;
    return true;
}
```
```cpp
/* Формування значення заголовка з залишком часу */
std::optional<std::string> serialize_deadline(const DeadlineContext& ctx) {
    const auto rem = ctx.remaining().count();
    if (rem <= 0) {
        return std::nullopt;
    }
    return std::to_string(rem);
}

/* Розбір заголовка на сервері та побудова контексту */
std::optional<DeadlineContext> parse_deadline(std::string_view header_val,
                                             std::chrono::milliseconds rtt_estimate,
                                             std::chrono::milliseconds default_timeout) {
    if (header_val.empty()) {
        return DeadlineContext(default_timeout);
    }

    int64_t remain_ms = 0;
    const auto [ptr, ec] = std::from_chars(header_val.data(),
                                           header_val.data() + header_val.size(),
                                           remain_ms);
    if (ec != std::errc() || remain_ms <= 0) {
        return std::nullopt;
    }

    auto effective = std::chrono::milliseconds(remain_ms) - (rtt_estimate / 2);
    if (effective <= std::chrono::milliseconds::zero()) {
        /* Дедлайн вичерпано ще під час транзиту пакета */
        DeadlineContext expired_ctx(std::chrono::milliseconds::zero());
        expired_ctx.cancel();
        return expired_ctx;
    }

    return DeadlineContext(effective);
}
```
:::

## Неблокуюче встановлення TCP-з'єднання з дедлайном

Мало хто з розробників знає, що класичний системний виклик `connect()` на блокуючому сокеті не має власного параметра таймауту. Якщо цільовий сервер вимкнено з розетки або проміжний маршрутизатор мовчки дропає TCP SYN пакети, виклик `connect()` блокуватиме потік операційної системи до **75 секунд** (стандартна тривалість ретрансмісій TCP SYN за RFC 1122).

Щоб підпорядкувати фазу з'єднання загальному бюджету часу:
1. Сокет переводиться в неблокуючий режим через `fcntl(fd, F_SETFL, O_NONBLOCK)`.
2. Викликається `connect()`. Він негайно повертає `-1` з помилкою `EINPROGRESS` (з'єднання ініційовано, але очікує підтвердження SYN-ACK).
3. Очікування завершення рукостискання здійснюється через `poll()` з подією `POLLOUT` і таймаутом, рівним залишку дедлайну.
4. Після спрацювання `poll()` перевіряється опція `getsockopt(fd, SOL_SOCKET, SO_ERROR, ...)`, щоб переконатися, що з'єднання встановлено успішно, а не відкинуто пакетом TCP RST.

:::tabs
```c
/* Встановлення TCP з'єднання з жорстким контролем дедлайну */
int connect_with_deadline(int sock_fd, const struct sockaddr *addr, socklen_t addrlen,
                          const deadline_context_t *ctx) {
    /* Переводимо сокет у неблокуючий режим */
    int flags = fcntl(sock_fd, F_GETFL, 0);
    fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

    int ret = connect(sock_fd, addr, addrlen);
    if (ret == 0) {
        return 0; /* З'єднання встановлено миттєво (локальний сокет) */
    }

    if (errno != EINPROGRESS) {
        return -1; /* Миттєва помилка маршрутизації */
    }

    int64_t remain_ms = context_remaining_ms(ctx);
    if (remain_ms <= 0) {
        errno = ETIMEDOUT;
        return -1;
    }

    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLOUT;
    pfd.revents = 0;

    ret = poll(&pfd, 1, (int)remain_ms);
    if (ret <= 0) {
        errno = (ret == 0) ? ETIMEDOUT : errno;
        return -1;
    }

    /* Перевірка помилки сокета після готовності POLLOUT */
    int sock_err = 0;
    socklen_t err_len = sizeof(sock_err);
    if (getsockopt(sock_fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) < 0 || sock_err != 0) {
        errno = (sock_err != 0) ? sock_err : ECOMM;
        return -1;
    }

    return 0; /* TCP-з'єднання успішно встановлено в межах бюджету */
}
```
```cpp
/* Неблокуючий connect із дедлайном на C++ */
bool connect_with_deadline(int sock_fd, const struct sockaddr* addr, socklen_t addrlen,
                           const DeadlineContext& ctx) {
    const int flags = ::fcntl(sock_fd, F_GETFL, 0);
    ::fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

    if (::connect(sock_fd, addr, addrlen) == 0) {
        return true;
    }

    if (errno != EINPROGRESS) {
        return false;
    }

    const auto remain = ctx.remaining();
    if (remain <= std::chrono::milliseconds::zero()) {
        return false;
    }

    struct pollfd pfd{sock_fd, POLLOUT, 0};
    const int timeout_ms = static_cast<int>(remain.count());
    const int ret = ::poll(&pfd, 1, timeout_ms);

    if (ret <= 0) {
        return false;
    }

    int sock_err = 0;
    socklen_t err_len = sizeof(sock_err);
    if (::getsockopt(sock_fd, SOL_SOCKET, ERROR_PARAM, &sock_err, &err_len) < 0 || sock_err != 0) {
        return false;
    }

    return true;
}
```
:::

## Затискання підзапитів (Subcall Clamping) та відсікання безнадійних викликів

Коли сервер виконує бізнес-логіку і готується викликати дочірній мікросервіс (наприклад, базу даних або платіжний шлюз), виникає ключова математична операція розподіленого бюджетування: **затискання (clamping)**.

У конфігурації клієнта для кожного методу прописано статичний максимальний таймаут (наприклад, «платіжний шлюз має ліміт 500 мс»). Але якщо від клієнтського бюджету після попередніх кроків залишилося лише 140 мс, сервер **не має права** виділяти підзапиту 500 мс. Він обчислює фактичний таймаут:

```
T_subcall = min( T_configured, T_remain − T_margin )
```

Якщо `T_subcall` виявляється меншим за мінімальний час встановлення з'єднання та проходження пакетів у мережі (`min_viable_rtt`, наприклад 15 мс), функція `derive_subcall_context` повертає відмову ще до відкриття сокета. Це рятує систему від витрат на марні мережеві запити, відповідь на які гарантовано запізниться.

:::tabs
```c
/* Створення затиснутого дочірнього контексту для підзапиту */
bool create_subcall_context(const deadline_context_t *parent_ctx,
                            int64_t configured_subcall_timeout_ms,
                            int64_t min_viable_rtt_ms,
                            deadline_context_t *out_subcall_ctx) {
    int64_t parent_remain = context_remaining_ms(parent_ctx);

    /* Віднімаємо запас батьківського контексту */
    int64_t available = parent_remain - parent_ctx->safety_margin_ms;

    /* Якщо залишок менший за мінімальний мережевий RTT — підзапит безнадійний */
    if (available < min_viable_rtt_ms) {
        return false; /* Fail Fast: не робимо виклик */
    }

    /* Таймаут підзапиту — мінімум між конфігурацією та доступним залишком */
    int64_t subcall_timeout = configured_subcall_timeout_ms;
    if (subcall_timeout > available) {
        subcall_timeout = available;
    }

    *out_subcall_ctx = context_with_timeout(subcall_timeout, parent_ctx->safety_margin_ms);
    return true;
}
```
```cpp
/* Створення дочірнього контексту з динамічним затисканням */
std::optional<DeadlineContext> derive_subcall_context(
    const DeadlineContext& parent,
    std::chrono::milliseconds configured_limit,
    std::chrono::milliseconds min_viable_rtt = std::chrono::milliseconds(10)) {

    const auto parent_rem = parent.remaining();
    const auto available = parent_rem - parent.margin();

    /* Якщо часу не вистачить навіть на мережевий раунд-тріп — відмовляємося */
    if (available < min_viable_rtt) {
        return std::nullopt;
    }

    const auto subcall_limit = std::min(configured_limit, available);
    return DeadlineContext(subcall_limit, parent.margin());
}
```
:::

## Сокетне читання з дедлайном через `poll()`

Більшість класичних мережевих програм використовують блокуючі сокети з опцією `SO_RCVTIMEO`. Проте цей підхід має фатальну вразливість: `SO_RCVTIMEO` скидається в нуль щоразу, коли ядро операційної системи отримує з мережі хоча б один байт даних. Зловмисник або нестабільний сервер, надсилаючи по одному байту кожні 4 секунди при таймауті 5 секунд, може утримувати з'єднання відкритим нескінченно довго.

Правильна реалізація читання потоку даних з дедлайном спирається на три принципи:
1. Сокет переводиться в неблокуючий режим (`MSG_DONTWAIT` або `O_NONBLOCK`).
2. Перед кожним очікуванням даних через системний виклик `poll()` таймаут обчислюється наново як `context_remaining_ms(ctx)`.
3. Якщо `poll()` повертає готовність до читання, програма зчитує доступні байти через `recv()`, зменшує лічильник залишку байтів `bytes_left` і повторює цикл, перераховуючи дедлайн.

Якщо під час очікування надходить сигнал операційної системи (`errno == EINTR`), програма не здається і не скидає таймер: вона повертається до перевірки монотонного годинника і продовжує очікування на залишок доступного часу.

:::tabs
```c
/* Читання рівно n байтів із сокета з жорстким дотриманням дедлайну */
int read_exact_with_deadline(int sock_fd, void *buf, size_t count, const deadline_context_t *ctx) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t bytes_left = count;

    while (bytes_left > 0) {
        int64_t remain_ms = context_remaining_ms(ctx);
        if (remain_ms <= 0) {
            errno = ETIMEDOUT;
            return -1; /* Дедлайн сплив під час читання */
        }

        struct pollfd pfd;
        pfd.fd = sock_fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int ret = poll(&pfd, 1, (int)remain_ms);
        if (ret < 0) {
            if (errno == EINTR) {
                continue; /* Переривання сигналом — перевіряємо час і повторюємо */
            }
            return -1;    /* Системна помилка */
        }
        if (ret == 0) {
            errno = ETIMEDOUT;
            return -1;    /* Таймаут poll */
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            errno = ECONNRESET;
            return -1;
        }

        if (pfd.revents & POLLIN) {
            ssize_t n = recv(sock_fd, ptr, bytes_left, MSG_DONTWAIT);
            if (n < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) {
                    continue;
                }
                return -1;
            }
            if (n == 0) {
                errno = ECONNABORTED; /* Передчасне закриття сокета іншим боком */
                return -1;
            }
            ptr += n;
            bytes_left -= n;
        }
    }
    return 0; /* Усі байти успішно зчитано в межах бюджету */
}
```
```cpp
/* RAII обгортка над сокетом */
class UniqueSocket {
public:
    explicit UniqueSocket(int fd) noexcept : fd_(fd) {}
    ~UniqueSocket() { if (fd_ >= 0) ::close(fd_); }
    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;
    UniqueSocket(UniqueSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
private:
    int fd_;
};

/* Читання точної кількості байтів у межах дедлайну */
bool read_exact(int sock_fd, std::span<uint8_t> buffer, const DeadlineContext& ctx) {
    size_t offset = 0;
    while (offset < buffer.size()) {
        const auto remain = ctx.remaining();
        if (remain <= std::chrono::milliseconds::zero()) {
            return false; /* Час вичерпано */
        }

        struct pollfd pfd{sock_fd, POLLIN, 0};
        const int timeout_ms = static_cast<int>(remain.count());
        const int ret = ::poll(&pfd, 1, timeout_ms);

        if (ret < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (ret == 0) {
            return false; /* Таймаут poll */
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            return false;
        }

        if (pfd.revents & POLLIN) {
            const ssize_t n = ::recv(sock_fd, buffer.data() + offset,
                                     buffer.size() - offset, MSG_DONTWAIT);
            if (n < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
                return false;
            }
            if (n == 0) {
                return false; /* Обрив зв'язку */
            }
            offset += static_cast<size_t>(n);
        }
    }
    return true;
}
```
:::

## Очікування з'єднання в пулі (Connection Pool Checkout)

Мережеві виклики починаються не з відправки байтів у сокет, а з отримання вільного TCP-з'єднання з локального пулу (`connection pool`). Якщо всі з'єднання пулу зайняті паралельними запитами, потік стає в чергу очікування.

Поширена архітектурна помилка полягає у використанні нескінченного блокування на м'ютексі чи умовній змінній пулу. Якщо бекенд перевантажений і повільно віддає з'єднання, сотні робочих потоків зависають у черзі до пулу, навіть якщо їхній клієнтський дедлайн уже сплив.

Правильна реалізація очікування підпорядковує взяття з'єднання загальному бюджету часу:

:::tabs
```c
/* Отримання з'єднання з пулу з контролем дедлайну */
int acquire_connection_with_deadline(pthread_mutex_t *pool_lock,
                                     pthread_cond_t *pool_cond,
                                     int *pool_slots_available,
                                     const deadline_context_t *ctx) {
    pthread_mutex_lock(pool_lock);

    while (*pool_slots_available <= 0) {
        int64_t remain_ms = context_remaining_ms(ctx);
        if (remain_ms <= 0) {
            pthread_mutex_unlock(pool_lock);
            errno = ETIMEDOUT;
            return -1; /* Час у черзі пулу вичерпано */
        }

        /* Переведення залишку мілісекунд в абсолютний таймспек на CLOCK_REALTIME */
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += remain_ms / 1000;
        ts.tv_nsec += (remain_ms % 1000) * 1000000;
        if (ts.tv_nsec >= 1000000000) {
            ts.tv_sec += 1;
            ts.tv_nsec -= 1000000000;
        }

        int ret = pthread_cond_timedwait(pool_cond, pool_lock, &ts);
        if (ret == ETIMEDOUT) {
            pthread_mutex_unlock(pool_lock);
            errno = ETIMEDOUT;
            return -1;
        }
    }

    (*pool_slots_available)--;
    pthread_mutex_unlock(pool_lock);
    return 0; /* З'єднання успішно виділено */
}
```
```cpp
/* Отримання ресурсу з пулу з перевіркою дедлайну */
bool acquire_connection(std::mutex& pool_mtx,
                        std::condition_variable& pool_cv,
                        int& available_slots,
                        const DeadlineContext& ctx) {
    std::unique_lock<std::mutex> lock(pool_mtx);

    const auto predicate = [&] { return available_slots > 0; };
    while (!predicate()) {
        const auto remain = ctx.remaining();
        if (remain <= std::chrono::milliseconds::zero()) {
            return false; /* Дедлайн вичерпано під час очікування в пулі */
        }

        if (pool_cv.wait_for(lock, remain) == std::cv_status::timeout) {
            return false;
        }
    }

    --available_slots;
    return true;
}
```
:::

## Зворотне скасування (Cancellation Signaling) та звільнення ресурсів

Коли клієнтський таймаут спливає або користувач закриває сторінку браузера, клієнт розриває зв'язок. Проте сервер, якщо він не перевіряє стан мережевого дескриптора під час виконання обчислень, продовжує виконувати «зомбі-роботу».

Для усунення цієї проблеми в сучасних протоколах застосовують два рівні скасування:
1. **Протокольний сигнал скасування:** у мультиплексованих протоколах (HTTP/2, HTTP/3, gRPC) клієнт надсилає окремий кадр `RST_STREAM` із кодом `CANCELLED`. Це дозволяє скасувати конкретний логічний потік без закриття спільного TCP-з'єднання, на якому паралельно працюють десятки інших запитів.
2. **Асинхронний моніторинг обриву сокета:** якщо сервер виконує тривале дискове читання або запит до бази даних, він підписується на подію `POLLRDHUP` (або `EPOLLRDHUP` у ядрі Linux). Щойно інший бік закриває напрямок запису, ядро генерує подію `POLLRDHUP`, серверний контекст негайно викликає `context_cancel(ctx)`, і транзакція в базі даних негайно відкочується (`ROLLBACK`).

:::tabs
```c
/* Перевірка, чи не закрив клієнт сокет під час виконання запиту */
bool is_socket_peer_closed(int sock_fd) {
    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLIN | POLLHUP;
    pfd.revents = 0;

    int ret = poll(&pfd, 1, 0); /* Миттєвий неблокуючий замір (таймаут 0) */
    if (ret > 0) {
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return true; /* Клієнт розірвав з'єднання */
        }
        /* Якщо сокет готовий до читання, перевіряємо чи це EOF (0 байтів) */
        if (pfd.revents & POLLIN) {
            char peek_buf[1];
            ssize_t n = recv(sock_fd, peek_buf, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return true; /* FIN отримано від клієнта */
            }
        }
    }
    return false;
}
```
```cpp
/* Перевірка закриття з'єднання клієнтом */
bool is_client_disconnected(int sock_fd) noexcept {
    struct pollfd pfd{sock_fd, POLLIN | POLLHUP, 0};
    const int ret = ::poll(&pfd, 1, 0);
    if (ret > 0) {
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return true;
        }
        if (pfd.revents & POLLIN) {
            char peek_byte = 0;
            const ssize_t n = ::recv(sock_fd, &peek_byte, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return true;
            }
        }
    }
    return false;
}
```
:::

## Прокидання дедлайну в реляційні бази даних

Коли запит виконує SQL-транзакцію, він може зависнути не в мережі, а на очікуванні блокування рядка (`row lock`) або перевантаженому диску бази даних. Якщо HTTP-клієнт обірвав з'єднання через дедлайн, відкрита транзакція в базі продовжує утримувати блокування, блокуючи інші транзакції.

Для запобігання «транзакційному тромбу» клієнт бази даних перед виконанням SQL-запиту зобов'язаний встановити таймаути всередині сесії СУБД:

```sql
-- PostgreSQL: динамічне встановлення лімітів на основі залишку контексту
SET LOCAL statement_timeout = '250ms';
SET LOCAL lock_timeout = '100ms';
```

Якщо виконання SQL-запиту перевищує 250 мс, рушій PostgreSQL самостійно генерує помилку `57014 (query_canceled)`, відкочує всі незбережені зміни транзакції та негайно вивільняє блокування рядків і пам'ять буферів, унеможливлюючи утворення дедлоків. У клієнтських бібліотеках на C/C++ (таких як `libpq`) для цього використовується виклик `PQcancel()`, який посилає асинхронний сигнал переривання по окремому сокету керування базою даних.

## Повний ланцюжок: конвеєр обробки з відсіканням на кожному кроці

Зберемо повний приклад обробника запиту `PlaceOrder`, який демонструє покроковий захист від каскадного зависання.

Конвеєр складається з кількох послідовних етапів:
1. Запит надходить від клієнта із загальним бюджетом 150 мс.
2. Запит проводить 50 мс у черзі потоків сервера перед початком обробки. Сервер перераховує залишок: залишилося 100 мс.
3. Сервер виконує підвиклик до `AuthService` (статичний ліміт 100 мс). Залишок бюджету дозволяє виклик, виконання займає 40 мс. Залишок падає до 60 мс.
4. Сервер виконує підвиклик до `PaymentService` (статичний ліміт 100 мс). Функція затискання автоматично обмежує виклик залишком `min(100, 60 − 10) = 50` мс. Платіж успішно проходить за 40 мс. Залишок падає до 20 мс.
5. Сервер готується викликати `NotificationService` (ліміт 80 мс). Але доступний залишок `20 − 10 = 10` мс є меншим за мінімальний поріг `min_viable_rtt` (15 мс). Функція `derive_subcall_context` миттєво повертає відмову, і сервер перемикається на асинхронну чергу сповіщень, успішно повертаючи відповідь клієнту до настання 150-ї мілісекунди.

:::tabs
```c
/* Імітація виклику мікросервісу з контролем бюджету */
int call_downstream_service(const char *name, int sock_fd, const deadline_context_t *parent_ctx,
                            int64_t configured_timeout_ms) {
    deadline_context_t sub_ctx;
    if (!create_subcall_context(parent_ctx, configured_timeout_ms, 15, &sub_ctx)) {
        printf("[-] %s: ВІДХИЛЕНО НА СТАРТІ (залишок %lld мс замалий для виклику)\n",
               name, (long long)context_remaining_ms(parent_ctx));
        return -1;
    }

    printf("[+] %s: запуск із таймаутом %lld мс (залишок батька %lld мс)\n",
           name, (long long)context_remaining_ms(&sub_ctx),
           (long long)context_remaining_ms(parent_ctx));

    /* Імітуємо відправку заголовка дедлайну та очікування відповіді */
    char hdr[64];
    serialize_deadline_header(&sub_ctx, hdr, sizeof(hdr));

    /* Імітуємо читання відповіді */
    uint8_t resp_buf[16];
    if (sock_fd >= 0) {
        if (read_exact_with_deadline(sock_fd, resp_buf, sizeof(resp_buf), &sub_ctx) != 0) {
            printf("[-] %s: ТАЙМАУТ / ПОМИЛКА під час очікування відповіді\n", name);
            return -1;
        }
    } else {
        /* Імітація локальної роботи (наприклад, 40 мс) */
        usleep(40 * 1000);
    }

    printf("[+] %s: успішно завершено, новий залишок %lld мс\n",
           name, (long long)context_remaining_ms(parent_ctx));
    return 0;
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ НАСКРІЗНОГО БЮДЖЕТУ ЧАСУ (C) ===\n\n");

    /* 1. Клієнтський запит із бюджетом 150 мс */
    const char *incoming_header = "150";
    deadline_context_t root_ctx;
    parse_deadline_header(incoming_header, 10, 500, &root_ctx);

    printf("[Вхід] Запит отримано. Дедлайн через %lld мс\n",
           (long long)context_remaining_ms(&root_ctx));

    /* 2. Імітуємо затримку в черзі пулу потоків (Admission Delay) */
    usleep(50 * 1000); /* 50 мс у черзі */
    printf("[Черга] Потік узяв запит у роботу. Залишок: %lld мс\n",
           (long long)context_remaining_ms(&root_ctx));

    /* 3. Крок 1: Аутентифікація (налаштований ліміт 100 мс) */
    if (call_downstream_service("AuthService", -1, &root_ctx, 100) != 0) {
        printf("[!] Запит провалено на етапі Auth\n");
        return 1;
    }

    /* 4. Крок 2: Платіж (налаштований ліміт 100 мс) */
    if (call_downstream_service("PaymentService", -1, &root_ctx, 100) != 0) {
        printf("[!] Запит провалено на етапі Payment\n");
        return 1;
    }

    /* 5. Крок 3: Сповіщення (налаштований ліміт 80 мс) */
    if (call_downstream_service("NotificationService", -1, &root_ctx, 80) != 0) {
        printf("[!] Notification відхилено за браком часу, переводимо в async fallback\n");
    }

    printf("\n[Результат] Операція завершена в межах дедлайну.\n");
    return 0;
}
```
```cpp
/* Імітація обробки конвеєра в C++ */
bool execute_subcall(std::string_view name,
                     const DeadlineContext& parent,
                     std::chrono::milliseconds configured_limit) {
    auto sub_ctx = derive_subcall_context(parent, configured_limit);
    if (!sub_ctx) {
        std::cout << "[-] " << name << ": ВІДХИЛЕНО НА СТАРТІ (залишок "
                  << parent.remaining().count() << " мс замалий)\n";
        return false;
    }

    std::cout << "[+] " << name << ": запуск із таймаутом "
              << sub_ctx->remaining().count() << " мс (батьківський залишок: "
              << parent.remaining().count() << " мс)\n";

    /* Імітація роботи сервісу 40 мс */
    ::usleep(40 * 1000);

    std::cout << "[+] " << name << ": завершено. Новий залишок: "
              << parent.remaining().count() << " мс\n";
    return true;
}

int main() {
    std::cout << "=== ДЕМОНСТРАЦІЯ НАСКРІЗНОГО БЮДЖЕТУ ЧАСУ (C++) ===\n\n";

    /* 1. Отримання вхідного запиту з бюджетом 150 мс */
    auto root_ctx = parse_deadline("150", std::chrono::milliseconds(10),
                                   std::chrono::milliseconds(500));
    if (!root_ctx || root_ctx->is_expired()) {
        std::cerr << "[!] Некоректний або прострочений запит на вході\n";
        return 1;
    }

    std::cout << "[Вхід] Запит отримано. Бюджет: "
              << root_ctx->remaining().count() << " мс\n";

    /* 2. Перебування в черзі воркерів 50 мс */
    ::usleep(50 * 1000);
    std::cout << "[Черга] Потік звільнився. Залишок: "
              << root_ctx->remaining().count() << " мс\n";

    /* 3. Крок 1: AuthService */
    if (!execute_subcall("AuthService", *root_ctx, std::chrono::milliseconds(100))) {
        std::cerr << "[!] Auth провалено\n";
        return 1;
    }

    /* 4. Крок 2: PaymentService */
    if (!execute_subcall("PaymentService", *root_ctx, std::chrono::milliseconds(100))) {
        std::cerr << "[!] Payment провалено\n";
        return 1;
    }

    /* 5. Крок 3: NotificationService */
    if (!execute_subcall("NotificationService", *root_ctx, std::chrono::milliseconds(80))) {
        std::cout << "[!] Notification відхилено за браком часу, переводимо в async fallback\n";
    }

    std::cout << "\n[Результат] Операція завершена успішно.\n";
    return 0;
}
```
:::

## Детерміноване тестування дедлайнів: симуляція часу без sleep()

Тестування розподілених таймаутів через реальні паузи `sleep()` є повільним і ненадійним: тести в CI/CD стають нестабільними («миготливими», flaky) через випадкові затримки планувальника операційної системи.

Професійний підхід полягає у введенні абстракції джерела часу (Time Source):
- У продакшн-коді використовується реальний монотонний годинник (`RealTimeSource`).
- У тестах використовується віртуальний годинник (`MockTimeSource`), який дозволяє штучно «промотувати» час на сотні мілісекунд уперед за 1 мікросекунду.

Це дає можливість за мілісекунди протестувати найскладніші крайові випадки:
- Запит, у якого залишається рівно 1 наносекунда до спливу дедлайну під час входу в `poll()`.
- Сплеск черги з 10 000 запитів, де 90 % відкидаються на етапі `Admission Check`.
- Симуляція повільної передачі даних байт за байтом (Slowloris) і перевірка, що таймер `poll()` надійно обриває з'єднання точно на 100-й мілісекунді.

## Інженерні пастки при реалізації контролю дедлайнів

1. **Використання настінного годинника замість монотонного.** Якщо використати `gettimeofday()` або `CLOCK_REALTIME`, підведення системного часу сервісом NTP назад може перетворити 200-мілісекундний дедлайн на нескінченне очікування або, навпаки, миттєво обірвати всі активні з'єднання.
2. **Неврахування часу перебування в черзі.** Найпоширеніша помилка — запускати відлік таймауту в момент, коли потік почав виконувати функцію обробника. Якщо запит провів у черзі вхідного пулу 400 мс при загальному ліміті 500 мс, сервер зобов'язаний виділити на виконання лише залишок у 100 мс, а не свіжі 500 мс.
3. **Пастка статичного таймауту сокета (`SO_RCVTIMEO`).** Встановлення `SO_RCVTIMEO` захищає лише від повної тиші в каналі, але беззахисне проти повільної передачі даних по 1 байту в секунду (атака типу Slowloris). Єдиний надійний спосіб — передавати таймаут, що спадає, у кожен наступний виклик `poll()` / `epoll_wait()`.
4. **Втрата дедлайну при повторних спробах (Retries).** Якщо запит завершився мережевою помилкою і клієнт вирішує зробити повтор, він зобов'язаний виділити на повторну спробу лише залишок оригінального дедлайну. Повтор зі свіжим повним бюджетом призводить до каскадного колапсу системи.
5. **Витік дескрипторів та фонових горутин/потоків.** Коли контекст дедлайну спливає, системні виклики I/O повертають помилку, але потік повинен гарантовано закрити відкритий сокет або з'єднання з пулу. У мові C для цього потрібні явні блоки очищення ресурсів, а в C++ — використання RAII-обгорток (як продемонстровано в класі `UniqueSocket`), деструктори яких автоматично закривають файловий дескриптор при розмотуванні стека (stack unwinding).
6. **Ігнорування дедлайну всередині обчислювальних циклів.** Якщо запит виконує важку математику або обробку великого JSON-документа в пам'яті, системні виклики I/O відсутні, і потік не блокується на `poll()`. Щоб сервер не зависав на обробці простроченого запиту, розробник повинен періодично викликати `context_is_expired(ctx)` або перевіряти `std::stop_token::stop_requested()` всередині ітерацій обробки.
7. **Блокування на DNS-резолвінгу.** Функція `getaddrinfo()` у стандартній бібліотеці glibc є блокуючою і не приймає таймаут. Зависання DNS-сервера може заблокувати потік на десятки секунд до початку TCP-з'єднання. Надійні продакшн-системи використовують асинхронні DNS-резолвери (наприклад, c-ares або epoll-based DNS клієнти), інтегровані з контекстом дедлайну.
