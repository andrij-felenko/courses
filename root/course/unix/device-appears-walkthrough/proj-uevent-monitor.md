# ⚙️ Монітор подій ядра через Netlink: читання uevent у реальному часі

Цей проект демонструє створення повнофункціональної утиліти для перехоплення апаратних сповіщень ядра Linux у реальному часі через сирий сокет протоколу `NETLINK_KOBJECT_UEVENT` без використання зовнішніх бібліотек чи посередництва системного демона `systemd-udevd`.

У середовищі Linux системний демон `udevd` не має ексклюзивного доступу до потоку апаратних подій. Ядро транслює кожну зміну стану пристрою у широкомовну групу `1` сокета Netlink. Будь-який процес із відповідними правами може створити власний сокет `AF_NETLINK`, підписатися на цю групу та безпосередньо отримувати бінарні пакети подій. Це дозволяє створювати надшвидкі спеціалізовані монітори для вбудованих систем, діагностичні утиліти часу виконання та демони швидкого реагування на під'єднання заліза.

---

## 1. Архітектурна модель перехоплення подій через Netlink

Родина сокетів Netlink (англ. *Netlink Sockets*) розроблена як асинхронний дуплексний канал зв'язку між простором ядра та процесами простору користувача. На відміну від стандартних сокетів `AF_UNIX` або `AF_INET`, Netlink не створює файлів у файловій системі та не вимагає мережевих інтерфейсів, а передає повідомлення через структури сокетних буферів ядра `struct sk_buff`.

Для підсистеми керування об'єктами виділено окремий числовий протокол `NETLINK_KOBJECT_UEVENT` (число `15` у системних заголовках).

```
┌──────────────────────────────────────────────────────────────────┐
│                          ПРОСТІР ЯДРА                            │
│  Апаратне переривання ──> Детектування ──> kobject_uevent()      │
│                                                   │              │
│                                    netlink_broadcast(group=1)    │
└───────────────────────────────────────────────────┼──────────────┘
                                                    │ [sk_buff]
════════════════════════════════════════════════════╪═══════════════
                                                    │
┌───────────────────────────────────────────────────▼──────────────┐
│                    ПРОСТІР КОРИСТУВАЧА                           │
│  socket(AF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT)            │
│  bind(sa_family=AF_NETLINK, nl_groups=1)                         │
│                                                                  │
│  ┌────────────────────────┐          ┌────────────────────────┐  │
│  │     systemd-udevd      │          │     uevent_monitor     │  │
│  │ (обробка правил, /dev) │          │ (наша утиліта аналізу) │  │
│  └────────────────────────┘          └────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

Коли ядро викликає функцію `kobject_uevent()`, воно формує пакет, який містить:
1. Заголовок події — рядок вигляду `add@/devices/...`, завершений нульовим байтом `\0`.
2. Список змінних оточення — послідовність рядків `КЛЮЧ=ЗНАЧЕННЯ`, кожен із яких завершується нульовим байтом `\0`.

Утиліта підключається до сокета, читає пакет у лінійний буфер через системний виклик `recv()` або `recvmsg()` та розбирає нуль-терміновані пари без додаткового копіювання пам'яті.

---

## 2. Повна реалізація утиліти на мовах C та C++

Нижче наведено паралельні реалізації монітора: класичну версію мовою C (POSIX-сумісний системний код) та сучасну ідіоматичну версію на C++23, де безпека ресурсів забезпечується класом RAII, обробка помилок спирається на `std::expected`, а парсинг рядків виконується через `std::string_view` з нульовим динамічним виділенням пам'яті на купі.

:::tabs
```c
/* uevent_monitor.c — Системний монітор подій ядра Linux на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 16384
#define SOCKET_RECV_BUFFER (2 * 1024 * 1024) /* 2 МБ для запобігання ENOBUFS */

static volatile sig_atomic_t g_stop = 0;

static void handle_signal(int sig)
{
    (void)sig;
    g_stop = 1;
}

/* Структура для збереження покажчиків на витягнуті параметри події */
struct uevent_fields {
    const char *action;
    const char *devpath;
    const char *subsystem;
    const char *devname;
    const char *modalias;
    const char *seqnum;
    const char *major;
    const char *minor;
    const char *driver;
};

static void parse_uevent_buffer(const char *buf, ssize_t len, struct uevent_fields *fields)
{
    fields->action = "N/A";
    fields->devpath = "N/A";
    fields->subsystem = "N/A";
    fields->devname = NULL;
    fields->modalias = NULL;
    fields->seqnum = "N/A";
    fields->major = NULL;
    fields->minor = NULL;
    fields->driver = NULL;

    /* Перший рядок у пакеті — заголовок вигляду "add@/devices/..." */
    const char *header = buf;
    size_t header_len = strlen(header);
    const char *ptr = buf + header_len + 1;
    const char *end = buf + len;

    /* Ітеруємося по нуль-термінованих рядках KEY=VALUE */
    while (ptr < end && *ptr != '\0') {
        if (strncmp(ptr, "ACTION=", 7) == 0) {
            fields->action = ptr + 7;
        } else if (strncmp(ptr, "DEVPATH=", 8) == 0) {
            fields->devpath = ptr + 8;
        } else if (strncmp(ptr, "SUBSYSTEM=", 10) == 0) {
            fields->subsystem = ptr + 10;
        } else if (strncmp(ptr, "DEVNAME=", 8) == 0) {
            fields->devname = ptr + 8;
        } else if (strncmp(ptr, "MODALIAS=", 9) == 0) {
            fields->modalias = ptr + 9;
        } else if (strncmp(ptr, "SEQNUM=", 7) == 0) {
            fields->seqnum = ptr + 7;
        } else if (strncmp(ptr, "MAJOR=", 6) == 0) {
            fields->major = ptr + 6;
        } else if (strncmp(ptr, "MINOR=", 6) == 0) {
            fields->minor = ptr + 6;
        } else if (strncmp(ptr, "DRIVER=", 7) == 0) {
            fields->driver = ptr + 7;
        }

        /* Переходимо до наступного рядка за нульовим байтом */
        ptr += strlen(ptr) + 1;
    }
}

static void print_uevent(const struct uevent_fields *f)
{
    printf("────────────────────────────────────────────────────────────────\n");
    printf("[UEVENT #%-6s] ДІЯ: %-8s | ПІДСИСТЕМА: %s\n", f->seqnum, f->action, f->subsystem);
    printf("  Шлях у sysfs:  /sys%s\n", f->devpath);

    if (f->devname) {
        if (f->major && f->minor) {
            printf("  Нода у /dev:   /dev/%s (major:minor = %s:%s)\n", f->devname, f->major, f->minor);
        } else {
            printf("  Нода у /dev:   /dev/%s\n", f->devname);
        }
    }

    if (f->driver) {
        printf("  Драйвер ядра:  %s\n", f->driver);
    }

    if (f->modalias) {
        printf("  MODALIAS:      %s\n", f->modalias);
    }
}

int main(void)
{
    struct sigaction sa_sig;
    memset(&sa_sig, 0, sizeof(sa_sig));
    sa_sig.sa_handler = handle_signal;
    sigaction(SIGINT, &sa_sig, NULL);
    sigaction(SIGTERM, &sa_sig, NULL);

    int sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
    if (sock_fd < 0) {
        perror("Помилка створення сокета Netlink");
        return EXIT_FAILURE;
    }

    /* Встановлюємо розмір буфера прийому ядра */
    int buf_size = SOCKET_RECV_BUFFER;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size)) < 0) {
        perror("Попередження: не вдалося встановити SO_RCVBUF");
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_pid = 0;       /* 0 дозволяє ядру призначити власний унікальний ID */
    sa.nl_groups = 1;   /* 1 — багатоадресна група подій kobject ядра */

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки bind() до групи Netlink");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    printf("================================================================\n");
    printf(" Монітор подій Netlink uevent запущено (Ctrl+C для виходу)\n");
    printf(" Очікування повідомлень ядра про під'єднання пристроїв...\n");
    printf("================================================================\n");

    char buffer[UEVENT_BUFFER_SIZE];
    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLIN;

    while (!g_stop) {
        int ret = poll(&pfd, 1, 500); /* 500 мс таймаут для перевірки g_stop */
        if (ret < 0) {
            if (errno == EINTR)
                continue;
            perror("Помилка опитування poll()");
            break;
        }
        if (ret == 0)
            continue;

        if (pfd.revents & POLLIN) {
            ssize_t len = recv(sock_fd, buffer, sizeof(buffer) - 1, MSG_DONTWAIT);
            if (len < 0) {
                if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK)
                    continue;
                if (errno == ENOBUFS) {
                    fprintf(stderr, "УВАГА: переповнення буфера сокета (ENOBUFS). Частину подій втрачено.\n");
                    continue;
                }
                perror("Помилка виклику recv()");
                break;
            }

            if (len == 0)
                continue;

            buffer[len] = '\0';
            struct uevent_fields fields;
            parse_uevent_buffer(buffer, len, &fields);
            print_uevent(&fields);
            fflush(stdout);
        }
    }

    printf("\nЗавершення роботи монітора uevent. Закриття сокета.\n");
    close(sock_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// uevent_monitor.cpp — Ідіоматичний монітор uevent на C++23
#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <format>
#include <expected>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <linux/netlink.h>

namespace netlink {

// Безпечна RAII обгортка для володіння файловим дескриптором
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct UeventRecord {
    std::string_view action{"N/A"};
    std::string_view devpath{"N/A"};
    std::string_view subsystem{"N/A"};
    std::string_view devname{};
    std::string_view modalias{};
    std::string_view seqnum{"N/A"};
    std::string_view major{};
    std::string_view minor{};
    std::string_view driver{};
};

class UeventListener {
    UniqueFd socket_;
    static constexpr size_t kBufferSize = 16384;
    static constexpr int kSocketRecvBuffer = 2 * 1024 * 1024;

public:
    static std::expected<UeventListener, std::string> create() {
        int raw_fd = ::socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
        if (raw_fd < 0) {
            return std::unexpected(std::format("Не вдалося створити сокет Netlink: {}", std::strerror(errno)));
        }

        UniqueFd sock(raw_fd);

        int buf_size = kSocketRecvBuffer;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_pid = 0;
        sa.nl_groups = 1;

        if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(std::format("Помилка bind() до групи Netlink: {}", std::strerror(errno)));
        }

        return UeventListener(std::move(sock));
    }

    void run(const volatile std::sig_atomic_t& stop_flag) {
        std::println("================================================================");
        std::println(" Монітор Netlink uevent на C++23 запущено (Ctrl+C для виходу)");
        std::println(" Очікування пакетів ядра у реальному часі...");
        std::println("================================================================");

        std::array<char, kBufferSize> buffer{};
        pollfd pfd{
            .fd = socket_.get(),
            .events = POLLIN,
            .revents = 0
        };

        while (!stop_flag) {
            int ret = ::poll(&pfd, 1, 500);
            if (ret < 0) {
                if (errno == EINTR) continue;
                std::println(stderr, "Помилка poll(): {}", std::strerror(errno));
                break;
            }
            if (ret == 0) continue;

            if (pfd.revents & POLLIN) {
                ssize_t len = ::recv(socket_.get(), buffer.data(), buffer.size() - 1, MSG_DONTWAIT);
                if (len < 0) {
                    if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) continue;
                    if (errno == ENOBUFS) {
                        std::println(stderr, "УВАГА: переповнення буфера сокета ядра (ENOBUFS)!");
                        continue;
                    }
                    std::println(stderr, "Помилка читання recv(): {}", std::strerror(errno));
                    break;
                }
                if (len == 0) continue;

                buffer[len] = '\0';
                process_payload(std::string_view(buffer.data(), static_cast<size_t>(len)));
            }
        }

        std::println("\nЗавершення роботи. Дескриптор сокета закривається автоматично через RAII.");
    }

private:
    explicit UeventListener(UniqueFd sock) noexcept : socket_(std::move(sock)) {}

    void process_payload(std::string_view data) {
        UeventRecord record;
        size_t offset = 0;

        // Пропускаємо початковий рядок заголовка ("add@/devices/...")
        size_t first_null = data.find('\0');
        if (first_null != std::string_view::npos) {
            offset = first_null + 1;
        }

        while (offset < data.size()) {
            size_t next_null = data.find('\0', offset);
            size_t token_len = (next_null == std::string_view::npos) ? (data.size() - offset) : (next_null - offset);

            if (token_len == 0) break;

            std::string_view token = data.substr(offset, token_len);
            parse_token(token, record);

            if (next_null == std::string_view::npos) break;
            offset = next_null + 1;
        }

        render_record(record);
    }

    void parse_token(std::string_view token, UeventRecord& rec) {
        if (token.starts_with("ACTION=")) rec.action = token.substr(7);
        else if (token.starts_with("DEVPATH=")) rec.devpath = token.substr(8);
        else if (token.starts_with("SUBSYSTEM=")) rec.subsystem = token.substr(10);
        else if (token.starts_with("DEVNAME=")) rec.devname = token.substr(8);
        else if (token.starts_with("MODALIAS=")) rec.modalias = token.substr(9);
        else if (token.starts_with("SEQNUM=")) rec.seqnum = token.substr(7);
        else if (token.starts_with("MAJOR=")) rec.major = token.substr(6);
        else if (token.starts_with("MINOR=")) rec.minor = token.substr(6);
        else if (token.starts_with("DRIVER=")) rec.driver = token.substr(7);
    }

    void render_record(const UeventRecord& r) {
        std::println("────────────────────────────────────────────────────────────────");
        std::println("[UEVENT #{:<6}] ДІЯ: {:<8} | ПІДСИСТЕМА: {}", r.seqnum, r.action, r.subsystem);
        std::println("  Шлях у sysfs:  /sys{}", r.devpath);

        if (!r.devname.empty()) {
            if (!r.major.empty() && !r.minor.empty()) {
                std::println("  Нода у /dev:   /dev/{} (major:minor = {}:{})", r.devname, r.major, r.minor);
            } else {
                std::println("  Нода у /dev:   /dev/{}", r.devname);
            }
        }

        if (!r.driver.empty()) {
            std::println("  Драйвер ядра:  {}", r.driver);
        }

        if (!r.modalias.empty()) {
            std::println("  MODALIAS:      {}", r.modalias);
        }
    }
};

} // namespace netlink

static volatile std::sig_atomic_t g_terminate = 0;

static void on_signal(int) {
    g_terminate = 1;
}

int main() {
    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    auto listener = netlink::UeventListener::create();
    if (!listener) {
        std::println(stderr, "Критична помилка: {}", listener.error());
        return 1;
    }

    listener->run(g_terminate);
    return 0;
}
```
:::

---

## 3. Збирання, перевірка та запуск

Для компіляції скористайтеся стандартними інструментами збирання:

```bash
# Компільована версія C:
gcc -O2 -Wall -Wextra uevent_monitor.c -o uevent_monitor

# Компільована версія C++23:
g++ -std=c++23 -O2 -Wall -Wextra uevent_monitor.cpp -o uevent_monitor
```

### Вимоги до прав доступу

У старих ядрах Linux (до версії 3.10) створення сокетів родини `AF_NETLINK` із типом `SOCK_RAW` вимагало наявності привілею `CAP_NET_ADMIN` (права користувача `root`). Починаючи з версій 3.10+, відкриття сокета `NETLINK_KOBJECT_UEVENT` дозволено непривілейованим процесам для прослуховування подій власного мережевого простору імен (network namespace). Проте для отримання повного набору подій від фізичного заліза системи програму слід запускати від імені адміністратора:

```bash
sudo ./uevent_monitor
```

---

## 4. Порівняння підходів до моніторингу пристроїв

Розробник у середовищі Linux має три альтернативні рівні доступу до апаратних подій. Кожен із них має власну сферу застосування та накладні витрати:

| Характеристика | Прямий сокет Netlink (цей проект) | Бібліотека libudev / udev_monitor | Підсистема sd-device (systemd) |
| :--- | :--- | :--- | :--- |
| **Залежності** | Жодних (лише системні виклики ядра) | Потребує бібліотеки `libudev.so` | Потребує `libsystemd.so` |
| **Джерело даних** | Безпосередньо простір ядра | Сокет демона `systemd-udevd` | Сокет D-Bus / `/run/udev/data/` |
| **Швидкість реакції** | Миттєва (0–1 мс від переривання) | Після проходження конвеєра правил (5–50 мс) | Після завершення unit'ів systemd |
| **Оброблені атрибути** | Тільки сирі змінні ядра (`MODALIAS`, `DEVPATH`) | Повні властивості (`ID_FS_UUID`, `ID_VENDOR`) | Повні властивості + стан Unit'ів |
| **Сфера застосування** | Вбудовані системи (embedded), BusyBox, драйвери | Стандартні системні утиліти Linux | Глибока інтеграція зі службами systemd |

---

## 5. Покроковий розбір реального трасування подій

Розглянемо реальні логи перехоплення для двох типових сценаріїв: під'єднання USB-флешки та перетворювача USB-UART.

### 5.1. Під'єднання USB-накопичувача (Flash Drive)

Під час під'єднання флешки ядро послідовно розгортає ієрархію об'єктів від фізичного порту до логічних розділів накопичувача:

```text
================================================================
 Монітор подій Netlink uevent запущено (Ctrl+C для виходу)
 Очікування повідомлень ядра про під'єднання пристроїв...
================================================================
────────────────────────────────────────────────────────────────
[UEVENT #2041 ] ДІЯ: add      | ПІДСИСТЕМА: usb
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2
  MODALIAS:      usb:v0781p5583d0100dc00dsc00dp00ic08isc06ip50in00
────────────────────────────────────────────────────────────────
[UEVENT #2042 ] ДІЯ: add      | ПІДСИСТЕМА: usb
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0
  MODALIAS:      usb:v0781p5583d0100dc00dsc00dp00ic08isc06ip50in00
────────────────────────────────────────────────────────────────
[UEVENT #2043 ] ДІЯ: bind     | ПІДСИСТЕМА: usb
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0
  Драйвер ядра:  usb-storage
────────────────────────────────────────────────────────────────
[UEVENT #2044 ] ДІЯ: add      | ПІДСИСТЕМА: scsi
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0/host6/target6:0:0/6:0:0:0
  Драйвер ядра:  sd
────────────────────────────────────────────────────────────────
[UEVENT #2045 ] ДІЯ: add      | ПІДСИСТЕМА: block
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0/host6/target6:0:0/6:0:0:0/block/sdb
  Нода у /dev:   /dev/sdb (major:minor = 8:16)
────────────────────────────────────────────────────────────────
[UEVENT #2046 ] ДІЯ: add      | ПІДСИСТЕМА: block
  Шлях у sysfs:  /sys/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0/host6/target6:0:0/6:0:0:0/block/sdb/sdb1
  Нода у /dev:   /dev/sdb1 (major:minor = 8:17)
```

Аналіз логу показує чітку причинно-наслідкову послідовність:
1. Подія `#2041`: ядро реєструє USB-пристрій на порті `1-2`.
2. Подія `#2042`: створюється об'єкт інтерфейсу `1-2:1.0` класу `0x08` (Mass Storage).
3. Подія `#2043`: драйвер `usb-storage` прив'язується до інтерфейсу (`bind`).
4. Подія `#2044`: створюється віртуальний SCSI-диск (`sd`).
5. Події `#2045` та `#2046`: з'являються блоковий пристрій `/dev/sdb` (major 8, minor 16) та його перший розділ `/dev/sdb1` (minor 17).

---

## 6. Практичні пастки, крайові випадки та системні обмеження

### 6.1. Переповнення сокета при штормі подій (Помилка ENOBUFS)

Сокет Netlink функціонує як ненадійний дейтаграмний канал без механізму керування потоком (flow control) на рівні протоколу. Якщо в системі одночасно ініціалізується багатопортовий контролер шини або відбувається завантаження десятків драйверів одночасно, ядро заповнює чергу сокета швидше, ніж застосунок встигає викликати `recv()`.

Коли черга переповнюється, ядро скидає нові пакети й повертає наступному виклику `recv()` помилку `-ENOBUFS` (No buffer space available).

**Шляхи запобігання:**
1. Встановлення великого розміру буфера прийому через `setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size))`. За замовчуванням ліміт пам'яті обмежено параметром `/proc/sys/net/core/rmem_default` (зазвичай 212 КБ). Для високошвидкісних серверів розмір варто збільшувати до 4–8 МБ.
2. Привілейовані процеси можуть використовувати системний прапорець `SO_RCVBUFFORCE`, який дозволяє перевищувати глобальний ліміт `/proc/sys/net/core/rmem_max`.
3. При отриманні `ENOBUFS` надійний монітор зобов'язаний виконати повне повторне сканування дерева каталогів `/sys/devices/`, щоб синхронізувати свій внутрішній стан із реальним станом системи.

### 6.2. Усікання пакетів при недостатньому розмірі буфера застосунку

Більшість повідомлень uevent мають розмір від 400 до 1200 байтів. Однак деякі пристрої підсистеми введення (наприклад, багатофункціональні ігрові маніпулятори або сенсорні панелі) транслюють у повідомленні розширені бітові маски `KEY=`, `ABS=` та `REL=`. Для таких пристроїв розмір буфера `kobj_uevent_env` сягає 2048 байтів.

Якщо буфер користувацького процесу менший за розмір надісланого дейтаграмного повідомлення, виклик `recv()` відтинає хвіст пакета, втрачаючи змінні оточення в кінці. Тому буфер прийому в програмі має бути не меншим ніж 8192 чи 16384 байти.

### 6.3. Ізоляція просторів імен мережі (Network Namespaces)

У сучасних контейнеризованих середовищах (Docker, Podman, LXC) кожен контейнер має власний мережевий простір імен `netns`. За замовчуванням ядро Linux транслює широкомовні пакети `NETLINK_KOBJECT_UEVENT` лише у первинний (хостовий) мережевий простір імен `init_net`.

Процеси, запущені всередині ізольованого контейнера з власним `netns`, не отримуватимуть глобальних апаратних сповіщень ядра, якщо контейнеру явно не надано доступ до хостової мережі (`--net=host`) або не налаштовано проксифікацію подій через сокет `systemd-udevd`.
