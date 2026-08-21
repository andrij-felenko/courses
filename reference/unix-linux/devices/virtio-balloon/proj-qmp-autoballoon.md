# ⚙️ Демон автобалонінгу: динамічне керування пам'яттю через QMP

Статичне виділення оперативної пам'яті віртуальним машинам призводить до неефективного використання серверів: одні гостьові системи простоюють із гігабайтами вільної пам'яті, тоді як інші страждають від браку ресурсів. Задача полягає у створенні демона автобалонінгу (англ. *auto-ballooning daemon*), який зчитує телеметрію гостьової пам'яті через протокол QMP (QEMU Monitor Protocol) і динамічно підганяє розмір виділеної пам'яті без ризику викликати аварійне вимкнення процесів (OOM Killer).

```
   +─────────────────────────────────────────────────────────────+
   |                  ДЕМОН АВТОБАЛОНІНГУ (ХОСТ)                 |
   |  1. Підключення до UNIX-сокета QMP (/var/run/qemu-vm.qmp)    |
   |  2. Увімкнення опитування: guest-stats-polling-interval = 2  |
   |  3. Читання метрик: stat-available-memory, stat-total-memory |
   |  4. Обчислення цільового RAM: Target = Used + Safety_Margin  |
   |  5. Відправка команди QMP {"execute": "balloon", ...}        |
   +─────────────────────────────────────────────────────────────+
                                  │
                          (QMP JSON сокет)
                                  ▼
   +─────────────────────────────────────────────────────────────+
   |                        ПРОЦЕС QEMU                          |
   |  Перетворює запит у зміну num_pages для virtio-balloon      |
   +─────────────────────────────────────────────────────────────+
```

## Принцип функціонування зворотного зв'язку

Керування пам'яттю віртуальної машини є класичною задачею теорії автоматичного керування зі зворотним зв'язком (англ. *closed-loop feedback control*). Головна мета алгоритму — підтримувати оптимальну частку вільної пам'яті всередині гостьової ОС, забираючи надлишки на користь фізичного хоста або інших віртуальних машин.

Якщо демон забирає забагато пам'яті, гостьове ядро змушене скидати корисний дисковий кеш і починати витіснення сторінок у віртуальний своп. Сигналом такого перевантаження є різке зростання лічильника `stat-major-faults` (важких сторінкових помилок, що потребують читання з диска). Якщо демон забирає замало пам'яті, хост втрачає переваги перекомітування (overcommit).

### Алгоритм розрахунку з подушкою безпеки та захистом від гойдалок

Щоб уникнути виснаження пам'яті всередині гостя, демон підтримує цільову «подушку безпеки» (англ. *headroom*). Якщо гостьова ОС використовує 4 ГБ з 8 ГБ, а цільовий запас вільної пам'яті встановлено на рівні 20% від загального обсягу, новий цільовий розмір пам'яті віртуальної машини обчислюється за формулою:

```
Зайнята пам'ять гостя = Total_Memory - Available_Memory
Цільова подушка безпеки = Total_Memory · 0.20
Новий розмір ВМ (Target) = Зайнята пам'ять + Цільова подушка безпеки
```

Для згладжування короткочасних сплесків споживання пам'яті демон використовує експоненційне зважене ковзне середнє (англ. *Exponential Weighted Moving Average, EWMA*):

```
Згладжене_значення = α · Поточне_значення + (1 - α) · Попереднє_значення
```

Де коефіцієнт згладжування `α = 0.3` дозволяє реагувати на тривалі тренди, ігноруючи секундні коливання активності процесів.

Для запобігання явищу гойдалок пам'яті (англ. *memory thrashing*), коли розмір балона змінюється щосекунди від найменшого коливання кешу, алгоритм застосовує смугу нечутливості — гістерезис (англ. *hysteresis*). Зміна розміру балона ініціюється лише тоді, коли різниця між поточним значенням і новим розрахунковим значенням `Target` перевищує встановлений поріг (наприклад, 256 МіБ):

```
|Target - Current_Actual| >= HYSTERESIS_THRESHOLD (256 МіБ)
```

Крім того, демон накладає жорсткі межі безпеки: обсяг виділеної пам'яті ніколи не опускається нижче гарантованого мінімуму `MIN_RAM` (наприклад, 2 ГБ) і ніколи не перевищує фізичний максимум віртуальної машини `Total_Memory`.

## Протокол QMP та взаємодія через UNIX-сокети

Протокол QEMU Monitor Protocol (QMP) працює поверх потокових UNIX domain сокетів або TCP-з'єднань і використовує формат повідомлень JSON-RPC. Робота клієнта складається з чотирьох послідовних етапів:

1. **Рукостискання (Handshake):** Одразу після встановлення TCP/UNIX з'єднання QEMU надсилає вітальне повідомлення з переліком підтримуваних версій протоколу. Клієнт зобов'язаний відповісти командою узгодження `qmp_capabilities`. Доки ця команда не виконана, QEMU відхиляє будь-які інші керуючі запити.
2. **Активація таймера статистики:** За замовчуванням гіпервізор не опитує гостьовий драйвер балонінгу, щоб не витрачати ресурси vCPU. Клієнт викликає команду `qom-set` над об'єктом `/machine/peripheral/balloon0`, встановлюючи властивість `guest-stats-polling-interval` у значення 2 секунди.
3. **Регулярне опитування та реакція:** Клієнт періодично надсилає команду `qom-get` для читання структури `guest-stats`, парсить отримані поля та за потреби надсилає команду `balloon` із новим числовим значенням у байтах.
4. **Обробка розривів та перезапусків:** При перезавантаженні гостя або міграції сокет закривається. Клієнт реалізує кінцевий автомат із повторним підключенням через інтервали експоненційного очікування (exponential backoff).

## Реалізація клієнта QMP

Нижче наведено робочий приклад демона трьома мовами: C (системний рівень POSIX-сокетів), C++ (ідіоматична об'єктна модель RAII з обробкою помилок) та Python (асинхронний цикл обробки подій).

:::tabs
```c
/* qmp_autoballoon.c — демон автобалонінгу мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdint.h>

#define BUFFER_SIZE 4096
#define MIN_RAM_BYTES (2ULL * 1024 * 1024 * 1024) /* Мінімум 2 ГБ */
#define SAFETY_MARGIN_PERCENT 20

static int qmp_send_command(int fd, const char *cmd, char *response, size_t resp_len) {
    if (write(fd, cmd, strlen(cmd)) < 0) {
        perror("write to qmp socket failed");
        return -1;
    }
    ssize_t n = read(fd, response, resp_len - 1);
    if (n < 0) {
        perror("read from qmp socket failed");
        return -1;
    }
    response[n] = '\0';
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_qmp_сокета>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *socket_path = argv[1];
    int sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket creation failed");
        return EXIT_FAILURE;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    if (connect(sock_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect to qmp failed");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    char buf[BUFFER_SIZE];
    /* Читаємо вітальне повідомлення QMP */
    read(sock_fd, buf, sizeof(buf) - 1);

    /* 1. Узгодження можливостей QMP */
    const char *qmp_cap = "{\"execute\": \"qmp_capabilities\"}\n";
    if (qmp_send_command(sock_fd, qmp_cap, buf, sizeof(buf)) < 0) {
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* 2. Встановлюємо інтервал опитування statsq на 2 секунди */
    const char *set_poll = "{\"execute\": \"qom-set\", \"arguments\": "
                           "{\"path\": \"/machine/peripheral/balloon0\", "
                           "\"property\": \"guest-stats-polling-interval\", \"value\": 2}}\n";
    qmp_send_command(sock_fd, set_poll, buf, sizeof(buf));

    printf("[autoballoon] Демон успішно підключився до %s\n", socket_path);

    /* 3. Головний цикл моніторингу */
    while (1) {
        sleep(3);

        const char *get_stats = "{\"execute\": \"qom-get\", \"arguments\": "
                                "\"property\": \"guest-stats\", "
                                "\"path\": \"/machine/peripheral/balloon0\"}}\n";
        if (qmp_send_command(sock_fd, get_stats, buf, sizeof(buf)) < 0)
            break;

        /* Спрощений пошук числових полів у відповіді JSON */
        char *p_total = strstr(buf, "\"stat-total-memory\":");
        char *p_avail = strstr(buf, "\"stat-available-memory\":");

        if (p_total && p_avail) {
            uint64_t total_mem = strtoull(p_total + 20, NULL, 10);
            uint64_t avail_mem = strtoull(p_avail + 24, NULL, 10);

            if (total_mem > 0 && avail_mem > 0) {
                uint64_t used_mem = total_mem - avail_mem;
                uint64_t safety = (total_mem * SAFETY_MARGIN_PERCENT) / 100;
                uint64_t target_mem = used_mem + safety;

                if (target_mem < MIN_RAM_BYTES)
                    target_mem = MIN_RAM_BYTES;
                if (target_mem > total_mem)
                    target_mem = total_mem;

                printf("[autoballoon] Total: %lu МБ, Avail: %lu МБ -> Target: %lu МБ\n",
                       total_mem / (1024 * 1024), avail_mem / (1024 * 1024),
                       target_mem / (1024 * 1024));

                char cmd[256];
                snprintf(cmd, sizeof(cmd),
                         "{\"execute\": \"balloon\", \"arguments\": {\"value\": %lu}}\n",
                         target_mem);
                qmp_send_command(sock_fd, cmd, buf, sizeof(buf));
            }
        }
    }

    close(sock_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// qmp_autoballoon.cpp — ідіоматична реалізація на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <expected>
#include <system_error>
#include <algorithm>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

class QmpConnection {
    int fd_{-1};

public:
    explicit QmpConnection(int fd) noexcept : fd_(fd) {}
    ~QmpConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    QmpConnection(const QmpConnection &) = delete;
    QmpConnection &operator=(const QmpConnection &) = delete;

    QmpConnection(QmpConnection &&other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    QmpConnection &operator=(QmpConnection &&other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    static std::expected<QmpConnection, std::error_code> connect(std::string_view socket_path) {
        int sock = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (sock < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        if (socket_path.size() >= sizeof(addr.sun_path)) {
            ::close(sock);
            return std::unexpected(std::make_error_code(std::errc::filename_too_long));
        }
        std::copy(socket_path.begin(), socket_path.end(), addr.sun_path);

        if (::connect(sock, reinterpret_cast<sockaddr *>(&addr), sizeof(addr)) < 0) {
            int err = errno;
            ::close(sock);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return QmpConnection(sock);
    }

    std::expected<std::string, std::error_code> execute(std::string_view command) {
        if (::write(fd_, command.data(), command.size()) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<char> buffer(4096);
        ssize_t bytes_read = ::read(fd_, buffer.data(), buffer.size() - 1);
        if (bytes_read < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return std::string(buffer.data(), static_cast<size_t>(bytes_read));
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_qmp_сокета>\n";
        return 1;
    }

    auto conn_res = QmpConnection::connect(argv[1]);
    if (!conn_res) {
        std::cerr << "Помилка підключення: " << conn_res.error().message() << '\n';
        return 1;
    }
    auto conn = std::move(*conn_res);

    // Ініціалізація сесії QMP
    std::vector<char> greeting_buf(2048);
    auto _ = conn.execute("{\"execute\": \"qmp_capabilities\"}\n");

    // Встановлення інтервалу збору статистики в 2 секунди
    conn.execute("{\"execute\": \"qom-set\", \"arguments\": "
                 "{\"path\": \"/machine/peripheral/balloon0\", "
                 "\"property\": \"guest-stats-polling-interval\", \"value\": 2}}\n");

    std::cout << "[autoballoon] Керування пам'яттю запущено.\n";

    constexpr uint64_t min_ram = 2ULL * 1024 * 1024 * 1024; // 2 ГБ
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(3));

        auto stats_res = conn.execute("{\"execute\": \"qom-get\", \"arguments\": "
                                     "{\"path\": \"/machine/peripheral/balloon0\", "
                                     "\"property\": \"guest-stats\"}}\n");
        if (!stats_res) break;

        const std::string &raw = *stats_res;
        auto pos_tot = raw.find("\"stat-total-memory\":");
        auto pos_avail = raw.find("\"stat-available-memory\":");

        if (pos_tot != std::string::npos && pos_avail != std::string::npos) {
            uint64_t total = std::stoull(raw.substr(pos_tot + 20));
            uint64_t avail = std::stoull(raw.substr(pos_avail + 24));

            if (total > 0 && avail > 0) {
                uint64_t used = total - avail;
                uint64_t safety = total * 20 / 100;
                uint64_t target = std::clamp(used + safety, min_ram, total);

                std::cout << "[autoballoon] Total: " << (total >> 20)
                          << " MB, Avail: " << (avail >> 20)
                          << " MB -> New target: " << (target >> 20) << " MB\n";

                std::string cmd = "{\"execute\": \"balloon\", \"arguments\": {\"value\": " +
                                  std::to_string(target) + "}}\n";
                conn.execute(cmd);
            }
        }
    }
    return 0;
}
```
```py
# autoballoon.py — асинхронний демон автобалонінгу мовою Python
import asyncio
import json
import sys

MIN_RAM_BYTES = 2 * 1024 * 1024 * 1024  # 2 ГБ мінімум
SAFETY_MARGIN_PCT = 0.20                # 20% вільної пам'яті


async def run_autoballoon(socket_path: str):
    reader, writer = await asyncio.open_unix_connection(socket_path)

    # Зчитуємо початкове привітання QMP
    await reader.readline()

    # 1. Узгодження QMP
    writer.write(json.dumps({"execute": "qmp_capabilities"}).encode() + b"\n")
    await writer.drain()
    await reader.readline()

    # 2. Встановлюємо інтервал опитування телеметрії statsq
    poll_cmd = {
        "execute": "qom-set",
        "arguments": {
            "path": "/machine/peripheral/balloon0",
            "property": "guest-stats-polling-interval",
            "value": 2
        }
    }
    writer.write(json.dumps(poll_cmd).encode() + b"\n")
    await writer.drain()
    await reader.readline()

    print(f"[autoballoon] Моніторинг активний для {socket_path}")

    while True:
        await asyncio.sleep(3)

        # Опитування статистики
        get_cmd = {
            "execute": "qom-get",
            "arguments": {
                "path": "/machine/peripheral/balloon0",
                "property": "guest-stats"
            }
        }
        writer.write(json.dumps(get_cmd).encode() + b"\n")
        await writer.drain()

        line = await reader.readline()
        if not line:
            break

        data = json.loads(line.decode())
        stats = data.get("return", {}).get("stats", {})

        total_mem = stats.get("stat-total-memory", 0)
        avail_mem = stats.get("stat-available-memory", 0)

        if total_mem > 0 and avail_mem > 0:
            used_mem = total_mem - avail_mem
            safety = int(total_mem * SAFETY_MARGIN_PCT)
            target_mem = max(MIN_RAM_BYTES, min(total_mem, used_mem + safety))

            print(f"[autoballoon] Total: {total_mem // (1024**2)} MB, "
                  f"Available: {avail_mem // (1024**2)} MB -> "
                  f"Target: {target_mem // (1024**2)} MB")

            balloon_cmd = {
                "execute": "balloon",
                "arguments": {"value": target_mem}
            }
            writer.write(json.dumps(balloon_cmd).encode() + b"\n")
            await writer.drain()
            await reader.readline()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Використання: {sys.argv[0]} <шлях_до_qmp_сокета>")
        sys.exit(1)

    asyncio.run(run_autoballoon(sys.argv[1]))
```
:::

## Інтеграція із systemd у промислових середовищах

Для розгортання демона як системної служби створюється юніт-файл `/etc/systemd/system/autoballoon@.service`:

```ini
[Unit]
Description=QMP Dynamic Memory Ballooning Daemon for %i
After=libvirtd.service qemu.service
Requires=libvirtd.service

[Service]
Type=simple
ExecStart=/usr/local/bin/qmp_autoballoon /var/run/qemu/%i.qmp
Restart=always
RestartSec=5s

# Обмеження безпеки хоста
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Запуск демона для конкретної віртуальної машини `vm-database`:
```bash
systemctl daemon-reload
systemctl enable --now autoballoon@vm-database.service
```

## Підводні камені та надійність промислової експлуатації

При розгортанні демонів автобалонінгу на реальних кластерах слід враховувати такі специфічні крайові випадки:

1. **Розрив з'єднання при міграції чи перезавантаженні:** Якщо віртуальна машина мігрує на інший хост або перезапускається, сокет QMP закривається з боку гіпервізора. Демон повинен перехоплювати помилки `ECONNRESET` / `EPIPE` і переходити в режим періодичних спроб повторного підключення (exponential backoff).
2. **Асинхронні події QMP (Events):** QEMU періодично надсилає в сокет спонтанні повідомлення (наприклад, `BALLOON_CHANGE`, `DEVICE_DELETED`). Простий парсер відповідей повинен фільтрувати об'єкти з ключем `"event"` і не плутати їх із результатами викликів `"return"`.
3. **Облік свопінгу гостя (`stat-swap-in` / `stat-swap-out`):** Якщо гостьова система починає активно витісняти сторінки у своп (зростання `stat-swap-in`), демон зобов'язаний негайно припинити надування балона або навіть екстрено здути його на 1–2 ГБ, надавши гостю запас фізичної пам'яті для стабілізації затримок вводу-виводу.
4. **Конфлікт із виділенням HugePages у гості:** Якщо всередині віртуальної машини запускається СУБД (PostgreSQL / Oracle), налаштована на виділення `vm.nr_hugepages`, балон не зможе захопити сторінки пам'яті, якщо вони вже заблоковані пулом HugeTLB. Демон повинен відстежувати лічильник `stat-htlb-fail` і не намагатися надувати балон понад доступний залишок звичайної пам'яті.
