# ⚙️ Демон нагляду за процесами та сторож зв'язку з автопілотом

Бортовий комп'ютер під керуванням ОС Linux виконує високорівневі обчислювальні завдання автономного польоту: обробку зображень з камер глибини, візуальну одометрію (VIO), побудову карти висот, виявлення перешкод нейромережами та планування локальної траєкторії в середовищі ROS 2. На відміну від польотного контролера (FCU), де прошивка працює під керуванням операційної системи реального часу (RTOS) з детермінованим часом відгуку, програмний стек Linux у просторі користувача піддається численним непередбачуваним збоям.

Процеси в Linux можуть аварійно завершуватися через помилки сегментації пам'яті (`SIGSEGV`), примусово знищуватися ядром при вичерпанні оперативної пам'яті (OOM Killer) або зависати у нескінченних циклах та взаємних блокуваннях (*deadlock*) при роботі з потоками. Стандартні системні засоби ініціалізації (наприклад, `systemd`) здатні перезапустити процес лише тоді, коли він повністю завершився і повернув код помилки. Проте якщо потік нейромережевого інференсу завис у блокуючому драйвері камери або черзі повідомлень, процес залишається формально активним (`state: R` або `state: D`), але генерація навігаційних уставок повністю припиняється.

Щоб польотний контролер міг своєчасно зафіксувати відмову верхнього рівня, на бортовому комп'ютері розгортається ізольований **демон нагляду** (*companion watchdog daemon*). Він функціонує як незалежний посередник між інтелектуальним ПЗ, каналом телеметрії MAVLink та апаратною лінією фізичного сторожа.

## Архітектура та принцип роботи наглядача

Демон нагляду працює як автономна служба з підвищеним пріоритетом реального часу і виконує три взаємопов'язані задачі моніторингу:

1. **Міжпроцесна перевірка працездатності (Internal Health IPC):**
   Усі критичні воркер-процеси (вузли ROS 2, планувальник траєкторій, демон зв'язку MAVSDK) зобов'язані періодично надсилати сигнал підтвердження активності («пінг здоров'я») через локальний UNIX-сокет дейтаграм (`/tmp/companion_health.sock`). Кожен воркер надсилає сигнал лише тоді, коли його внутрішній контур успішно завершив повну ітерацію обробки даних (наприклад, отримано новий кадр, оновлено карту та розраховано вектор швидкості). Якщо будь-який із критичних потоків не надіслав сигнал упродовж встановленого інтервалу (наприклад, 2 секунди), демон фіксує зависання підсистеми.

2. **Трансляція MAVLink-статусу у польотний контролер:**
   Демон безпосередньо відкриває порт UART (`TELEM2`) і щосекунди надсилає кадр `HEARTBEAT` (Message ID: 0). Якщо всі внутрішні модулі функціонують штатно, у полі стану передається прапорець `MAV_STATE_ACTIVE`. Якщо ж зафіксовано збій воркера, демон негайно змінює прапорець на `MAV_STATE_CRITICAL` або припиняє передачу кадрів, що змушує польотний контролер скинути режим Offboard та активувати зависання на місці.

3. **Генерація апаратного стробу (GPIO Watchdog Strobe):**
   Демон здійснює періодичне перемикання фізичного виводу GPIO (генерація меандру з частотою 5 Гц) через інтерфейс ядра `libgpiod`. Цей сигнал подається на вхід апаратного таймера польотного контролера або спеціалізованої мікросхеми сторожа (наприклад, `TPL5010` чи `MAX6369`). Якщо демон зависає разом із ядром ОС або фіксує аварію робочого процесу, стробування вимикається (рівень фіксується в логічному `0`). Після закінчення таймауту 1.5 секунди апаратна схема скидає живлення комп'ютера.

```
+-------------------------------------------------------------+
| Бортовий комп'ютер (Linux Single Board Computer)            |
|                                                             |
|  +------------------+         UNIX Socket Datagram          |
|  | ROS 2 / MAVSDK   | ----------------------------------+   |
|  | Робочий процес   |  "ALIVE" кожні 50-100 мс          |   |
|  +------------------+                                   |   |
|                                                         v   |
|  +-------------------------------------------------------+  |
|  | Демон нагляду (Watchdog Daemon, SCHED_FIFO)           |  |
|  +-------------------------------------------------------+  |
|         |                                      |            |
|         | MAVLink HEARTBEAT (1 Гц)             | GPIO Strobe|
|         v UART (/dev/ttyAMA0)                  v (5 Гц)     |
+---------|--------------------------------------|------------+
          |                                      |
          v                                      v
+-------------------------------------------------------------+
| Польотний контролер (FCU STM32 RTOS)                        |
|  • Парсер телеметрії MAVLink (Failsafe FSM)                 |
|  • Таймер захоплення імпульсів GPIO (Pulse Capture)         |
|  • Керування ключем живлення SBC_PWR_EN (P-MOSFET)          |
+-------------------------------------------------------------+
```

## Програмна реалізація демона

Нижче наведено повні та готові до компіляції реалізації демона моніторингу мовами C (POSIX) та ідіоматичною C++23.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <time.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <gpiod.h>

#define SOCKET_PATH      "/tmp/companion_health.sock"
#define SERIAL_PORT      "/dev/ttyAMA0"
#define BAUDRATE         B921600
#define GPIO_CHIP_NAME   "gpiochip0"
#define WATCHDOG_PIN     17

#define HEARTBEAT_PERIOD_MS   1000
#define STROBE_PERIOD_MS      100
#define PROCESS_TIMEOUT_SEC   2

/* Структура корисного навантаження MAVLink v2 HEARTBEAT (Message ID 0) */
#pragma pack(push, 1)
typedef struct {
    uint32_t custom_mode;
    uint8_t  type;           /* MAV_TYPE_ONBOARD_CONTROLLER = 18 */
    uint8_t  autopilot;      /* MAV_AUTOPILOT_INVALID = 8 */
    uint8_t  base_mode;      /* MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1 */
    uint8_t  system_status;  /* MAV_STATE_ACTIVE = 3, MAV_STATE_CRITICAL = 5 */
    uint8_t  mavlink_version;/* 3 для версії протоколу MAVLink v2 */
} mavlink_heartbeat_payload_t;

typedef struct {
    uint8_t  magic;          /* Стартовий байт 0xFD для MAVLink v2 */
    uint8_t  len;            /* Довжина пейлоаду (9 байтів) */
    uint8_t  incompat_flags; /* Прапорці несумісності (0) */
    uint8_t  compat_flags;   /* Прапорці сумісності (0) */
    uint8_t  seq;            /* Порядковий номер пакета */
    uint8_t  sysid;          /* Системний ID апарата (1) */
    uint8_t  compid;         /* ID компонента: MAV_COMP_ID_ONBOARD_COMPUTER = 191 */
    uint8_t  msgid[3];       /* ID повідомлення: 0 = [0x00, 0x00, 0x00] */
    mavlink_heartbeat_payload_t payload;
    uint16_t checksum;       /* Контрольна сума CRC-16-CCITT + CRC_EXTRA (50) */
} mavlink_v2_heartbeat_packet_t;
#pragma pack(pop)

/* Накопичувальний розрахунок контрольної суми MAVLink X.25 */
static uint16_t crc_accumulate(uint8_t byte, uint16_t crc) {
    uint8_t ch = byte ^ (uint8_t)(crc & 0x00FF);
    ch = (uint8_t)(ch ^ (ch << 4));
    return (uint16_t)((crc >> 8) ^ ((uint16_t)ch << 8) ^ ((uint16_t)ch << 3) ^ ((uint16_t)ch >> 4));
}

static uint16_t calculate_mavlink_crc(const uint8_t *buffer, size_t len, uint8_t crc_extra) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 1; i < len; ++i) { /* Пропуск стартового байта 0xFD */
        crc = crc_accumulate(buffer[i], crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}

static int configure_realtime_priority(void) {
    struct sched_param param;
    param.sched_priority = 50;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("Попередження: не вдалося встановити SCHED_FIFO");
    }
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("Попередження: не вдалося заблокувати пам'ять mlockall");
    }
    return 0;
}

static int open_serial_port(const char *dev, speed_t speed) {
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        perror("Помилка відкриття послідовного порту");
        return -1;
    }
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }
    cfmakeraw(&tty);
    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS;
    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static int setup_unix_server_socket(const char *path) {
    unlink(path);
    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK, 0);
    if (fd < 0) {
        perror("Помилка створення UNIX сокета");
        return -1;
    }
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка прив'язки UNIX сокета");
        close(fd);
        return -1;
    }
    chmod(path, 0666);
    return fd;
}

int main(void) {
    configure_realtime_priority();

    int serial_fd = open_serial_port(SERIAL_PORT, BAUDRATE);
    int sock_fd = setup_unix_server_socket(SOCKET_PATH);
    if (serial_fd < 0 || sock_fd < 0) {
        return EXIT_FAILURE;
    }

    struct gpiod_chip *chip = gpiod_chip_open_by_name(GPIO_CHIP_NAME);
    struct gpiod_line *line = NULL;
    if (chip) {
        line = gpiod_chip_get_line(chip, WATCHDOG_PIN);
        if (line) {
            gpiod_line_request_output(line, "companion-watchdog", 0);
        }
    }

    uint8_t packet_seq = 0;
    int pin_state = 0;
    time_t last_worker_ping = time(NULL);
    struct timespec last_hb_time, last_strobe_time, now;
    clock_gettime(CLOCK_MONOTONIC, &last_hb_time);
    clock_gettime(CLOCK_MONOTONIC, &last_strobe_time);

    printf("Companion Watchdog запущено. Моніторинг сокета: %s\n", SOCKET_PATH);

    while (1) {
        clock_gettime(CLOCK_MONOTONIC, &now);

        /* 1. Опитування черги повідомлень від робочих процесів */
        char buf[32];
        ssize_t bytes = recv(sock_fd, buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            if (strncmp(buf, "ALIVE", 5) == 0) {
                last_worker_ping = time(NULL);
            }
        }

        bool worker_healthy = (time(NULL) - last_worker_ping) < PROCESS_TIMEOUT_SEC;

        /* 2. Апаратне стробування GPIO виводу */
        int64_t strobe_dt_ms = (now.tv_sec - last_strobe_time.tv_sec) * 1000 +
                               (now.tv_nsec - last_strobe_time.tv_nsec) / 1000000;
        if (strobe_dt_ms >= STROBE_PERIOD_MS) {
            if (worker_healthy && line) {
                pin_state = !pin_state;
                gpiod_line_set_value(line, pin_state);
            } else if (line) {
                gpiod_line_set_value(line, 0); /* Скидання стробу при аварії */
            }
            last_strobe_time = now;
        }

        /* 3. Генерація кадру MAVLink HEARTBEAT */
        int64_t hb_dt_ms = (now.tv_sec - last_hb_time.tv_sec) * 1000 +
                           (now.tv_nsec - last_hb_time.tv_nsec) / 1000000;
        if (hb_dt_ms >= HEARTBEAT_PERIOD_MS) {
            mavlink_v2_heartbeat_packet_t pkt;
            memset(&pkt, 0, sizeof(pkt));

            pkt.magic = 0xFD;
            pkt.len = sizeof(mavlink_heartbeat_payload_t);
            pkt.incompat_flags = 0;
            pkt.compat_flags = 0;
            pkt.seq = packet_seq++;
            pkt.sysid = 1;
            pkt.compid = 191; /* MAV_COMP_ID_ONBOARD_COMPUTER */
            pkt.msgid[0] = 0x00;
            pkt.msgid[1] = 0x00;
            pkt.msgid[2] = 0x00;

            pkt.payload.type = 18; /* MAV_TYPE_ONBOARD_CONTROLLER */
            pkt.payload.autopilot = 8; /* MAV_AUTOPILOT_INVALID */
            pkt.payload.base_mode = 1; /* MAV_MODE_FLAG_CUSTOM_MODE_ENABLED */
            pkt.payload.system_status = worker_healthy ? 3 : 5; /* 3=ACTIVE, 5=CRITICAL */
            pkt.payload.mavlink_version = 3;

            size_t payload_and_header_len = 10 + sizeof(mavlink_heartbeat_payload_t);
            pkt.checksum = calculate_mavlink_crc((const uint8_t *)&pkt, payload_and_header_len, 50);

            if (write(serial_fd, &pkt, sizeof(pkt)) < 0) {
                perror("Помилка відправки HEARTBEAT");
            }
            last_hb_time = now;
        }

        usleep(10000); /* Крок опитування 10 мс */
    }

    if (line) gpiod_line_release(line);
    if (chip) gpiod_chip_close(chip);
    close(sock_fd);
    close(serial_fd);
    unlink(SOCKET_PATH);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <span>
#include <chrono>
#include <thread>
#include <vector>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <gpiod.h>

namespace companion {

using namespace std::chrono_literals;

inline constexpr std::string_view kSocketPath{"/tmp/companion_health.sock"};
inline constexpr std::string_view kSerialPort{"/dev/ttyAMA0"};
inline constexpr std::string_view kGpioChip{"gpiochip0"};
inline constexpr unsigned int kWatchdogPin = 17;

inline constexpr auto kHeartbeatPeriod = 1000ms;
inline constexpr auto kStrobePeriod = 100ms;
inline constexpr auto kProcessTimeout = 2s;

#pragma pack(push, 1)
struct MavlinkHeartbeatPayload {
    std::uint32_t custom_mode{0};
    std::uint8_t  type{18};            // MAV_TYPE_ONBOARD_CONTROLLER
    std::uint8_t  autopilot{8};         // MAV_AUTOPILOT_INVALID
    std::uint8_t  base_mode{1};         // MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
    std::uint8_t  system_status{3};     // 3=ACTIVE, 5=CRITICAL
    std::uint8_t  mavlink_version{3};
};

struct MavlinkV2HeartbeatPacket {
    std::uint8_t  magic{0xFD};
    std::uint8_t  len{sizeof(MavlinkHeartbeatPayload)};
    std::uint8_t  incompat_flags{0};
    std::uint8_t  compat_flags{0};
    std::uint8_t  seq{0};
    std::uint8_t  sysid{1};
    std::uint8_t  compid{191};          // MAV_COMP_ID_ONBOARD_COMPUTER
    std::uint8_t  msgid[3]{0, 0, 0};
    MavlinkHeartbeatPayload payload{};
    std::uint16_t checksum{0};
};
#pragma pack(pop)

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_{fd} {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_{other.release()} {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

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

class GpioLineGuard {
public:
    GpioLineGuard(std::string_view chip_name, unsigned int pin) {
        chip_ = gpiod_chip_open_by_name(chip_name.data());
        if (chip_) {
            line_ = gpiod_chip_get_line(chip_, pin);
            if (line_) {
                gpiod_line_request_output(line_, "companion-watchdog-cpp", 0);
            }
        }
    }

    ~GpioLineGuard() {
        if (line_) {
            gpiod_line_release(line_);
        }
        if (chip_) {
            gpiod_chip_close(chip_);
        }
    }

    void set_level(int value) noexcept {
        if (line_) {
            gpiod_line_set_value(line_, value);
        }
    }

    [[nodiscard]] bool available() const noexcept { return line_ != nullptr; }

private:
    struct gpiod_chip* chip_{nullptr};
    struct gpiod_line* line_{nullptr};
};

void setup_realtime_priority() noexcept {
    sched_param param{};
    param.sched_priority = 50;
    ::sched_setscheduler(0, SCHED_FIFO, &param);
    ::mlockall(MCL_CURRENT | MCL_FUTURE);
}

[[nodiscard]] std::uint16_t crc_accumulate(std::uint8_t byte, std::uint16_t crc) noexcept {
    std::uint8_t ch = byte ^ static_cast<std::uint8_t>(crc & 0x00FF);
    ch = static_cast<std::uint8_t>(ch ^ (ch << 4));
    return static_cast<std::uint16_t>((crc >> 8) ^ (static_cast<std::uint16_t>(ch) << 8) ^
                                     (static_cast<std::uint16_t>(ch) << 3) ^ (static_cast<std::uint16_t>(ch) >> 4));
}

[[nodiscard]] std::uint16_t calculate_mavlink_crc(std::span<const std::uint8_t> buffer, std::uint8_t crc_extra) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (std::size_t i = 1; i < buffer.size(); ++i) { // без стартового байта 0xFD
        crc = crc_accumulate(buffer[i], crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}

std::expected<FileDescriptor, std::error_code> open_serial(std::string_view dev, speed_t speed) {
    int fd = ::open(dev.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    struct termios tty{};
    if (::tcgetattr(fd, &tty) != 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    cfmakeraw(&tty);
    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS;
    if (::tcsetattr(fd, TCSANOW, &tty) != 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return FileDescriptor(fd);
}

std::expected<FileDescriptor, std::error_code> open_unix_socket(std::string_view path) {
    ::unlink(path.data());
    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, path.data(), sizeof(addr.sun_path) - 1);
    if (::bind(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    ::chmod(path.data(), 0666);
    return FileDescriptor(fd);
}

} // namespace companion

int main() {
    companion::setup_realtime_priority();

    auto serial_res = companion::open_serial(companion::kSerialPort, B921600);
    if (!serial_res) {
        std::cerr << "Помилка відкриття UART: " << serial_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    auto socket_res = companion::open_unix_socket(companion::kSocketPath);
    if (!socket_res) {
        std::cerr << "Помилка відкриття сокета: " << socket_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    auto serial_fd = std::move(*serial_res);
    auto sock_fd = std::move(*socket_res);
    companion::GpioLineGuard gpio(companion::kGpioChip, companion::kWatchdogPin);

    std::uint8_t seq = 0;
    int pin_state = 0;
    auto last_worker_ping = std::chrono::steady_clock::now();
    auto last_hb_time = std::chrono::steady_clock::now();
    auto last_strobe_time = std::chrono::steady_clock::now();

    std::cout << "C++23 Companion Watchdog запущено. Моніторинг активний.\n";

    while (true) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Прийом сигналів активності від робочих потоків
        char buf[32];
        ssize_t bytes = ::recv(sock_fd.get(), buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            if (std::string_view(buf, bytes).starts_with("ALIVE")) {
                last_worker_ping = now;
            }
        }

        const bool worker_healthy = (now - last_worker_ping) < companion::kProcessTimeout;

        // 2. Генерація стробу апаратного сторожа
        if (now - last_strobe_time >= companion::kStrobePeriod) {
            if (worker_healthy && gpio.available()) {
                pin_state = 1 - pin_state;
                gpio.set_level(pin_state);
            } else {
                gpio.set_level(0);
            }
            last_strobe_time = now;
        }

        // 3. Відправка пакета MAVLink HEARTBEAT
        if (now - last_hb_time >= companion::kHeartbeatPeriod) {
            companion::MavlinkV2HeartbeatPacket pkt{};
            pkt.seq = seq++;
            pkt.payload.system_status = worker_healthy ? 3 : 5; // 3=ACTIVE, 5=CRITICAL

            const auto pkt_span = std::span<const std::uint8_t>(
                reinterpret_cast<const std::uint8_t*>(&pkt),
                10 + sizeof(companion::MavlinkHeartbeatPayload)
            );
            pkt.checksum = companion::calculate_mavlink_crc(pkt_span, 50);

            ::write(serial_fd.get(), &pkt, sizeof(pkt));
            last_hb_time = now;
        }

        std::this_thread::sleep_for(10ms);
    }

    ::unlink(companion::kSocketPath.data());
    return EXIT_SUCCESS;
}
```
:::

## Інтеграція зі службою systemd та моніторинг

Для забезпечення безперервного запуску під час завантаження операційної системи демон оформлюється як системний сервіс `systemd`. Файл конфігурації `/etc/systemd/system/companion-watchdog.service` задає правила перезапуску та ліміти ресурсів:

```ini
[Unit]
Description=Companion Watchdog Daemon for Flight Controller
After=network.target local-fs.target
Before=ros2_nodes.service mavsdk.service

[Service]
Type=simple
ExecStart=/usr/local/bin/companion_watchdog
Restart=always
RestartSec=1s
CPUSchedulingPolicy=fifo
CPUSchedulingPriority=50
LimitMEMLOCK=infinity
WatchdogSec=5s

[Install]
WantedBy=multi-user.target
```

Параметр `CPUSchedulingPolicy=fifo` гарантує, що планувальник ядра виділятиме кванти часу демону поза чергою звичайних фонових задач. Якщо сам демон нагляду впаде, `systemd` перезапустить його впродовж однієї секунди.

## Інженерні підводні камені та надійність

1. **Вплив буферизації файлової системи на планувальник:**
   Якщо демон нагляду намагатиметься записувати діагностичні повідомлення у звичайний файл на SD-карті чи eMMC синхронно (`fwrite` / `std::ofstream`), ядро Linux під час інтенсивного скидання кешу сторінок (*flush dirty pages*) заблокує процес у стані `D` (*uninterruptible sleep*) на час від 500 мс до кількох секунд. У результаті демон пропустить такти генерації стробу, і апаратний сторож помилково скине живлення повністю справного комп'ютера. **Правило:** робочий цикл сторожа повинен працювати виключно з оперативною пам'яттю, не містити дискового вводу-виводу і виділяти пам'ять лише на етапі ініціалізації.

2. **Необхідність блокування сторінок пам'яті (`mlockall`):**
   При високому навантаженні на оперативну пам'ять (наприклад, запуск важкої моделі сегментації) демон нагляду може бути частково витіснений у swap-розділ. Наступне звернення до коду викличе обробку промаху сторінки (*page fault*), що займе сотні мілісекунд. Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` у поєднанні з пріоритетом `SCHED_FIFO` гарантує, що сторінки процесу сторожа завжди залишаються у фізичній RAM і виконуються з мінімальною затримкою.

3. **Скидання залишкових прав доступу до сокета:**
   При аварійному перезапуску самого демона файл сокета `/tmp/companion_health.sock` залишається у файловій системі. Демон зобов'язаний явно викликати `unlink()` перед функцією `bind()`, інакше спроба відкриття порту поверне помилку `EADDRINUSE`, і моніторинг не запуститься.

4. **Розрив з'єднання та переповнення буферів UART:**
   Якщо апаратний блок UART комп'ютера налаштовано без апаратного керування потоком (RTS/CTS), при високому навантаженні ядра драйвер `tty` може скидати вхідні байти через переповнення буфера FIFO (*RX FIFO overrun*). Це призводить до спотворення контрольної суми CRC кадру `HEARTBEAT` на стороні FCU. Демон повинен контролювати лічильники помилок через системний інтерфейс `/sys/class/tty/ttyAMA0/device/` та своєчасно сповіщати про деградацію фізичної лінії зв'язку.
