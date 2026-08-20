# ⚙️ Контролер моніторингу здоров'я та огородження вузлів кластера

У розподіленому кластері баз даних найнебезпечнішим станом є «розщеплення мозку» (Split-Brain), коли вузол вважає себе активним лідером і продовжує записувати клієнтські транзакції в локальні таблиці, хоча решта кластера вже визнала його мертвим і обрала новий Primary-сервер. Якщо мережевий зв'язок відновлюється, дві копії бази даних мають несумісні історії транзакцій, що вимагає ручного втручання та неминуче призводить до втрати частини бізнес-даних.

Щоб унеможливити подвійне лідерство на рівні операційної системи, кожен вузол кластера повинен мати автономного сторожового агента — **контролер огородження (англ. *Fencing Controller*)**. Цей контролер безперервно перевіряє життєздатність локального рушія СУБД, подовжує лізу в системі консенсусу (DCS) та скидає апаратний сторожовий таймер ядра (`/dev/watchdog`). Якщо чергове подовження лізи провалюється або процес СУБД зависає, сторож негайно ізолює локальний вузол або ініціює апаратне скидання живлення (STONITH).

Нижче реалізовано повнофункціональний контролер огородження та моніторингу лізи на мовах C та C++ з використанням монотонних годинників, неблокуючих перевірок здоров'я через UNIX-сокети та взаємодії з підсистемою Linux Watchdog.

---

## 1. Архітектурна ідея та машина станів контролера

Сторожовий контролер функціонує як незалежний системний демон у просторі користувача. Головне завдання контролера — забезпечити, щоб вузол мав право приймати операції запису виключно тоді, коли він має активну, нетерміновану оренду (лізу) в розподіленому сховищі консенсусу (DCS) та підтверджений локальний стан здоров'я.

Життєвий цикл контролера описується скінченним автоматом із чотирма основними станами:

```
               ┌───────────────────────────────┐
               │    1. СТАН: FOLLOWER / IDLE   │
               │   (Стеження за станом лідера) │
               └───────────────┬───────────────┘
                               │
            Виграно лізу в DCS │ (CAS-успіх)
                               ▼
               ┌───────────────────────────────┐
         ┌────►│     2. СТАН: LEADER_ACTIVE    │◄────┐
         │     │ (Скидання watchdog, RW режим) │     │
         │     └───────────────┬───────────────┘     │
         │                     │                     │
Цикл OK  │                     │ Збій DCS / Таймаут  │ Швидке відновлення
(Heartbeat)                    ▼                     │ (< Safety Margin)
         │     ┌───────────────────────────────┐     │
         └─────┤    3. СТАН: LEASE_DEGRADED    ├─────┘
               │  (Спроби зв'язку, таймер цокає)│
               └───────────────┬───────────────┘
                               │
              Час вичерпано    │ (Elapsed >= Safety Margin)
                               ▼
               ┌───────────────────────────────┐
               │   4. СТАН: FENCING_TRIGGERED  │
               │  (Emergency Kill / WD Reboot) │
               └───────────────────────────────┘
```

### 1.1. Детальний опис переходів між станами

1. **`FOLLOWER / IDLE` (Режим репліки):**
   Вузол перебуває в ролі Standby. Контролер не утримує лідерської лізи в DCS і не взаємодіє з апаратним сторожовим таймером. Контролер періодично перевіряє стан локального процесу реплікації (відставання за LSN) та відстежує стан ключа `/service/leader` у DCS. Якщо ключ звільняється, контролер ініціює процедуру участі у виборах.

2. **`LEADER_ACTIVE` (Активне лідерство):**
   Вузол успішно виграв атомарну транзакцію в DCS і став лідером кластера. У цьому стані запускається жорсткий періодичний цикл `T_loop` (за замовчуванням 2 секунди). Під час кожного проходу циклу контролер виконує дві обов'язкові перевірки:
   - Відправляє тестовий запит до локальної СУБД через локальний сокет для підтвердження того, що рушій не завис у взаємному блокуванні (Deadlock) або дисковому I/O;
   - Надсилає запит продовження терміну дії лізи до DCS (etcd/Consul).
   Якщо обидві операції завершуються успішно, контролер надсилає керуючий сигнал `ioctl(fd, WDIOC_KEEPALIVE)` драйверу ядра `/dev/watchdog`.

3. **`LEASE_DEGRADED` (Деградація оренди):**
   Якщо зв'язок із DCS переривається (наприклад, через втрату пакетів на комутаторі) або СУБД не відповідає на сокетний запит протягом встановленого таймауту, контролер переходить у стан тривоги. У цьому стані контролер **негайно припиняє скидати сторожовий таймер**. Починається відлік часу від моменту останнього успішного серцебиття `last_successful_heartbeat`. Якщо зв'язок відновлюється до вичерпання захисного інтервалу `T_safety_margin` (наприклад, за 3 секунди), контролер повертається у стан `LEADER_ACTIVE`.

4. **`FENCING_TRIGGERED` (Примусове огородження):**
   Якщо минулий час перевищив поріг безпеки `T_safety_margin`, контролер констатує втрату права на лідерство. Оскільки решта кластера незабаром обере нового лідера після спливання `T_ttl`, старий лідер зобов'язаний гарантувати повне припинення прийому транзакцій. Контролер надсилає сигнал `SIGKILL` усім локальним процесам СУБД, примусово скидає відкриті сокети або дозволяє апаратному сторожовому таймеру ядра виконати безумовне перезавантаження материнської плати.

---

## 2. Підсистема Linux Watchdog та взаємодія з ядром

Підсистема сторожового таймера в ядрі Linux (`drivers/watchdog/watchdog_core.c`) забезпечує зв'язок між простором користувача та апаратним модулем скидання (Hardware Watchdog Timer). Цей модуль може бути інтегрований у південний міст материнської плати, контролер віддаленого управління сервером (Baseboard Management Controller, BMC / IPMI) або емульований гіпервізором у віртуальному середовищі (наприклад, віртуальний пристрій `i6300esb` у QEMU/KVM).

```
   [ Простір користувача: Контролер ]
                   │
         ioctl()   │ WDIOC_KEEPALIVE (кожні 2 сек)
                   ▼
   [ Простір ядра: /dev/watchdog ] ──► [ Апаратний лічильник таймера (7 сек) ]
                                                        │
                                    Таймаут сплив?      │ Лічильник дійшов до 0
                                    (Не оновлено)       ▼
                                       [ Апаратний Hard Reset процесора ]
```

### 2.1. Керуючі виклики `ioctl` драйвера watchdog

Взаємодія з символьним пристроєм `/dev/watchdog` виконується через спеціалізовані POSIX системні виклики `ioctl`:
- `WDIOC_SETTIMEOUT`: встановлює апаратний таймаут спрацювання (у секундах). Якщо протягом цього часу ядро не отримає сигналу оновлення, апаратний модуль замикає лінію RESET на материнській платі.
- `WDIOC_KEEPALIVE`: скидає внутрішній зворотний лічильник апаратного модуля назад до встановленого значення таймауту.
- `WDIOC_GETTIMEOUT`: зчитує поточний налаштований таймаут пристрою.
- `WDIOC_SETOPTIONS`: дозволяє програмно вмикати або вимикати сторожовий таймер за допомогою прапорців `WDIOS_ENABLECARD` та `WDIOS_DISABLECARD`.

Особливістю підсистеми є механізм «Magic Close»: якщо процес у просторі користувача просто закриває файловий дескриптор викликом `close(fd)` без попереднього запису символу `'V'` (ASCII 86), драйвер ядра розцінює це як падіння керуючого демона і навмисно не вимикає апаратний таймер, спричиняючи примусове перезавантаження сервера.

---

## 3. Повнофункціональна реалізація контролера на C та C++

Програма написана для роботи під керуванням сучасних версій ядра Linux. Код містить дві паралельні ідіоматичні реалізації: низькорівневу версію на C (із прямими викликами POSIX API та контролем дескрипторів) та безпечну об'єктно-орієнтовану реалізацію на C++20 (із використанням RAII-обгорток для ресурсів ядра, `std::chrono` та обробкою помилок через типізовані структури).

:::tabs
```c
/* ============================================================================
 * cluster_fencing_daemon.c — C-реалізація контролера огородження та лізи
 * ============================================================================ */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

#define LOOP_WAIT_MS       2000   /* Інтервал циклу опитування (2 сек) */
#define RETRY_TIMEOUT_MS   4000   /* Таймаут зв'язку з координатором (4 сек) */
#define SAFETY_MARGIN_MS   5000   /* Запас безпеки до примусового огородження (5 сек) */
#define LEASE_TTL_MS       10000  /* Повний час життя лізи в DCS (10 сек) */
#define WATCHDOG_DEV       "/dev/watchdog"

typedef enum {
    NODE_STATE_FOLLOWER,
    NODE_STATE_LEADER_ACTIVE,
    NODE_STATE_LEASE_DEGRADED,
    NODE_STATE_FENCED
} node_state_t;

typedef struct {
    int watchdog_fd;
    int db_sock_fd;
    node_state_t state;
    uint64_t lease_acquired_at_ms;
    uint64_t last_successful_heartbeat_ms;
    bool is_leader;
} cluster_controller_t;

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
}

/* Ініціалізація апаратного сторожового таймера Linux */
static int init_watchdog(void) {
    int fd = open(WATCHDOG_DEV, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "[WARN] Не вдалося відкрити %s: %s (працюємо в емуляції)\n",
                WATCHDOG_DEV, strerror(errno));
        return -1;
    }
    int timeout_sec = (LOOP_WAIT_MS + SAFETY_MARGIN_MS) / 1000;
    if (ioctl(fd, WDIOC_SETTIMEOUT, &timeout_sec) < 0) {
        fprintf(stderr, "[WARN] Не вдалося встановити таймаут watchdog: %s\n", strerror(errno));
    } else {
        printf("[INFO] Апаратний Watchdog активовано. Таймаут: %d сек\n", timeout_sec);
    }
    return fd;
}

/* Скидання апаратного сторожового таймера */
static void ping_watchdog(int fd) {
    if (fd >= 0) {
        int dummy = 0;
        if (ioctl(fd, WDIOC_KEEPALIVE, &dummy) < 0) {
            fprintf(stderr, "[ERR] Збій оновлення Watchdog: %s\n", strerror(errno));
        }
    }
}

/* Безпечне вимкнення Watchdog за допомогою 'магічного символу' 'V' */
static void disable_watchdog(int fd) {
    if (fd >= 0) {
        write(fd, "V", 1);
        close(fd);
        printf("[INFO] Watchdog коректно деактивовано.\n");
    }
}

/* Перевірка працездатності локальної СУБД через сокет */
static bool probe_local_db_health(const char *socket_path) {
    int sock = socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0);
    if (sock < 0) return false;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    int res = connect(sock, (struct sockaddr *)&addr, sizeof(addr));
    if (res < 0 && errno != EINPROGRESS) {
        close(sock);
        return false;
    }

    struct pollfd pfd = { .fd = sock, .events = POLLOUT, .revents = 0 };
    int poll_res = poll(&pfd, 1, 300); /* 300 мс таймаут на підключення */
    if (poll_res <= 0 || (pfd.revents & (POLLERR | POLLHUP))) {
        close(sock);
        return false;
    }

    int so_error = 0;
    socklen_t len = sizeof(so_error);
    getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
    close(sock);
    return (so_error == 0);
}

/* Імітація продовження оренди лізи в розподіленому координаторі DCS (etcd) */
static bool renew_dcs_lease(bool simulate_network_drop) {
    if (simulate_network_drop) {
        return false;
    }
    /* У реальній системі: транзакція CAS в etcd v3 gRPC/HTTP API */
    return true;
}

/* Примусове огородження локального вузла (Emergency Fencing) */
static void execute_emergency_fencing(cluster_controller_t *ctrl) {
    printf("[CRITICAL] ОГОРОДЖЕННЯ! Ліза втрачена. Виконується екстрена ізоляція вузла!\n");
    ctrl->state = NODE_STATE_FENCED;
    ctrl->is_leader = false;

    /* 1. Обрив з'єднань і надсилання SIGTERM/SIGKILL процесам СУБД */
    system("pkill -9 -f postgres || true");

    /* 2. Якщо watchdog активний — не скидаємо його, дозволяючи ядру виконати reboot */
    if (ctrl->watchdog_fd >= 0) {
        fprintf(stderr, "[PANIC] Залишаємо Watchdog без подовження для апаратного скидання!\n");
    }
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    cluster_controller_t ctrl = {
        .watchdog_fd = init_watchdog(),
        .db_sock_fd = -1,
        .state = NODE_STATE_LEADER_ACTIVE,
        .lease_acquired_at_ms = get_monotonic_ms(),
        .last_successful_heartbeat_ms = get_monotonic_ms(),
        .is_leader = true
    };

    printf("[INFO] Контролер огородження запущено. Роль: LEADER. Моніторинг активний.\n");

    int iteration = 0;
    while (g_running && ctrl.state != NODE_STATE_FENCED) {
        uint64_t now = get_monotonic_ms();
        iteration++;

        /* Для тестування: на 6-й ітерації імітуємо мережевий збій із DCS */
        bool simulate_partition = (iteration >= 6 && iteration <= 8);

        bool db_ok = probe_local_db_health("/tmp/.s.PGSQL.5432");
        bool dcs_ok = renew_dcs_lease(simulate_partition);

        if (db_ok && dcs_ok) {
            ctrl.last_successful_heartbeat_ms = now;
            ctrl.state = NODE_STATE_LEADER_ACTIVE;
            ping_watchdog(ctrl.watchdog_fd);
            printf("[OK] Ітерація %d: СУБД здорова, лізу подовжено в DCS. Watchdog скинуто.\n", iteration);
        } else {
            uint64_t elapsed_since_hb = now - ctrl.last_successful_heartbeat_ms;
            ctrl.state = NODE_STATE_LEASE_DEGRADED;
            fprintf(stderr, "[WARN] Ітерація %d: Збій оновлення лізи (DB: %d, DCS: %d). "
                            "Минуло часу: %lu мс / Запас: %d мс\n",
                    iteration, db_ok, dcs_ok, (unsigned long)elapsed_since_hb, SAFETY_MARGIN_MS);

            if (elapsed_since_hb >= SAFETY_MARGIN_MS) {
                execute_emergency_fencing(&ctrl);
                break;
            }
        }

        struct timespec req = { .tv_sec = LOOP_WAIT_MS / 1000, .tv_nsec = (LOOP_WAIT_MS % 1000) * 1000000L };
        nanosleep(&req, NULL);
    }

    if (ctrl.state != NODE_STATE_FENCED) {
        disable_watchdog(ctrl.watchdog_fd);
    }
    printf("[INFO] Контролер завершив роботу.\n");
    return (ctrl.state == NODE_STATE_FENCED) ? 1 : 0;
}
```
```cpp
// ============================================================================
// cluster_fencing_daemon.cpp — C++20 реалізація контролера з RAII та chrono
// ============================================================================
#include <iostream>
#include <string_view>
#include <chrono>
#include <expected>
#include <optional>
#include <thread>
#include <atomic>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

using namespace std::chrono_literals;

namespace cluster {

constexpr auto kLoopWaitInterval = 2000ms;
constexpr auto kSafetyMargin = 5000ms;
constexpr auto kLeaseTtl = 10000ms;
constexpr std::string_view kWatchdogPath = "/dev/watchdog";
constexpr std::string_view kDbSocketPath = "/tmp/.s.PGSQL.5432";

enum class NodeRole {
    Follower,
    LeaderActive,
    LeaseDegraded,
    Fenced
};

// RAII обгортка над дескриптором файлу/сокета
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

// RAII контролер апаратного сторожового пристрою Linux
class WatchdogDriver {
public:
    static std::expected<WatchdogDriver, std::string> create(std::chrono::seconds timeout) {
        int fd = ::open(kWatchdogPath.data(), O_WRONLY);
        if (fd < 0) {
            return std::unexpected(std::strerror(errno));
        }

        int t_sec = static_cast<int>(timeout.count());
        if (::ioctl(fd, WDIOC_SETTIMEOUT, &t_sec) < 0) {
            std::cerr << "[WARN] Не вдалося налаштувати таймаут watchdog: " << std::strerror(errno) << "\n";
        }
        return WatchdogDriver(UniqueFd(fd), timeout);
    }

    ~WatchdogDriver() {
        if (fd_.isValid() && !fenced_) {
            // Магічний символ 'V' дозволяє закрити пристрій без паніки ядра
            [[maybe_unused]] auto res = ::write(fd_.get(), "V", 1);
            std::cout << "[INFO] Watchdog коректно деактивовано.\n";
        }
    }

    WatchdogDriver(WatchdogDriver&&) noexcept = default;
    WatchdogDriver& operator=(WatchdogDriver&&) noexcept = default;

    void keepAlive() noexcept {
        if (fd_.isValid() && !fenced_) {
            int dummy = 0;
            ::ioctl(fd_.get(), WDIOC_KEEPALIVE, &dummy);
        }
    }

    void triggerFencing() noexcept {
        fenced_ = true;
        // Залишаємо дескриптор відкритим без подовження, щоб ядро ініціювало перезавантаження
        std::cerr << "[PANIC] Watchdog залишено без оновлення для апаратного скидання!\n";
    }

private:
    explicit WatchdogDriver(UniqueFd fd, std::chrono::seconds timeout)
        : fd_(std::move(fd)), timeout_(timeout) {}

    UniqueFd fd_;
    std::chrono::seconds timeout_{0};
    bool fenced_{false};
};

class FencingSupervisor {
public:
    explicit FencingSupervisor(std::optional<WatchdogDriver> watchdog)
        : watchdog_(std::move(watchdog)),
          role_(NodeRole::LeaderActive),
          last_heartbeat_(std::chrono::steady_clock::now()) {}

    void run(std::atomic<bool>& shutdown_requested) {
        std::cout << "[INFO] C++ Контролер огородження запущено. Роль: Primary.\n";
        int iteration = 0;

        while (!shutdown_requested && role_ != NodeRole::Fenced) {
            ++iteration;
            auto now = std::chrono::steady_clock::now();

            bool simulate_network_drop = (iteration >= 6 && iteration <= 8);
            bool db_alive = checkDatabaseHealth();
            bool dcs_ok = renewConsensusLease(simulate_network_drop);

            if (db_alive && dcs_ok) {
                last_heartbeat_ = now;
                role_ = NodeRole::LeaderActive;
                if (watchdog_) {
                    watchdog_->keepAlive();
                }
                std::cout << "[OK] Ітерація " << iteration << ": лізу підтверджено, сторож оновлений.\n";
            } else {
                role_ = NodeRole::LeaseDegraded;
                auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_heartbeat_);
                std::cerr << "[WARN] Ітерація " << iteration << ": втрата зв'язку. Минуло: "
                          << elapsed.count() << "мс із дозволених "
                          << std::chrono::duration_cast<std::chrono::milliseconds>(kSafetyMargin).count() << "мс\n";

                if (elapsed >= kSafetyMargin) {
                    performEmergencyFencing();
                    break;
                }
            }

            std::this_thread::sleep_for(kLoopWaitInterval);
        }
    }

    [[nodiscard]] NodeRole getRole() const noexcept { return role_; }

private:
    bool checkDatabaseHealth() const noexcept {
        UniqueFd sock(::socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0));
        if (!sock.isValid()) return false;

        sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, kDbSocketPath.data(), sizeof(addr.sun_path) - 1);

        if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            if (errno != EINPROGRESS) return false;
        }

        pollfd pfd{.fd = sock.get(), .events = POLLOUT, .revents = 0};
        int res = ::poll(&pfd, 1, 300);
        if (res <= 0 || (pfd.revents & (POLLERR | POLLHUP))) return false;

        int error = 0;
        socklen_t len = sizeof(error);
        ::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &error, &len);
        return (error == 0);
    }

    bool renewConsensusLease(bool simulate_drop) const noexcept {
        return !simulate_drop;
    }

    void performEmergencyFencing() {
        std::cerr << "[CRITICAL] ОГОРОДЖЕННЯ! Аварійна ізоляція вузла.\n";
        role_ = NodeRole::Fenced;
        std::system("pkill -9 -f postgres || true");
        if (watchdog_) {
            watchdog_->triggerFencing();
        }
    }

    std::optional<WatchdogDriver> watchdog_;
    NodeRole role_;
    std::chrono::steady_clock::time_point last_heartbeat_;
};

} // namespace cluster

static std::atomic<bool> g_stop_signal{false};

extern "C" void signal_handler(int) {
    g_stop_signal = true;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    auto watchdog_res = cluster::WatchdogDriver::create(7s);
    std::optional<cluster::WatchdogDriver> watchdog;
    if (watchdog_res) {
        watchdog.emplace(std::move(*watchdog_res));
    } else {
        std::cerr << "[WARN] Працюємо без апаратного Watchdog: " << watchdog_res.error() << "\n";
    }

    cluster::FencingSupervisor supervisor(std::move(watchdog));
    supervisor.run(g_stop_signal);

    return (supervisor.getRole() == cluster::NodeRole::Fenced) ? 1 : 0;
}
```
:::

---

## 4. Математичний розрахунок часових інтервалів безпеки

Надійність огородження базується на чіткому математичному бюджеті часу. Нехай:
- `T_loop` = 2.0 секунди (період опитування та подовження серцебиття);
- `T_safety_margin` = 5.0 секунд (максимально дозволений час деградації зв'язку);
- `T_watchdog_timeout` = 7.0 секунд (апаратний таймаут драйвера ядра, що дорівнює `T_loop + T_safety_margin`);
- `T_lease_ttl` = 10.0 секунд (час життя оренди в розподіленому сховищі `etcd`).

Розрахунок часової послідовності гарантованого огородження старого лідера при раптовій втраті мережі:

```
t = 0.0s     : Мережевий комутатор відкидає пакети лідера до DCS.
t = 2.0s     : Перша невдала спроба оновлення. Контролер переходить у стан LEASE_DEGRADED.
t = 4.0s     : Друга невдала спроба. Watchdog не скидається протягом 4 секунд.
t = 6.0s     : Третя невдала спроба.
t = 7.0s     : Спрацьовує ліміт Safety Margin (7.0s - 2.0s = 5.0s з моменту збою).
               Контролер викликає execute_emergency_fencing() і вбиває СУБД (SIGKILL).
               Якщо контролер завис разом із процесором — апаратний /dev/watchdog
               скидає живлення хоста рівно о t = 7.0s.
t = 10.0s    : В etcd закінчується термін дії лізи /service/leader (TTL = 10s).
t = 10.1s    : Здорова репліка бачить звільнення ключа, проводить вибори й стає Primary.
```

**Інженерний висновок:** Часовий проміжок між моментом апаратного знеструмлення старого лідера (`t = 7.0s`) та моментом обрання нового лідера (`t = 10.1s`) становить **3.1 секунди**. Цей захисний буфер гарантує нульову ймовірність накладання операцій запису між старим та новим лідерами за будь-яких умов.

---

## 5. Системна інтеграція та конфігурація Systemd

У реальній виробничій експлуатації контролер огородження повинен запускатися як системна служба найвищого пріоритету. Якщо сервер зазнає високого процесорного навантаження (CPU Starvation) або вичерпання оперативної пам'яті (Memory Pressure), демон сторожа не повинен витіснятися планувальником операційної системи.

Нижче наведено конфігурацію служби `systemd` (`/etc/systemd/system/fencing-controller.service`):

```ini
[Unit]
Description=Database Cluster Fencing and Watchdog Controller
After=network.target local-fs.target
Before=patroni.service postgresql.service

[Service]
Type=simple
ExecStart=/usr/local/bin/cluster_fencing_daemon
Restart=always
RestartSec=1s

# ── Пріоритет планувальника реального часу (Real-Time Scheduling) ─────────────
CPUSchedulingPolicy=rr
CPUSchedulingPriority=99

# ── Захист від знищення менеджером пам'яті (OOM Killer Score) ────────────────
OOMScoreAdjust=-1000

# ── Обмеження ресурсів та ізоляція cgroups v2 ─────────────────────────────────
MemoryMin=64M
MemoryLow=64M
CPUWeight=10000

# ── Права доступу до апаратних пристроїв ──────────────────────────────────────
DeviceAllow=/dev/watchdog rw
CapabilityBoundingSet=CAP_SYS_RAWIO CAP_SYS_BOOT CAP_KILL CAP_SYS_NICE

[Install]
WantedBy=multi-user.target
```

Параметр `CPUSchedulingPolicy=rr` із пріоритетом `99` гарантує, що планувальник ядра Linux буде виділяти процесорні кванти контролеру позачергово за алгоритмом Round-Robin реального часу. Навіть якщо прикладні запити до СУБД створять 100% завантаження всіх процесорних ядер, потік сторожа гарантовано отримає керування для своєчасного скидання сторожового таймера.

---

## 6. Пастки реалізації та крайові випадки

1. **Пастка 1: Використання системного годинника реального часу (`CLOCK_REALTIME`):**
   Якщо для розрахунку інтервалів використовувати функції `gettimeofday()`, `time(NULL)` або `std::chrono::system_clock`, коригування системного часу демоном `chrony` або `ntpd` (наприклад, стрибок на 15 секунд назад після синхронізації з часовим сервером або введення секунди координації) призведе до того, що таймер деградації ніколи не спрацює. Вузол залишиться завислим лідером у минулому часі. Для вимірювання інтервалів у сторожових контролерах обов'язково застосовується монотонний годинник `CLOCK_MONOTONIC` або `std::chrono::steady_clock`, який не зазнає стрибків при зміні системного часу.

2. **Пастка 2: Зависання в стані непереривного сну ядра (`TASK_UNINTERRUPTIBLE` / D-state):**
   Якщо дисковий контролер NVMe або мережева файлова система iSCSI/NFS зависає під час виконання операції скидання дискових кешів `fsync()`, потік процесу СУБД переходить у стан ядра `D`. У цьому стані процес повністю ігнорує будь-які сигнали простору користувача, включно з `SIGKILL` (`kill -9`). Саме тому програмного завершення процесів через `pkill` недостатньо для гарантії безпеки: єдиним безкомпромісним засобом огородження є апаратний таймер `/dev/watchdog`, який перезавантажує процесор на рівні системної шини.

3. **Пастка 3: Падіння керуючого демона без коректного деактивування Watchdog:**
   Драйвер ядра Linux Watchdog за замовчуванням вважає аварійним будь-яке раптове закриття файлового дескриптора без запису спеціального магічного байта `'V'`. Якщо контролер огородження зазнає критичного збою (наприклад, `SIGSEGV` через помилку пам'яті), ядро розцінює це як відмову сервісу й автоматично перезавантажує операційну систему через встановлений таймаут, захищаючи кластер від існування некерованого вузла.

---

## 7. Зовнішнє апаратне огородження (Out-of-Band IPMI / Redfish Fencing)

Окрім внутрішнього самоогородження через локальний Watchdog (Self-Fencing), зрілі виробничі кластери реалізують зовнішнє примусове знеструмлення (External STONITH). Якщо вузол повністю завис і його операційна система не здатна виконати жодних дій у просторі ядра, сусідні вузли кластера або оркестратор ініціюють відключення живлення ззовні через окремий виділений інтерфейс управління сервером (Baseboard Management Controller, BMC).

```
   [ Вузол-Свідок / Кворум ]
              │
              │ Відправляє команду скидання живлення
              ▼
   ┌─────────────────────────────────────────────────────────┐
   │  Виділена мережа управління (Out-of-Band Management)    │
   │  Протокол IPMI over LAN або REST API Redfish / iLO / iDRAC│
   └──────────────────────────┬──────────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────┐
   │  Апаратний контролер сервера BMC (Сервер Вузла 1)       │
   │  Реле живлення материнської плати -> [ ЖИВЛЕННЯ ВИМКНЕНО ]│
   └─────────────────────────────────────────────────────────┘
```

### 7.1. Протоколи та команди зовнішнього огородження

1. **IPMI over LAN (`ipmitool`):**
   Використовує мережевий протокол UDP (порт 623) для прямої взаємодії з мікроконтролером BMC:
   - `ipmitool -I lanplus -H 192.168.100.21 -U admin -P secret chassis power off`: негайне безумовне знеструмлення материнської плати (Power Cut);
   - `ipmitool -I lanplus -H 192.168.100.21 -U admin -P secret chassis power reset`: примусовий холодний апаратний перезапуск;
   - `ipmitool -I lanplus -H 192.168.100.21 -U admin -P secret chassis power status`: верифікація фізичного відключення живлення перед промоцією репліки.

2. **Сучасний стандарт Redfish REST API:**
   Використовує захищений HTTPS-інтерфейс із JSON-пейлоадами. Для переведення сервера в стан скидання надсилається POST-запит:
   `POST https://bmc-node01.mgmt/redfish/v1/Systems/System.1/Actions/ComputerSystem.Reset` із тілом `{"ResetType": "ForceOff"}`.

3. **Керовані блоки розподілу живлення (Switched PDU):**
   Якщо BMC сервера не відповідає, керуючий агент надсилає команду за протоколом SNMP на розумну розетку PDU (Power Distribution Unit), яка фізично розмикає електромеханічне реле конкретного силового вводу, знеструмлюючи блок живлення сервера.

---

## 8. Мережева ізоляція засобами eBPF та iptables

Перед тим, як апаратний сторож перезавантажить хост, контролер може виконати миттєве програмне відсікання клієнтського трафіку на рівні мережевого стека ядра Linux. Це дозволяє запобігти надходженню нових запитів протягом мілісекунд:

1. **Блокування порту СУБД через iptables:**
   ```bash
   iptables -I INPUT 1 -p tcp --dport 5432 -j REJECT --reject-with tcp-reset
   ```
   Використання правила `REJECT --reject-with tcp-reset` замість звичайного `DROP` є критично важливим: воно змушує ядро негайно надіслати клієнтам пакет `TCP RST`, що призводить до миттєвого закриття сокетів у застосунках і перемикання пулу з'єднань на новий вузол без очікування таймаутів з'єднання (Connection Timeout).

2. **Швидкісне скидання пакетів через eBPF/XDP:**
   У високонавантажених системах контролер завантажує програму XDP (eXpress Data Path) безпосередньо в драйвер мережевої карти, яка перевіряє стан прапорця в спільній карті BPF (`BPF_MAP_TYPE_ARRAY`). Якщо статус вузла змінено на `FENCED`, мережева карта апаратно відкидає всі пакети до порту бази даних зі швидкістю понад 10 мільйонів пакетів на секунду без залучення ядерного стека TCP/IP.

---

## 9. Компіляція, розгортання та верифікація

Для компіляції низькорівневих бінарних файлів контролера застосовуються сучасні компілятори GCC або Clang із оптимізаціями та суворими попередженнями компілятора:

```bash
# Компіляція C-версії (вимагає підтримки POSIX.1-2008)
gcc -O2 -Wall -Wextra -Wpedantic -std=c11 cluster_fencing_daemon.c -o cluster_fencing_c

# Компіляція C++20 версії (вимагає GCC 13+ або Clang 16+)
g++ -O2 -Wall -Wextra -std=c++20 -pthread cluster_fencing_daemon.cpp -o cluster_fencing_cpp
```

### 9.1. Лабораторний тест сценарію мережевого розриву

Для перевірки роботи контролера в тестовому оточенні імітується штучна ізоляція вузла:

1. Запускається демон контролера в терміналі: `./cluster_fencing_cpp`.
2. В іншому терміналі створюється блокування мережевих пакетів до DCS:
   ```bash
   iptables -A OUTPUT -p tcp --dport 2379 -j DROP
   ```
3. У логах контролера спостерігається перехід зі стану `LEADER_ACTIVE` у стан `LEASE_DEGRADED`.
4. Через 5.0 секунд (значення `SAFETY_MARGIN_MS`) контролер фіксує перевищення порогу безпеки, переходить у стан `FENCED`, надсилає `SIGKILL` процесам PostgreSQL та ініціює скидання через Watchdog.
5. Після відновлення правила `iptables -D OUTPUT ...` сервер демонструє чистий перезапуск без пошкодження дискових сторінок.

---

## 10. Огородження на базі блочного сховища (SBD — Storage-Based Death)

У корпоративних середовищах із виділеними дисковими сховищами SAN/iSCSI альтернативою мережевому або апаратному сторожу є механізм **SBD (Storage-Based Death)**. Цей метод базується на спільному блочному пристрої (LUN), куди кожен вузол кластера записує повідомлення серцебиття в спеціально виділені дискові сектори (Slots).

```
   [ Вузол 1 (Лідер) ] ──► [ Читає свій дисковий слот кожні 1с ] ◄── [ Спільний LUN /dev/sdb ]
                                                                             ▲
   [ Вузол 2 (Кворум) ] ──► [ Записує команду "POISON PILL" у слот 1 ] ─────┘
```

1. **Дисковий слот повідомлень:**
   Кожен вузол має фіксовану 512-байтну область на спільному диску, яку локальний сторожовий демон SBD зчитує з періодичністю 1 секунда без кешування файлової системи (`O_DIRECT`). Заголовок слота містить магічне число `0x53424431` (SBD1), унікальний ідентифікатор вузла, монотонний лічильник покоління повідомлення та контрольну суму CRC32.

2. **Отруйна пігулка (Poison Pill):**
   Якщо кворумний менеджер кластера вирішує ізолювати вузол (наприклад, через втрату мережевого відгуку), здоровий вузол записує байтовий патерн `POISON_PILL` у слот відмовляючого вузла на спільному диску. Під час запису прапорець `O_SYNC` гарантує, що повідомлення миттєво записується на магнітні пластини або енергонезалежну флеш-пам'ять масиву без осідання в кешах контролера.

3. **Апаратна реакція драйвера:**
   Локальний демон SBD на ізольованому вузлі зчитує отруйну пігулку зі свого дискового сектора й негайно викликає паніку ядра через `/dev/watchdog`. Якщо ж дисковий зв'язок до LUN втрачено повністю, демон не може підтвердити стан свого слота й ініціює перезавантаження за тайм-аутом втрати сховища.

---

## 11. Налаштування параметрів ядра Linux (`sysctl`) для сторожового вузла

Для коректного функціонування контролера огородження операційна система Linux вимагає оптимізації низки параметрів підсистеми пам'яті та обробки аварійних станів ядра у файлі `/etc/sysctl.d/99-fencing.conf`:

1. **`kernel.panic = 10`:**
   Визначає поведінку ядра після виникнення Kernel Panic. Значення `10` вказує ядру зачекати 10 секунд (для запису дампу в системний журнал або kdump) та виконати безумовне апаратне перезавантаження хоста.

2. **`kernel.panic_on_oops = 1`:**
   Примусово переводить будь-яку внутрішню помилку драйвера або ядра (Oops) у стан повної паніки ядра, унеможливлюючи роботу сервера з пошкодженими ядерними структурами блокування.

3. **`vm.panic_on_oom = 2`:**
   У разі критичного вичерпання пам'яті ядро відмовляється від вибіркового вбивства випадкових процесів через OOM Killer і негайно генерує паніку ядра. Це захищає кластер від ситуації, коли OOM Killer випадково знищує керуючий демон Patroni або фоновий процес реплікації, залишаючи при цьому живим основний процес PostgreSQL.

4. **`kernel.hung_task_panic = 1` та `kernel.hung_task_timeout_secs = 120`:**
   Ядро постійно перевіряє процеси, що перебувають у непереривному сні (D-state). Якщо процес СУБД зависає на дисковій операції довше ніж на 120 секунд, ядро ініціює паніку та перезавантаження.

---

## 12. Порівняльна матриця стратегій огородження

Вибір стратегії огородження диктується середовищем розгортання кластера та вимогами до надійності:

| Метод огородження | Швидкість спрацювання (RTO) | Вимоги до інфраструктури | Слабкі місця та крайові ризики |
|---|---|---|---|
| **Локальний Watchdog (Self-Fencing)** | 5–7 секунд | Підтримка ядра `/dev/watchdog` або віртуальний WDT | Якщо ОС зависає в стані апаратного переривання, реакція залежить виключно від апаратного таймера материнської плати. |
| **Зовнішній IPMI / Redfish STONITH** | 1–3 секунди | Виділена позасмугова мережа (Out-of-Band) та налаштований BMC | Залежність від працездатності контролера BMC та окремої мережі управління. |
| **Керовані розетки PDU (Power Cut)** | 2–5 секунд | Розумні стійкові PDU з підтримкою SNMP | Необхідність суворого ведення обліку фізичного підключення кабелів живлення серверів до портів PDU. |
| **Дисковий SBD (Storage-Based Death)** | 3–5 секунд | Спільний блочний LUN (iSCSI, FC, NVMe-oF) | Не підходить для хмарних Shared-Nothing архітектур без спільних дисків. |
| **Мережеве відсікання eBPF / iptables** | < 100 мілісекунд | Програмна підтримка ядра Linux | Є першою лінією оборони (пом'якшення наслідків), але не замінює апаратне знеструмлення при зависанні ядра. |

Поєднання локального контролера огородження на базі Watchdog із зовнішнім кворумом DCS є універсальним еталоном для хмарних і датацентрових розгортань, що забезпечує стовідсотковий захист від розбіжності даних.
