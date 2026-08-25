# ⚙️ Реалізація системного хаос-ін'єктора з контролем дедлайнів

Цей приклад демонструє створення надійного системного координатора ін'єкцій збоїв із вбудованим сторожовим таймером аварійного вимкнення (Dead Man's Switch), атомарним керуванням станом та гарантованим автоматичним відкатом правил при перевищенні порогу помилок.

## Завдання: безпечний ін'єктор збоїв у реальному часі

Розробка інструментів хаос-інженерії на системному рівні вимагає безкомпромісної надійності самого тестового рушія. Якщо процес, що вносить штучну затримку чи блокує мережеві пакети, зависне, впаде через виняток пам'яті або втратить зв'язок з оркестратором, тестований сервіс ризикує назавжди залишитися в деградованому стані.

Ін'єктор повинен відповідати чотирьом ключовим критеріям безпеки:
1. **Сторожовий таймер дедлайну (Watchdog TTL):** Експеримент має фіксований час життя. Якщо координатор не отримає явного підтвердження подовження або впаде, таймер ядра операційної системи зобов'язаний автоматично перевести ін'єктор у режим відкату (Rollback).
2. **Аварійне переривання (Automated Kill Switch):** Постійний моніторинг індикатора стійкого стану (SLI). Якщо частота помилок перевищує встановлений ліміт, ін'єкція припиняється за мікросекунди.
3. **Атомарний скінченний автомат:** Переходи між станами `IDLE`, `RUNNING`, `ABORTED` та `CLEANED` повинні бути потокобезпечними та не допускати повторних або пропущених операцій очищення.
4. **Ідемпотентний відкат:** Функція очищення (відновлення мережевих правил та зняття штучного навантаження) зобов'язана успішно виконуватися за будь-яких обставин, зокрема під час отримання сигналів `SIGINT` або `SIGTERM`.

## Архітектура рішення

Рушій будується як багатопотоковий координатор. Один робочий потік емулює проходження мережевих запитів через контрольований хаос-проксі (внесення штучної затримки `inject_delay_ms` та ймовірнісної відмови `drop_rate_pct`). Другий потік відстежує телеметрію та сторожовий таймер ядра.

```
┌─────────────────────────────────────────────────────────────┐
│                    Chaos Coordinator                        │
│                                                             │
│   ┌──────────────────────┐      ┌───────────────────────┐   │
│   │   Worker / Proxy     │      │   Watchdog & Monitor  │   │
│   │                      │      │                       │   │
│   │  Вхідний запит       │      │  Таймер дедлайну      │   │
│   │        │             │      │  Опитування метрик    │   │
│   │  [Ймовірність збою?] │      │        │              │   │
│   │   ├── Так: Delay/Err │      │  SLI < Поріг?         │   │
│   │   └── Ні:  200 OK    │      │   └── Аварійний Abort │   │
│   └──────────────────────┘      └───────────────────────┘   │
│              │                              │               │
│              └──────────────┬───────────────┘               │
│                             ▼                               │
│                [Атомарний стан: STATE]                      │
│                             │                               │
│              ┌──────────────┴───────────────┐               │
│              ▼                              ▼               │
│      Normal Completion              Emergency Rollback      │
└─────────────────────────────────────────────────────────────┘
```

Нижче наведено повнофункціональну реалізацію координатора мовами C (чистий POSIX із `timerfd` та атоміками) та C++ (сучасний стандарт C++20 із `std::jthread`, `std::stop_token` та RAII-контролем ресурсів).

## Реалізація ін'єктора збоїв

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <signal.h>
#include <time.h>

/* Стан скінченного автомата експерименту */
typedef enum {
    CHAOS_STATE_IDLE = 0,
    CHAOS_STATE_RUNNING,
    CHAOS_STATE_ABORTED,
    CHAOS_STATE_COMPLETED
} chaos_state_t;

/* Конфігурація хаос-ін'єкції */
typedef struct {
    uint32_t duration_sec;       /* Загальний час експерименту */
    uint32_t delay_ms;           /* Штучна затримка */
    uint32_t failure_rate_pct;   /* Відсоток штучних помилок (0-100) */
    double   max_allowed_err_pct;/* Критичний поріг для Kill Switch */
} chaos_config_t;

/* Структура координатора */
typedef struct {
    chaos_config_t   config;
    _Atomic int      state;
    _Atomic uint64_t total_requests;
    _Atomic uint64_t failed_requests;
    int              timer_fd;
    pthread_t        worker_thread;
    pthread_t        monitor_thread;
} chaos_coordinator_t;

/* Безпечний сон у мілісекундах */
static void sleep_ms(uint32_t ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

/* Ініціалізація сторожового таймера через timerfd */
static int init_watchdog_timer(uint32_t seconds) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd < 0) {
        perror("timerfd_create failed");
        return -1;
    }
    struct itimerspec its;
    memset(&its, 0, sizeof(its));
    its.it_value.tv_sec = seconds;
    its.it_value.tv_nsec = 0;
    if (timerfd_settime(tfd, 0, &its, NULL) < 0) {
        perror("timerfd_settime failed");
        close(tfd);
        return -1;
    }
    return tfd;
}

/* Ідемпотентна функція відкату правил та згортання */
static void chaos_rollback(chaos_coordinator_t *coord, const char *reason) {
    int expected = CHAOS_STATE_RUNNING;
    if (atomic_compare_exchange_strong(&coord->state, &expected, CHAOS_STATE_ABORTED)) {
        printf("\n[ROLLBACK] Аварійна зупинка хаос-ін'єкції! Причина: %s\n", reason);
        printf("[ROLLBACK] Відновлення мережевих правил та зняття обмежень...\n");
        /* Симуляція відновлення правил Linux TC або скидання envoy filter */
        printf("[ROLLBACK] Стан системи повернуто до базової лінії (Clean).\n");
    }
}

/* Потік моніторингу SLI та сторожового таймера */
static void *monitor_thread_fn(void *arg) {
    chaos_coordinator_t *coord = (chaos_coordinator_t *)arg;
    uint64_t exp_buf;

    while (atomic_load(&coord->state) == CHAOS_STATE_RUNNING) {
        /* Перевірка спрацювання дедлайну timerfd */
        ssize_t s = read(coord->timer_fd, &exp_buf, sizeof(exp_buf));
        if (s == sizeof(exp_buf)) {
            chaos_rollback(coord, "Вичерпано ліміт часу експерименту (Watchdog TTL)");
            break;
        }

        /* Перевірка індикатора стійкого стану (SLI) */
        uint64_t total = atomic_load(&coord->total_requests);
        uint64_t failed = atomic_load(&coord->failed_requests);
        if (total > 20) {
            double current_err_pct = ((double)failed / (double)total) * 100.0;
            if (current_err_pct > coord->config.max_allowed_err_pct) {
                char reason[128];
                snprintf(reason, sizeof(reason), "Порушення SLO! Помилки: %.2f%% (ліміт: %.2f%%)",
                         current_err_pct, coord->config.max_allowed_err_pct);
                chaos_rollback(coord, reason);
                break;
            }
        }
        sleep_ms(100);
    }
    return NULL;
}

/* Робочий потік: симуляція проходження клієнтських транзакцій */
static void *worker_thread_fn(void *arg) {
    chaos_coordinator_t *coord = (chaos_coordinator_t *)arg;

    while (atomic_load(&coord->state) == CHAOS_STATE_RUNNING) {
        atomic_fetch_add(&coord->total_requests, 1);
        int roll = rand() % 100;

        if (roll < (int)coord->config.failure_rate_pct) {
            /* Ін'єкція збою: затримка та повернення коду помилки */
            sleep_ms(coord->config.delay_ms);
            atomic_fetch_add(&coord->failed_requests, 1);
            printf("[WORKER] Ін'єкція: затримка %ums -> Помилка 503 (відмова)\n", coord->config.delay_ms);
        } else {
            /* Нормальна обробка запиту */
            sleep_ms(15);
            printf("[WORKER] Запит оброблено штатно (200 OK)\n");
        }
        sleep_ms(50);
    }
    return NULL;
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== Запуск системного координатора хаос-експериментів (C POSIX) ===\n");

    chaos_coordinator_t coord;
    memset(&coord, 0, sizeof(coord));
    coord.config.duration_sec = 4;
    coord.config.delay_ms = 120;
    coord.config.failure_rate_pct = 35;
    coord.config.max_allowed_err_pct = 30.0; /* Поріг аварійного відкату */

    atomic_store(&coord.state, CHAOS_STATE_RUNNING);
    coord.timer_fd = init_watchdog_timer(coord.config.duration_sec);
    if (coord.timer_fd < 0) {
        return EXIT_FAILURE;
    }

    pthread_create(&coord.monitor_thread, NULL, monitor_thread_fn, &coord);
    pthread_create(&coord.worker_thread, NULL, worker_thread_fn, &coord);

    /* Очікування завершення роботи потоків */
    pthread_join(coord.monitor_thread, NULL);
    pthread_join(coord.worker_thread, NULL);

    int final_state = atomic_load(&coord->state);
    if (final_state == CHAOS_STATE_RUNNING) {
        int expected = CHAOS_STATE_RUNNING;
        atomic_compare_exchange_strong(&coord->state, &expected, CHAOS_STATE_COMPLETED);
        printf("\n[SUCCESS] Хаос-експеримент завершено штатно без порушення SLO.\n");
    }

    uint64_t total = atomic_load(&coord->total_requests);
    uint64_t failed = atomic_load(&coord->failed_requests);
    printf("Підсумок: %lu запитів, %lu помилок (%.2f%%)\n",
           total, failed, total ? ((double)failed / (double)total) * 100.0 : 0.0);

    close(coord.timer_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <random>
#include <string>
#include <string_view>
#include <format>
#include <memory>
#include <system_error>
#include <cstdint>
#include <sys/timerfd.h>
#include <unistd.h>

enum class ChaosState : uint8_t {
    Idle = 0,
    Running,
    Aborted,
    Completed
};

struct ChaosConfig {
    std::chrono::seconds duration{4};
    std::chrono::milliseconds delay{120};
    uint32_t failure_rate_pct{35};
    double max_allowed_err_pct{30.0};
};

/* RAII-обгортка над системним дескриптором timerfd */
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

class ChaosCoordinator {
public:
    explicit ChaosCoordinator(ChaosConfig config)
        : config_(config), state_(ChaosState::Idle) {}

    void run() {
        state_.store(ChaosState::Running, std::memory_order_release);
        std::cout << "=== Запуск системного координатора хаос-експериментів (Modern C++) ===\n";

        UniqueFd timer_fd = create_watchdog_timer(config_.duration);

        // Запуск потоків моніторингу та воркера з використанням std::jthread
        std::jthread monitor_thread([this, fd = timer_fd.get()](std::stop_token stoken) {
            monitor_loop(stoken, fd);
        });

        std::jthread worker_thread([this](std::stop_token stoken) {
            worker_loop(stoken);
        });

        // Головний потік чекає завершення (коли state перейде з Running)
        while (state_.load(std::memory_order_acquire) == ChaosState::Running) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        // Надсилаємо запит на зупинку jthread
        monitor_thread.request_stop();
        worker_thread.request_stop();
        // RAII jthread автоматично викличе join() при виході зі скоупу

        print_summary();
    }

private:
    static UniqueFd create_watchdog_timer(std::chrono::seconds duration) {
        int fd = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "timerfd_create failed");
        }
        struct itimerspec its{};
        its.it_value.tv_sec = duration.count();
        if (::timerfd_settime(fd, 0, &its, nullptr) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "timerfd_settime failed");
        }
        return UniqueFd(fd);
    }

    void rollback(std::string_view reason) {
        ChaosState expected = ChaosState::Running;
        if (state_.compare_exchange_strong(expected, ChaosState::Aborted, std::memory_order_acq_rel)) {
            std::cout << std::format("\n[ROLLBACK] Аварійна зупинка хаос-ін'єкції! Причина: {}\n", reason);
            std::cout << "[ROLLBACK] Відновлення мережевих маршрутів та правил ядра...\n";
            std::cout << "[ROLLBACK] Базовий стан відновлено (Clean State).\n";
        }
    }

    void monitor_loop(std::stop_token stoken, int timer_fd) {
        uint64_t exp_buf = 0;
        while (!stoken.stop_requested() && state_.load(std::memory_order_acquire) == ChaosState::Running) {
            // Перевірка спрацювання сторожового таймера ядра
            ssize_t s = ::read(timer_fd, &exp_buf, sizeof(exp_buf));
            if (s == sizeof(exp_buf)) {
                rollback("Вичерпано ліміт часу експерименту (Watchdog TTL)");
                break;
            }

            // Перевірка порушення SLI
            uint64_t total = total_requests_.load(std::memory_order_relaxed);
            uint64_t failed = failed_requests_.load(std::memory_order_relaxed);
            if (total > 20) {
                double current_err_pct = (static_cast<double>(failed) / static_cast<double>(total)) * 100.0;
                if (current_err_pct > config_.max_allowed_err_pct) {
                    rollback(std::format("Порушення SLO! Помилки: {:.2f}% (ліміт: {:.2f}%)",
                                         current_err_pct, config_.max_allowed_err_pct));
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    void worker_loop(std::stop_token stoken) {
        std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint32_t> dist(0, 99);

        while (!stoken.stop_requested() && state_.load(std::memory_order_acquire) == ChaosState::Running) {
            total_requests_.fetch_add(1, std::memory_order_relaxed);
            uint32_t roll = dist(rng);

            if (roll < config_.failure_rate_pct) {
                std::this_thread::sleep_for(config_.delay);
                failed_requests_.fetch_add(1, std::memory_order_relaxed);
                std::cout << std::format("[WORKER] Ін'єкція: затримка {}ms -> Відмова 503\n", config_.delay.count());
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(15));
                std::cout << "[WORKER] Запит оброблено успішно (200 OK)\n";
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }

    void print_summary() const {
        ChaosState final_st = state_.load(std::memory_order_acquire);
        if (final_st == ChaosState::Running) {
            std::cout << "\n[SUCCESS] Хаос-експеримент завершено успішно без порушень SLO.\n";
        }
        uint64_t total = total_requests_.load(std::memory_order_relaxed);
        uint64_t failed = failed_requests_.load(std::memory_order_relaxed);
        double err_pct = total ? (static_cast<double>(failed) / static_cast<double>(total)) * 100.0 : 0.0;
        std::cout << std::format("Підсумок: {} запитів, {} помилок ({:.2f}%)\n", total, failed, err_pct);
    }

    ChaosConfig config_;
    std::atomic<ChaosState> state_{ChaosState::Idle};
    std::atomic<uint64_t> total_requests_{0};
    std::atomic<uint64_t> failed_requests_{0};
};

int main() {
    try {
        ChaosConfig config{
            .duration = std::chrono::seconds(4),
            .delay = std::chrono::milliseconds(120),
            .failure_rate_pct = 35,
            .max_allowed_err_pct = 30.0
        };

        ChaosCoordinator coordinator(config);
        coordinator.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка координатора: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Поглиблений розбір системних механізмів

Розглянемо детально, як функціонують окремі системні компоненти координатора, на яких базується безпека хаос-експериментів у висококритичних середовищах.

### 1. Сторожовий таймер ядра (Linux timerfd) проти прикладного таймера

Головна небезпека наївних хаос-скриптів полягає у використанні прикладних таймерів (наприклад, `sleep(duration)` у скрипті Python або Node.js). Якщо інтерпретатор зависне під час Garbage Collection, потік буде заблокований взаємним блокуванням (deadlock) або вичерпає чергу подій, таймер сну не спрацює, і тестована система залишиться у стані збою на невизначений термін.

Системний виклик `timerfd_create` реєструє таймер безпосередньо у планувальнику ядра Linux:
- `CLOCK_MONOTONIC`: Годинник, що монотонно зростає і не піддається стрибкам системного часу через протокол NTP або ручне коригування адміністратором. Це виключає ризик передчасного чи запізнілого спрацьовування таймера.
- `TFD_NONBLOCK`: Дескриптор відкривається в неблокуючому режимі. Системний виклик `read(timer_fd, ...)` повертає кількість спрацьовувань таймера або помилку `EAGAIN`, якщо час ще не минув, дозволяючи потоку моніторингу виконувати інші перевірки в єдиному циклі опитування.
- `TFD_CLOEXEC`: Прапорець закриття при виконанні (`close-on-exec`). Якщо координатор породжує дочірній процес (`fork`/`exec`), дескриптор таймера автоматично закривається в новому процесі, усуваючи витоки ресурсів у системні демони.

Коли таймер закінчується, ядро операційної системи генерує подію готовності дескриптора до читання. Навіть якщо процес ін'єктора зазнає колосального навантаження, ядро гарантує доставку сигналу пробудження.

### 2. Атомарний скінченний автомат і впорядкування пам'яті (Memory Ordering)

Координатор реалізує потокобезпечний скінченний автомат із чотирма станами: `IDLE` (підготовка), `RUNNING` (активна ін'єкція), `ABORTED` (аварійний відкат) та `COMPLETED` (штатне завершення).

Особливу увагу приділено операціям зі змінною стану `state_`:
- **Атомарний CAS (`compare_exchange_strong`):** Використовується у функції `rollback()`. Якщо потік моніторингу зафіксував перевищення помилок SLI рівно в ту ж мілісекунду, коли спрацював дедлайн `timerfd`, обидва потоки одночасно спробують викликати процедуру відкату. Завдяки операції CAS лише перший потік змінить значення стану з `RUNNING` на `ABORTED` і поверне `true`. Другий потік отримає `false` і негайно вийде. Це гарантує ідемпотентність і запобігає подвійному скиданню мережевих правил.
- **Семантика пам'яті (Acquire-Release):**
  - Запис початкового стану `state_.store(Running, std::memory_order_release)` гарантує, що вся ініціалізація структур конфігурації та таймерів буде повністю зафіксована в пам'яті до того, як робочі потоки побачать стан `Running`.
  - Читання стану у циклах `state_.load(std::memory_order_acquire)` гарантує, що потоки негайно побачать зміни спільних змінних, зроблені потоком відкату, запобігаючи використанню застарілих кеш-ліній процесора.

### 3. Розрахунок ковзного вікна SLI та динамічне аварійне гальмування

Функція моніторингу оцінює поточний рівень якості обслуговування (SLI) у реальному часі.

У промислових системах оцінка здійснюється за алгоритмом ковзного вікна (Sliding Window):
```
                       Вікно спостереження W = 5 сек
               ┌───────────────────────────────────────────┐
Запити:        ... [OK] [ERR] [OK] [OK] [ERR] [ERR] [OK] [OK] [ERR] ...
                                    │
                                    ▼
                Поточний відсоток помилок: 3 / 8 = 37.5%
                Критичний поріг (Threshold):       30.0%
                                    │
                                    ▼
                        [ТРИГЕР: Аварійний Abort]
```

Для запобігання хибнопозитивним спрацьовуванням (False Positives) на старті експерименту використовується бар'єр прогріву (`total > 20`). Без цього бар'єра перша ж випадкова помилка на першому тестовому запиті дала б миттєвий рівень помилок `100%`, що призвело б до передчасного зриву експерименту.

### 4. Рівень ядра Linux: інтеграція з Linux Traffic Control (netem) та cgroups v2

У реальних виробничих інструментах (Chaos Mesh, Pumba, Litmus) функція `chaos_rollback` взаємодіє з підсистемами ядра Linux. Розглянемо низькорівневі механізми, які виконуються замість тестового виводу `printf`:

1. **Мережева ін'єкція через Netlink (Linux TC `netem`):**
   Ін'єктор відкриває сокет Netlink (`AF_NETLINK`, протокол `NETLINK_ROUTE`) і формує бінарний пакет із повідомленням `RTM_NEWQDISC`. Структура повідомлення містить заголовок `struct nlmsghdr`, структуру `struct tcmsg` та вкладені атрибути `struct rtattr`:
   - Заголовок повідомлення вказує тип операції (`RTM_NEWQDISC`), прапорці створення (`NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL`) та порядковий номер транзакції `nlmsg_seq`.
   - Структура `tcmsg` задає мережевий інтерфейс (через `ifindex`, наприклад, інтерфейс віртуального комутатора `veth`), батьківський хендл (`TC_H_ROOT`) та власний ідентифікатор черги.
   - Вкладений атрибут `TCA_KIND` містить рядок `"netem"`, а атрибут `TCA_OPTIONS` передає структуру конфігурації `struct tc_netem_qopt`, де поля `latency`, `jitter`, `loss` та `corrupt` задають параметри деградації трафіку.
   Під час виклику `rollback()` координатор надсилає ядру команду `RTM_DELQDISC`, що призводить до миттєвого атомарного демонтажу дисципліни черги в ядрі та відновлення стандартного обробника черги (наприклад, `fq_codel` або `noqueue`).

2. **Математичні моделі розподілу мережевого джитера:**
   Підсистема ядра `netem` підтримує різні статистичні розподіли для параметра джитера (варіації затримки). Якщо затримка задана як `100ms ± 20ms`:
   - **Рівномірний розподіл (Uniform Distribution):** Затримка кожного пакета обирається як випадкова величина з відрізка `[80ms, 120ms]`. Ця модель є базовою, проте слабо відповідає фізичним реаліям інтернету.
   - **Нормальний розподіл Гауса (Normal Distribution):** Затримка генерується за формулою Гауса `N(μ = 100ms, σ = 10ms)`, що значно точніше моделює випадкові затримки комутаторів під помірним навантаженням.
   - **Розподіл Парето (Pareto / Pareto-Normal):** Моделює явище «довгого хвоста» (heavy-tailed latency), коли переважна більшість пакетів проходить швидко, але окремі пакети зазнають колосальних затримок через черги буферів маршрутизаторів (Bufferbloat).

3. **Обмеження обчислювальних ресурсів через cgroups v2:**
   Для симуляції процесорного голодування або вичерпання пам'яті координатор взаємодіє з віртуальною файловою системою контрольних груп Linux:
   - Обмеження CPU: запис квоти та періоду у файл `/sys/fs/cgroup/.../cpu.max`. Наприклад, рядок `50000 100000` обмежує споживання процесора 50 мілісекундами на кожні 100 мілісекунд астрономічного часу (еквівалент 0.5 ядра CPU). Якщо процес намагається спожити більше, планувальник CFS (Completely Fair Scheduler) примусово блокує його виконання (CPU throttling).
   - Обмеження пам'яті: запис ліміту в байтах у `/sys/fs/cgroup/.../memory.high`. При досягненні цього порогу ядро починає агресивне витіснення сторінок пам'яті в swap або сповільнює виділення пам'яті через асинхронний reclaim, імітуючи тяжку деградацію вузла без миттєвого вбивства процесу.
   - Під час процедури відкату координатор записує значення `max` у відповідні файли, повертаючи процесу повну обчислювальну потужність.

## Проксі-інтерцептори рівня сокетів та eBPF

Окрім маніпуляцій на рівні ядра через TC та cgroups, сучасні платформи хаосу застосовують пряму модифікацію потоків даних через сокетні проксі та ін'єкцію системних помилок через eBPF.

### 1. Перехоплення системних викликів через `LD_PRELOAD`

Бібліотека динамічно підміняє точки входу POSIX API:
- Коли застосунок викликає `recv(fd, buf, len, 0)`, перехоплювач звертається до атомарної структури стану хаосу.
- Якщо генератор псевдовипадкових чисел активує затримку, потік засинає через `nanosleep()` до виклику справжнього символу `dlsym(RTLD_NEXT, "recv")`.
- Якщо активна симуляція обриву зв'язку, функція миттєво повертає `-1` і записує `errno = ECONNRESET` або `errno = ETIMEDOUT`.

### 2. Ін'єкція помилок через eBPF (bpf_override_return)

У сучасних ядрах Linux (версії 4.16+) доступний найбільш хірургічний метод ін'єкції — використання eBPF-програм типу `BPF_PROG_TYPE_KPROBE` з хелпером `bpf_override_return()`:

:::tabs
```c
/* Простір ядра: eBPF kprobe-перехоплювач (kprobe_connect.bpf.c) */
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

extern u32 target_chaos_pid;

SEC("kprobe/__x64_sys_connect")
int BPF_KPROBE(trace_connect, struct pt_regs *regs) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (pid == target_chaos_pid) {
        /* Примусово підміняємо результат виконання ядра на помилку тайм-ауту */
        bpf_override_return(regs, -ETIMEDOUT);
        return 0;
    }
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```
```cpp
// Простір користувача: C++20 RAII-завантажувач eBPF (ChaosBpfLoader.hpp)
#include <memory>
#include <stdexcept>
#include <string_view>
#include <format>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class ChaosBpfManager {
public:
    explicit ChaosBpfManager(uint32_t target_pid) : target_pid_(target_pid) {
        skel_ = bpf_object__open_file("kprobe_connect.bpf.o", nullptr);
        if (!skel_) {
            throw std::runtime_error("Не вдалося відкрити eBPF об'єкт");
        }

        if (bpf_object__load(skel_) < 0) {
            bpf_object__close(skel_);
            throw std::runtime_error("Помилка завантаження eBPF програми в ядро");
        }

        // Прив'язка kprobe до системного виклику connect
        prog_ = bpf_object__find_program_by_name(skel_, "trace_connect");
        link_ = bpf_program__attach(prog_);
        if (!link_) {
            bpf_object__close(skel_);
            throw std::runtime_error("Не вдалося підключити eBPF kprobe hook");
        }
    }

    ~ChaosBpfManager() noexcept {
        if (link_) bpf_link__destroy(link_);
        if (skel_) bpf_object__close(skel_);
    }

    ChaosBpfManager(const ChaosBpfManager&) = delete;
    ChaosBpfManager& operator=(const ChaosBpfManager&) = delete;
    ChaosBpfManager(ChaosBpfManager&& other) noexcept 
        : skel_(other.skel_), prog_(other.prog_), link_(other.link_), target_pid_(other.target_pid_) {
        other.skel_ = nullptr;
        other.link_ = nullptr;
    }

private:
    struct bpf_object* skel_{nullptr};
    struct bpf_program* prog_{nullptr};
    struct bpf_link* link_{nullptr};
    uint32_t target_pid_{0};
};
```
:::

Коли цільовий процес намагається відкрити TCP-з'єднання через `connect()`, інструкція перехоплюється eBPF-віртуальною машиною. Ядро повністю пропускає реальний мережевий стек і негайно повертає застосунку помилку `ETIMEDOUT`. Це дозволяє симулювати повну ізоляцію окремого потоку чи процесу без зміни конфігурації мережевих інтерфейсів хоста.

### 3. Пастка напіввідкритих сокетів та прапорець `MSG_NOSIGNAL`

Якщо ін'єктор затримує передачу байтів, клієнтський стек може вичерпати власний таймаут сокета (`SO_RCVTIMEO`) і надіслати пакет `FIN` або `RST`. Якщо після цього проксі-потік спробує виконати стандартний виклик `write(socket_fd, ...)` або `send(...)` без прапорця `MSG_NOSIGNAL`, ядро згенерує сигнал `SIGPIPE`. За замовчуванням обробник `SIGPIPE` миттєво вбиває процес ін'єктора. Тому в коді проксі-ін'єкторів використовують `send(fd, buf, len, MSG_NOSIGNAL)` або на старті процесу встановлюють `signal(SIGPIPE, SIG_IGN)`.

### 4. Ін'єкція збоїв у DNS-резолвінг

Окремим критичним вектором відмов у хмарних середовищах є деградація DNS. Коли Kubernetes CoreDNS або локальний резолвер `systemd-resolved` зазнають перевантаження, клієнтський резолвер `glibc` починає повторювати UDP-запити до портів 53:
- Параметр `ndots:5` у файлі `/etc/resolv.conf` змушує бібліотеку послідовно опитувати всі суфікси пошуку (`namespace.svc.cluster.local`, `svc.cluster.local`, `cluster.local`) для кожного некваліфікованого доменного імені.
- Внесення 5% втрати пакетів на UDP-порт 53 призводить до 5-секундних таймаутів у клієнтських пулах HTTP-з'єднань, оскільки кожен пропущений пакет DNS-відповіді змушує `glibc` чекати вичерпання внутрішнього таймера перед повторною спробою. Ін'єктор DNS-хаосу дозволяє виявити відсутність локального кешування імен (nscd / NodeLocal DNSCache) у сервісі до того, як відмова CoreDNS викличе повний параліч кластера.

### 5. Інтерцептори протоколу gRPC та метадані контексту

Для мікросервісів, що спілкуються через gRPC / HTTP/2, хаос-ін'єкція реалізується на рівні сервісних інтерцепторів (gRPC Client / Server Interceptors):
- Інтерцептор вичитує метадані виклику (gRPC Metadata), шукаючи контекстний заголовок `x-chaos-fault: status=UNAVAILABLE,delay=200ms`.
- Якщо заголовок знайдено, інтерцептор призупиняє передачу RPC-повідомлення через неблокуючий таймер подій на 200 мс і повертає статус `grpc::Status(grpc::StatusCode::UNAVAILABLE, "Fault injected by chaos middleware")`.
- Це дозволяє перевірити, чи коректно клієнтський стек gRPC виконує повторний вибір інстансу (gRPC Subchannel Rebalancing) та чи передає він дедлайн виклику (`grpc-timeout`) у дочірні виклики через дерево розподіленого трейсингу.

## Виробничі пастки та крайові випадки

Під час проектування системних хаос-рушіїв необхідно захищатися від типових прихованих небезпек:

1. **Пастка «осиротілих» правил ядра (Orphan Kernel Rules):**
   Якщо процес ін'єктора буде раптово вбитий операційною системою через нестачу пам'яті (`OOM Killer`) або отримає сигнал `SIGKILL` (`kill -9`), жоден користувацький код очищення не виконається. Правило затримки `netem` або обмеження cgroup залишиться активним у ядрі назавжди.
   *Вирішення:* Використання зовнішнього демона-наглядача (Watchdog Daemon) або реєстрація правил з обмеженим часом життя (eBPF map timer із TTL). Якщо агент хаосу не оновлює серцебиття (heartbeat) протягом встановленого інтервалу, незалежний наглядач видаляє правила ядра.
2. **Мережеві шторми повторних спроб (Retry Storms):**
   Штучне внесення затримки 120 мс може спровокувати спрацьовування таймаутів у клієнтських мікросервісах. Якщо клієнти налаштовані на агресивні повтори без експоненційного відступу (Exponential Backoff з Jitter), загальне навантаження на систему зросте в 5–10 разів. Якщо ін'єктор не відстежує загальний вхідний RPS, лавиноподібне зростання трафіку здатне повністю завалити базу даних або пул потоків.
3. **Витік файлових дескрипторів сокетів:**
   Під час проксіювання TCP-трафіку з ін'єкцією затримок сервер утримує відкриті сокети довше звичайного. За високої інтенсивності запитів процес може швидко вичерпати системний ліміт дескрипторів `RLIMIT_NOFILE`, що призведе до помилок `EMFILE: Too many open files` на всіх нових підключеннях.
4. **Каскадне блокування пулу потоків моніторингу:**
   Якщо потік, що виконує перевірку SLI, звертається до зовнішнього Prometheus або сервісу метрик через блокуючий HTTP-клієнт, падіння цього зовнішнього сервісу заблокує аварійний вимикач (Kill Switch). Щоб уникнути цього, потік моніторингу зобов'язаний спиратися виключно на локальні in-memory лічильники, або використовувати жорсткий локальний таймаут сокета не більше 50 мс.
5. **Теплова смерть пам'яті (Memory Leaks under Chaos):**
   Якщо застосунок накопичує чергу повідомлень під час уповільнення вихідного каналу, але не має налаштованого зворотного тиску (Backpressure), розмір черги в RAM зростає лінійно з часом. Ін'єкція затримки тривалістю понад 60 секунд здатна виснажити всю доступну оперативну пам'ять контейнера, спровокувавши аварійну загибель сервісу від OOM Killer замість перевірки штатної деградації.

## Інтеграція в CI/CD та автоматизовані ворота стійкості (Chaos Gates)

У сучасних інженерних конвеєрах розгортання хаос-ін'єктор запускається як автоматизований етап верифікації (Chaos Gate) перед виходом релізу в широкий продакшен:

1. **Канаркове розгортання нової версії:** Оркестратор деплоїть 5% Pod з новим бінарним файлом.
2. **Активація хаос-тесту:** Ін'єктор застосовує навантаження (50% втрати пакетів до вторинного кешу Redis).
3. **Оцінка автоматичного вироку:** Пайплайн протягом 3 хвилин оцінює індикатори SLI канаркової групи порівняно з контрольною групою. Якщо частота помилок канарки зростає більше ніж на 0.05%, реліз негайно скасовується (Auto-Rollback), а розробники отримують детальний звіт про неспрацювання локального fallback-кешу.

## Простеження та діагностика в Linux

Перевірити коректність роботи ін'єктора та його взаємодію з ядром операційної системи можна за допомогою системних утиліт Linux.

### 1. Трейсинг системних викликів через `strace`

Команда для діагностики створення та опитування дескрипторів таймера:
```bash
strace -f -e trace=timerfd_create,timerfd_settime,read,nanosleep ./chaos_injector
```

У виводі утиліти фіксується створення таймера та його неблокуюче опитування:
```text
timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK|TFD_CLOEXEC) = 3
timerfd_settime(3, 0, {it_interval={tv_sec=0, tv_nsec=0}, it_value={tv_sec=4, tv_nsec=0}}, NULL) = 0
nanosleep({tv_sec=0, tv_nsec=100000000}, NULL) = 0
read(3, 0x7fff..., 8) = -1 EAGAIN (Resource temporarily unavailable)
...
read(3, "\1\0\0\0\0\0\0\0", 8) = 8
[ROLLBACK] Аварійна зупинка хаос-ін'єкції! Причина: Вичерпано ліміт часу експерименту (Watchdog TTL)
```

### 2. Моніторинг правил Traffic Control

Перевірити активні правила дисципліни черги під час роботи експерименту:
```bash
tc -s qdisc show dev eth0
```
Після завершення роботи координатора вивід цієї команди повинен підтверджувати повну відсутність правил `netem`, що свідчить про чистоту та надійність виконаного відкату.
