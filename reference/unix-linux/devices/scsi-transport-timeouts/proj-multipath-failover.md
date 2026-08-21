# ⚙️ Моніторинг подій rport та симуляція обриву лінку у SAN

Коли в оптичній мережі збереження даних (SAN) виникає аварія, системний адміністратор або засіб автоматизованої оркестрації кластера повинні точно знати, як швидко ядро виявило обрив, скільки мілісекунд тривало блокування черги і коли саме `dm-multipath` перемкнув трафік на резервний маршрут. Ця вставка містить утиліту для моніторингу низькорівневих подій транспорту SCSI через Netlink-сокет ядра, а також практичну методику тестування відмовостійкості без фізичного висмикування оптичних патчкордів.

## Завдання та архітектурна ідея

Підсистема `udev` отримує сповіщення про зміну стану апаратних компонентів від ядра через широкомовний сокет `NETLINK_KOBJECT_UEVENT`. Кожен виклик `fc_remote_port_delete()`, перехід порту у стан `Blocked`, спрацювання таймера `fast_io_fail_tmo` або остаточне вилучення пристрою після вичерпання `dev_loss_tmo` генерує подію ядра у підсистемі `fc_remote_ports`, `iscsi_session` або `sas_rphy`.

Пряме читання сокета Netlink у просторі користувача дозволяє зафіксувати точні часові мітки переходів стану з мікросекундною роздільною здатністю без накладних витрат на періодичне опитування (polling) файлів у `/sys/class/`. Коли ядро фіксує зміну фізичного лінку, воно формує структуру uevent, де перелічує дію (`ACTION=change` або `ACTION=remove`), шлях у дереві пристроїв (`DEVPATH=/devices/pci.../rport-0:0-1`) та підсистему (`SUBSYSTEM=fc_remote_ports`).

Отримавши подію `change`, утиліта негайно зчитує поточний стан порту з псевдофайлу `port_state`, а також актуальні значення `fast_io_fail_tmo` та `dev_loss_tmo`. Це дозволяє в режимі реального часу спостерігати тривалість фази блокування (queue holding) та момент переходу підсистеми у фазу швидкого відхилення команд (fast failover).

## Програма моніторингу подій транспорту

Програма відкриває сирий сокет сімейства `AF_NETLINK` із протоколом `NETLINK_KOBJECT_UEVENT`, прив'язує його до широкомовної групи розсилки ядра (номер групи `1`) та входить у цикл очікування надходження дейтаграм. Повідомлення uevent складається з послідовності рядків змінних середовища `KEY=VALUE`, розділених нульовими байтами (`\0`).

Розбираючи буфер, програма виділяє ключові поля `SUBSYSTEM`, `ACTION` та `DEVPATH`. Якщо зафіксовано подію, пов'язану з Fibre Channel або iSCSI, утиліта звертається до відповідного каталогу в `sysfs`, зчитує діагностичні атрибути та виводить структурований звіт із міткою часу.

:::tabs
```c
/* rport_monitor.c — відстеження подій SCSI транспорту через Netlink uevent.
 * Складання: gcc -O2 -Wall -Wextra rport_monitor.c -o rport_monitor
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 4096

static void log_timestamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    struct tm tm_info;
    localtime_r(&ts.tv_sec, &tm_info);
    char buf[64];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm_info);
    printf("[%s.%03ld] ", buf, ts.tv_nsec / 1000000L);
}

static void read_sysfs_attr(const char *devpath, const char *attr, char *out, size_t out_len) {
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "/sys%s/%s", devpath, attr);
    int fd = open(full_path, O_RDONLY);
    if (fd < 0) {
        snprintf(out, out_len, "<недоступно>");
        return;
    }
    ssize_t n = read(fd, out, out_len - 1);
    close(fd);
    if (n > 0) {
        if (out[n - 1] == '\n') {
            out[n - 1] = '\0';
        } else {
            out[n] = '\0';
        }
    } else {
        snprintf(out, out_len, "<порожньо>");
    }
}

int main(void) {
    int sock_fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_KOBJECT_UEVENT);
    if (sock_fd < 0) {
        perror("Помилка створення сокета Netlink");
        return 1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = 1; /* Отримувати широкомовні uevents */

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки сокета (bind)");
        close(sock_fd);
        return 1;
    }

    printf("=== Запущено моніторинг подій SCSI транспорту (fc_remote_ports / iscsi_session) ===\n");
    printf("Очікування подій ядра... Для виходу натисніть Ctrl+C\n\n");

    char buffer[UEVENT_BUFFER_SIZE];

    while (1) {
        ssize_t len = recv(sock_fd, buffer, sizeof(buffer) - 1, 0);
        if (len <= 0) {
            continue;
        }
        buffer[len] = '\0';

        char *action = NULL;
        char *devpath = NULL;
        char *subsystem = NULL;

        /* Повідомлення uevent складається з рядків, розділених нульовими байтами */
        char *ptr = buffer;
        while (ptr < buffer + len) {
            if (strncmp(ptr, "ACTION=", 7) == 0) {
                action = ptr + 7;
            } else if (strncmp(ptr, "DEVPATH=", 8) == 0) {
                devpath = ptr + 8;
            } else if (strncmp(ptr, "SUBSYSTEM=", 10) == 0) {
                subsystem = ptr + 10;
            }
            ptr += strlen(ptr) + 1;
        }

        if (subsystem && (strcmp(subsystem, "fc_remote_ports") == 0 ||
                          strcmp(subsystem, "iscsi_session") == 0)) {
            log_timestamp();
            printf("ПОДІЯ: дія=%s | підсистема=%s | шлях=%s\n",
                   action ? action : "?", subsystem, devpath ? devpath : "?");

            if (devpath && strcmp(subsystem, "fc_remote_ports") == 0) {
                char state[64], fast_io[32], dev_loss[32], port_name[64];
                read_sysfs_attr(devpath, "port_state", state, sizeof(state));
                read_sysfs_attr(devpath, "fast_io_fail_tmo", fast_io, sizeof(fast_io));
                read_sysfs_attr(devpath, "dev_loss_tmo", dev_loss, sizeof(dev_loss));
                read_sysfs_attr(devpath, "port_name", port_name, sizeof(port_name));

                printf("       └─ WWPN: %s | Стан: %s | fast_io_fail_tmo: %s с | dev_loss_tmo: %s с\n",
                       port_name, state, fast_io, dev_loss);
            } else if (devpath && strcmp(subsystem, "iscsi_session") == 0) {
                char state[64], recovery[32], target[128];
                read_sysfs_attr(devpath, "state", state, sizeof(state));
                read_sysfs_attr(devpath, "recovery_tmo", recovery, sizeof(recovery));
                read_sysfs_attr(devpath, "targetname", target, sizeof(target));

                printf("       └─ Target: %s | Стан: %s | recovery_tmo: %s с\n",
                       target, state, recovery);
            }
            fflush(stdout);
        }
    }

    close(sock_fd);
    return 0;
}
```
```cpp
// rport_monitor.cpp — ідіоматичний моніторинг подій транспорту SCSI на C++20.
// Складання: g++ -std=c++20 -O2 -Wall -Wextra rport_monitor.cpp -o rport_monitor
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <span>
#include <chrono>
#include <format>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

namespace fs = std::filesystem;

class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_NETLINK) failed");
        }

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_groups = 1; // Broadcast uevents

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "bind(netlink) failed");
        }
    }

    ~NetlinkSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] ssize_t receive(std::span<char> buffer) const {
        return ::recv(fd_, buffer.data(), buffer.size(), 0);
    }

private:
    int fd_{-1};
};

static std::string read_sysfs(const fs::path& devpath, std::string_view attr) {
    fs::path full_path = fs::path("/sys") / devpath.relative_path() / attr;
    std::ifstream file(full_path);
    if (!file.is_open()) {
        return "<недоступно>";
    }
    std::string val;
    std::getline(file, val);
    return val.empty() ? "<порожньо>" : val;
}

int main() {
    try {
        NetlinkSocket socket(NETLINK_KOBJECT_UEVENT);
        std::cout << "=== Запущено моніторинг подій SCSI транспорту (C++20) ===\n";
        std::cout << "Очікування uevent... Для виходу натисніть Ctrl+C\n\n";

        std::array<char, 4096> buffer{};

        while (true) {
            ssize_t len = socket.receive(buffer);
            if (len <= 0) continue;

            std::string_view action{};
            std::string_view devpath{};
            std::string_view subsystem{};

            size_t offset = 0;
            while (offset < static_cast<size_t>(len)) {
                std::string_view entry(buffer.data() + offset);
                if (entry.starts_with("ACTION=")) {
                    action = entry.substr(7);
                } else if (entry.starts_with("DEVPATH=")) {
                    devpath = entry.substr(8);
                } else if (entry.starts_with("SUBSYSTEM=")) {
                    subsystem = entry.substr(10);
                }
                offset += entry.size() + 1;
            }

            if (subsystem == "fc_remote_ports" || subsystem == "iscsi_session") {
                const auto now = std::chrono::system_clock::now();
                std::cout << std::format("[{:%Y-%m-%d %H:%M:%S}] ПОДІЯ: дія={} | підсистема={} | шлях={}\n",
                                         now, action, subsystem, devpath);

                if (subsystem == "fc_remote_ports" && !devpath.empty()) {
                    fs::path p(devpath);
                    auto state = read_sysfs(p, "port_state");
                    auto fast_io = read_sysfs(p, "fast_io_fail_tmo");
                    auto dev_loss = read_sysfs(p, "dev_loss_tmo");
                    auto port_name = read_sysfs(p, "port_name");

                    std::cout << std::format("       └─ WWPN: {} | Стан: {} | fast_io_fail_tmo: {} с | dev_loss_tmo: {} с\n",
                                             port_name, state, fast_io, dev_loss);
                } else if (subsystem == "iscsi_session" && !devpath.empty()) {
                    fs::path p(devpath);
                    auto state = read_sysfs(p, "state");
                    auto recovery = read_sysfs(p, "recovery_tmo");
                    auto target = read_sysfs(p, "targetname");

                    std::cout << std::format("       └─ Target: {} | Стан: {} | recovery_tmo: {} с\n",
                                             target, state, recovery);
                }
                std::cout << std::flush;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Методика синтетичного тестування відмовостійкості

Для перевірки коректності поведінки підсистеми `dm-multipath` в умовах аварії каналу зв'язку застосовують методику програмної імітації збою без ризику апаратного пошкодження обладнання чи оптоволоконних конекторів.

Під час тестування одночасно відстежуються три процеси: активне дискове навантаження користувацького рівня, генерація uevent-подій у Netlink-сокеті та системні трасування ядра за допомогою ftrace або tracepoints підсистеми SCSI (`scsi:scsi_dispatch_cmd_timeout` та `scsi:scsi_eh_action`).

**Крок 1. Запуск тестового фонового навантаження.**
У фоновому режимі запускається утиліта генерації блокового навантаження `fio`, налаштована на прямий асинхронний запис у віртуальний пристрій `/dev/mapper/mpatha` з фіксацією затримок:

```bash
fio --name=failover_test --filename=/dev/mapper/mpatha --direct=1 \
    --rw=randwrite --bs=4k --ioengine=libaio --iodepth=32 \
    --time_based --runtime=120 --rate_iops=2000 \
    --write_lat_log=fio_lat --log_avg_msec=100 &
```

**Крок 2. Імітація обриву лінку Fibre Channel.**
Для імітації втрати оптичного сигналу на першому контролері HBA у псевдофайл скидання стану записується спеціальний примітив ініціалізації кільця (LIP — Loop Initialization Primitive) або ініціюється вимкнення порту на рівні комутатора SAN через командний інтерфейс:

```bash
# Примусове надсилання примітиву LIP на адаптер host0
echo 1 > /sys/class/fc_host/host0/issue_lip

# Альтернативно: блокування віддаленого порту через sysfs для тестування
echo "Blocked" > /sys/class/fc_remote_ports/rport-0:0-1/port_state 2>/dev/null || true
```

**Крок 3. Фіксація фаз перемикання та аналіз результатів.**
Утиліта `rport_monitor` фіксує перехід у стан `Blocked` о `t = 0.000 с`. Протягом перших 5 секунд (значення `fast_io_fail_tmo`) запити `fio` накопичуються в черзі блокового рівня ядра. На 5-й секунді порт переходить у режим швидкої відмови, `dm-multipath` отримує статус `DID_TRANSPORT_FAILFAST`, маркує шлях `/dev/sda` як `faulty` і негайно спрямовує всі накопичені операції у шлях `/dev/sdb`.

На графіку латентності `fio` спостерігається єдиний сплеск затримки тривалістю рівно 5.05 секунди, після чого обробка операцій продовжується зі штатною швидкістю без жодної помилки `EIO` у просторі користувача. Якщо ж відновити порт командою `echo 1 > /sys/class/fc_host/host0/issue_lip`, демон `multipathd` через перевірку `path_checker tur` поверне шлях у статус `active` і виконає балансування навантаження.

## Простеження обробки помилок через ядра tracepoints

Для глибшого аналізу поведінки черг ядра під час аварії лінку корисно підключити вбудований механізм tracepoints підсистеми `scsi`. Ядро Linux надає набір готових точок трасування в каталозі `/sys/kernel/debug/tracing/events/scsi/`:

```bash
# Увімкнення трасування подій таймера та відновлення після збоїв
echo 1 > /sys/kernel/debug/tracing/events/scsi/scsi_dispatch_cmd_timeout/enable
echo 1 > /sys/kernel/debug/tracing/events/scsi/scsi_eh_action/enable

# Перегляд журналу трасування в реальному часі
cat /sys/kernel/debug/tracing/trace_pipe
```

У журналі трасування з'являються записи із зазначенням номера команди CDB, ідентифікатора LUN та часу спрацювання таймера, що дозволяє переконатися у відсутності зайвих викликів `scsi_eh_action` при коректно налаштованому таймері `fast_io_fail_tmo`.

## Типові пастки конфігурації

1. **Значення `fast_io_fail_tmo` перевищує `dev_loss_tmo`.**
   Якщо адміністратор налаштує `fast_io_fail_tmo 60` та `dev_loss_tmo 30`, ядро відхилить таку конфігурацію помилкою `-EINVAL`. Якщо ж значення встановлюються скриптом без перевірки результату, таймер швидкої відмови не зміниться і залишиться у значенні за замовчуванням (`off`), що призведе до неможливості швидкого перемикання шляхів під час збою.

2. **Вимкнення `fast_io_fail_tmo` у кластерному середовищі.**
   Якщо параметр `fast_io_fail_tmo` встановлено в `off`, заблокований порт утримуватиме I/O запити протягом усього періоду `dev_loss_tmo` (наприклад, 120 секунд). Для кластерних файлових систем (GFS2, OCFS2) та розподілених баз даних така затримка призводить до спрацювання сторожових таймерів кластера (fencing/stonith) та аварійного перезавантаження працездатного вузла.

3. **Нескінченна черга `no_path_retry queue` при тривалій аварії сховища.**
   Якщо відмовили обидва контролери дискового масиву, опція `queue` змушує `dm-multipath` нескінченно утримувати всі запити в оперативній пам'яті. Це запобігає появі помилок у застосунках під час короткочасних робіт, але при тривалій аварії призводить до вичерпання пулу сторінок ядра та зависання системних процесів у стані очікування пам'яті (`D state`). Для критичних систем рекомендується обмежувати кількість повторів параметром `no_path_retry 12` (при інтервалі перевірки 5 с це дає 60 секунд очікування перед контрольованим поверненням помилки).
