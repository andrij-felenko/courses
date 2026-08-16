# ⚙️ Демон супервізії та сторожового таймера

У надійних автономних системах, мобільних роботах, промислових контролерах та серверних вузлах просте надсилання регулярних пінгів у пристрій `/dev/watchdog` є недостатнім. Якщо демон супервізії продовжує пингувати апаратний таймер, коли критичні сервіси бази даних зависли у Deadlock або оперативна пам'ять вичерпана через витік, сторожовий таймер не зможе виконати свою головну функцію — перезавантажити несправний вузол. 

У цій практичній вставці розглядається повна реалізація промислового демона супервізії мовами C та C++, який поєднує комплексний моніторинг системних ресурсів (використання RAM та доступність системи) із безпечним закриттям Magic Close через `ioctl` інтерфейс ядра Linux, а також його інтеграція у конфігурації `systemd`.

## 1. Архітектура та етапи роботи демона

Розробка промислового демона супервізії передбачає виконання трьох послідовних фаз:

1. **Ініціалізація та конфігурація**: Відкриття пристрою `/dev/watchdog` у режимі читання-запису з прапорцем `O_CLOEXEC`, зчитування можливостей апаратури `WDIOC_GETSUPPORT`, налаштування бажаного таймауту `WDIOC_SETTIMEOUT` та реєстрація асинхронних обробників сигналів `SIGTERM`/`SIGINT` для штатного вимкнення.
2. **Цикл моніторингу та здоров'я (Health Check Loop)**: Періодичний аналіз системних метрик (читання та парсинг `/proc/meminfo` для оцінки доступної пам'яті). Якщо метрики знаходяться у безпечних межах, демон надсилає сигнал Heartbeat через `ioctl(fd, WDIOC_KEEPALIVE, 0)`. Якщо виявлено критичну деградацію пам'яті або зависання системи, демон навмисно припиняє надсилання пінгів і дозволяє апаратному таймеру перезавантажити вузол.
3. **Безпечний вихід (Magic Close)**: При отриманні команд штатного зупинення (`SIGTERM`) демон записує символ `'V'` у дескриптор пристрою перед його закриттям, передаючи ядру команду зупинити апаратний зворотний відлік.

## 2. Реалізація демона супервізії

Приклади нижче демонструють реалізацію мовою C (із використанням низькорівневих POSIX-системних викликів) та ідіоматичною мовою C++ (із застосуванням принципу RAII, шаблонів обробки винятків `std::system_error` та методів стандартної бібліотеки).

:::tabs
```c
/* Демон супервізії сторожового таймера на мові C (Linux POSIX API) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/watchdog.h>

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

/* Перевірка стану ресурсів системи */
static int check_system_health(void) {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (!fp) {
        perror("Не вдалося відкрити /proc/meminfo");
        return -1;
    }

    long mem_total = 0, mem_available = 0;
    char line[128];
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "MemTotal: %ld kB", &mem_total) == 1) continue;
        if (sscanf(line, "MemAvailable: %ld kB", &mem_available) == 1) continue;
    }
    fclose(fp);

    if (mem_total > 0 && mem_available > 0) {
        double free_ratio = (double)mem_available / (double)mem_total;
        /* Якщо доступної пам'яті менше 2%, вважаємо стан системи критичним */
        if (free_ratio < 0.02) {
            fprintf(stderr, "Критична нестача пам'яті: %.2f%% вільно\n", free_ratio * 100.0);
            return 0;
        }
    }
    return 1; /* Система здорова */
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/watchdog";
    int req_timeout = 30; /* Таймаут 30 секунд */

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    int fd = open(dev_path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", dev_path, strerror(errno));
        return EXIT_FAILURE;
    }

    struct watchdog_info info;
    if (ioctl(fd, WDIOC_GETSUPPORT, &info) == 0) {
        printf("Watchdog: %s, прошивка: %u, опції: 0x%X\n",
               info.identity, info.firmware_version, info.options);
    }

    if (ioctl(fd, WDIOC_SETTIMEOUT, &req_timeout) == 0) {
        printf("Встановлено таймаут %d секунд\n", req_timeout);
    } else {
        perror("Не вдалося встановити таймаут через WDIOC_SETTIMEOUT");
    }

    int ping_interval = req_timeout / 2;
    if (ping_interval < 1) ping_interval = 1;
    printf("Розпочато моніторинг з інтервалом пінгу %d с...\n", ping_interval);

    while (g_running) {
        if (check_system_health()) {
            if (ioctl(fd, WDIOC_KEEPALIVE, 0) < 0) {
                perror("Помилка WDIOC_KEEPALIVE");
            } else {
                printf("[OK] Heartbeat надіслано в %s\n", dev_path);
            }
        } else {
            fprintf(stderr, "[WARN] Зупинка пингу через критичні метрики системи!\n");
        }
        sleep((unsigned int)ping_interval);
    }

    /* Штатне зупинення за допомогою Magic Close */
    printf("Штатне завершення: надсилання Magic Close 'V'...\n");
    const char magic_v = 'V';
    if (write(fd, &magic_v, 1) < 0) {
        perror("Помилка запису Magic Close");
    }

    close(fd);
    printf("Сторожовий таймер зупинено.\n");
    return EXIT_SUCCESS;
}
```
```cpp
// Демон супервізії сторожового таймера на мові C++ (C++20 RAII & System Interfaces)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <atomic>
#include <csignal>
#include <cerrno>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

namespace {
std::atomic<bool> g_running{true};

void signal_handler(int) {
    g_running.store(false);
}
}

class WatchdogDevice {
public:
    explicit WatchdogDevice(std::string_view path, int timeout_sec)
        : dev_path_(path) {
        fd_ = ::open(dev_path_.c_str(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Failed to open watchdog device " + dev_path_);
        }

        struct watchdog_info info{};
        if (::ioctl(fd_, WDIOC_GETSUPPORT, &info) == 0) {
            identity_ = reinterpret_cast<const char*>(info.identity);
            supports_magic_close_ = (info.options & WDIOF_MAGICCLOSE) != 0;
        }

        int t = timeout_sec;
        if (::ioctl(fd_, WDIOC_SETTIMEOUT, &t) == 0) {
            active_timeout_ = t;
        } else {
            active_timeout_ = timeout_sec;
        }
    }

    ~WatchdogDevice() {
        if (fd_ >= 0) {
            if (supports_magic_close_) {
                const char v = 'V';
                [[maybe_unused]] auto ret = ::write(fd_, &v, 1);
            }
            ::close(fd_);
        }
    }

    WatchdogDevice(const WatchdogDevice&) = delete;
    WatchdogDevice& operator=(const WatchdogDevice&) = delete;

    WatchdogDevice(WatchdogDevice&& other) noexcept 
        : fd_(other.fd_), dev_path_(std::move(other.dev_path_)),
          identity_(std::move(other.identity_)),
          active_timeout_(other.active_timeout_),
          supports_magic_close_(other.supports_magic_close_) {
        other.fd_ = -1;
    }

    void keep_alive() {
        if (::ioctl(fd_, WDIOC_KEEPALIVE, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "WDIOC_KEEPALIVE failed");
        }
    }

    [[nodiscard]] int timeout() const noexcept { return active_timeout_; }
    [[nodiscard]] const std::string& identity() const noexcept { return identity_; }

private:
    int fd_{-1};
    std::string dev_path_;
    std::string identity_;
    int active_timeout_{30};
    bool supports_magic_close_{false};
};

bool is_system_healthy() {
    std::ifstream meminfo("/proc/meminfo");
    if (!meminfo.is_open()) return true;  // немає /proc/meminfo — це не привід глушити Heartbeat

    std::string key;
    long value = 0;
    std::string unit;
    long total_kb = 0, avail_kb = 0;

    while (meminfo >> key >> value >> unit) {
        if (key == "MemTotal:") total_kb = value;
        else if (key == "MemAvailable:") avail_kb = value;
    }

    if (total_kb > 0 && avail_kb > 0) {
        double ratio = static_cast<double>(avail_kb) / static_cast<double>(total_kb);
        return ratio >= 0.02; // Поріг здоров'я — мінімум 2% вільної RAM
    }
    return true;
}

int main(int argc, char* argv[]) {
    std::string_view dev = (argc > 1) ? argv[1] : "/dev/watchdog";

    std::signal(SIGTERM, signal_handler);
    std::signal(SIGINT, signal_handler);

    try {
        WatchdogDevice wd(dev, 30);
        std::cout << "Watchdog initialized: " << wd.identity() 
                  << " (Timeout: " << wd.timeout() << "s)\n";

        const auto ping_interval = std::chrono::seconds(wd.timeout() / 2);

        while (g_running.load()) {
            if (is_system_healthy()) {
                wd.keep_alive();
                std::cout << "[Heartbeat] Ping sent to " << dev << '\n';
            } else {
                std::cerr << "[CRITICAL] Health check failed, ping suppressed!\n";
            }
            std::this_thread::sleep_for(ping_interval);
        }

        std::cout << "Gracefully shutting down supervisor daemon...\n";
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 3. Інтеграція у юніт-файл systemd

Для автоматичного запуску та супервізії самого демона створюється юніт-файл `/etc/systemd/system/watchdogd.service`:

```ini
[Unit]
Description=Custom Hardware Watchdog Supervisor Daemon
Documentation=man:watchdog(8)
DefaultDependencies=no
Before=sysinit.target shutdown.target
Conflicts=shutdown.target

[Service]
Type=notify
ExecStart=/usr/local/bin/watchdogd /dev/watchdog
Restart=always
RestartSec=1s
# Захист пам'яті та реального часу
LimitMEMLOCK=infinity
CPUSchedulingPolicy=fifo
CPUSchedulingPriority=99
MemoryMax=64M

[Install]
WantedBy=multi-user.target
```

Параметри `CPUSchedulingPolicy=fifo` та `CPUSchedulingPriority=99` переводять демон у режим реального часу `SCHED_FIFO`, що різко зменшує затримку виклику `ioctl` під високим навантаженням (повністю усунути її не може ніщо: лишаються сторінкові помилки й непереривні секції ядра).

## 4. Протокол sd_notify та повідомлення супервізора

У високонадійних сервісах демон супервізії повідомляє `systemd` про свій стан через UNIX domain dgram сокет `NOTIFY_SOCKET`. Демон відправляє текст `WATCHDOG=1` у сокет при кожній успішній перевірці метрик:

:::tabs
```c
/* Відправка протокольного повідомлення в systemd notify socket (C API) */
#include <sys/socket.h>
#include <sys/un.h>
#include <stdlib.h>

static void notify_systemd_watchdog(void) {
    const char *socket_path = getenv("NOTIFY_SOCKET");
    if (!socket_path) return;

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        strncpy(addr.sun_path + 1, socket_path + 1, sizeof(addr.sun_path) - 2);
    } else {
        strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);
    }

    const char msg[] = "WATCHDOG=1\nREADY=1";
    sendto(fd, msg, sizeof(msg) - 1, 0, (struct sockaddr*)&addr, sizeof(addr));
    close(fd);
}
```
```cpp
// Відправка протокольного повідомлення в systemd notify socket (C++ API)
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <string_view>
#include <system_error>

void notify_systemd_watchdog_cpp() {
    const char* socket_path = std::getenv("NOTIFY_SOCKET");
    if (!socket_path) return;

    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::strncpy(addr.sun_path + 1, socket_path + 1, sizeof(addr.sun_path) - 2);
    } else {
        std::strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);
    }

    constexpr std::string_view msg = "WATCHDOG=1\nREADY=1";
    ::sendto(fd, msg.data(), msg.size(), 0, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr));
    ::close(fd);
}
```
:::

Використання сокета `NOTIFY_SOCKET` дозволяє PID 1 перевіряти активність демона без викликів за розкладом. Якщо повідомлення `WATCHDOG=1` не надійшло протягом усього інтервалу `WatchdogSec`, `systemd` вважає службу завислою й застосовує до неї політику перезапуску; надсилати ж його рекомендують удвічі частіше — приблизно раз на `WatchdogSec/2`, щоб мати запас на затримки.

## 5. Простеження та діагностика через strace

Перевірити коректність відправки Heartbeat та запису Magic Close можна за допомогою утиліти `strace`:

```bash
strace -e openat,ioctl,write,close /usr/local/bin/watchdogd /dev/watchdog0
```

Типова послідовність викликів демонструє нормальний цикл роботи:

```text
openat(AT_FDCWD, "/dev/watchdog0", O_RDWR|O_CLOEXEC) = 3
ioctl(3, WDIOC_GETSUPPORT, {options=WDIOF_SETTIMEOUT|WDIOF_MAGICCLOSE, firmware_version=1, identity="iTCO_wdt"}) = 0
ioctl(3, WDIOC_SETTIMEOUT, [30])        = 0
ioctl(3, WDIOC_KEEPALIVE, 0)            = 0
--- SIGTERM {si_signo=SIGTERM, si_code=SI_USER} ---
write(3, "V", 1)                        = 1
close(3)                                = 0
```

## 6. Тестування на базі програмного емулятора softdog

Для безпечного зневадження демона без ризику перезавантаження реального фізичного сервера розробники використовують програмний модуль `softdog`:

```bash
# Завантаження емулятора з таймаутом 15 секунд
sudo modprobe softdog soft_margin=15

# Запуск демона на програмному таймері
/usr/local/bin/watchdogd /dev/watchdog0
```

Спроба зупинити демон командою `kill -9 <PID>` (SIGKILL) надсилає примусовий сигнал, який демон не може перехопити. Оскільки Magic Close `'V'` не надсилається, ядро зафіксує аварійне закриття, і через 15 секунд `softdog` аварійно перезапустить систему через `emergency_restart()` (а з параметром `soft_panic=1` — через `panic()`).

## 7. Критичні системні пастки при розробці

Під час проектування виробничих демонів супервізії розробник повинен враховувати такі підводні камені ядра Linux:

1. **Захист від витіснення в підкачку (`mlockall`)**: Якщо у системі виникає високий дефіцит RAM, процес демона супервізії може бути частково витіснений у підкачку (Swap). Коли настає час надсилати Heartbeat, звернення демона до сторінок пам'яті викличе затримку на I/O-операції зі свапом. Якщо затримка перевищить апаратний таймаут, станеться примусове перезавантаження. Промислові демони зобов'язані викликати системний виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` одразу при запуску та підвищувати свій пріоритет реального часу через `sched_setscheduler(0, SCHED_FIFO, &param)`.
2. **Монопольний доступ до пристрою (`EBUSY`)**: монополія тут не залежить від прапорців `open()` — її тримає сама підсистема `watchdog_dev`, яка допускає лише один відкритий дескриптор символьного пристрою `/dev/watchdog` одночасно. Спроба другого процесу (наприклад, паралельно запущеного демона моніторингу) відкрити цей же пристрій поверне помилку `EBUSY`.
3. **Пастка конфігурації `nowayout`**: Якщо драйвер завантажено з параметром `nowayout=1`, ядро ігнорує будь-яку спробу записати символ Magic Close `'V'` — це рішення підсистеми, а не заборона в кремнії. У такому разі виклик `close()` не зупинить зворотний відлік, і при зупинці демона служба повинна або продовжувати пінги, або передати володіння дескриптором головному процесу ініціалізації PID 1.
4. **Обробка сигналів та аварійне завершення**: У разі отримання сигналів аварійного згортання на зразок `SIGSEGV` чи `SIGBUS` операційна система не виконує обробник `SIGTERM`. Отже, запис символу Magic Close не відбувається, що гарантує спрацювання апаратного таймера при критичному збої самого супервізора.

Врахування всіх чотирьох пасток забезпечує створення безвідмовної архітектури супервізії, стійкої як до програмних помилок демона, так і до критичних навантажень на оперативну пам'ять та дискову підсистему Linux.
