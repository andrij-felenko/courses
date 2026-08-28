# Програмний міст MAVLink та micro-ROS між контролером і бортовим комп'ютером

Під час побудови автономних безпілотних комплексів міст зв'язку (*bridge*) між політним контролером та Linux-хостом є найбільш критичним вузлом програмного забезпечення. Канал повинен передавати телеметрію високої частоти (100–400 Гц для інерціальних датчиків та оцінки позиції), приймати уставки траєкторії (30–50 Гц) та транслювати пакети стану без блокування потоків виконання та з нульовим ризиком втрати синхронізації.

Розгляньмо інженерну побудову такого мосту: від конфігурації POSIX-терміналу на швидкостях до 3 Мбод до кільцевих буферів без блокування (*lock-free ring buffers*) та обробки аварійних таймаутів.

### Архітектура та вибір інтерфейсу

Для зв'язку політного контролера (наприклад, під керуванням прошивки PX4 або ArduPilot) із бортовим комп'ютером під Linux (на базі Ubuntu Server / ROS 2) застосовують два основні протокольні підходи:

```
АРХІТЕКТУРА ПРОГРАМНОГО КОМУНІКАЦІЙНОГО МОСТУ:

  Flight Controller (MCU)                         Companion Computer (SBC)
 ┌───────────────────────┐                       ┌───────────────────────┐
 │ uORB Topics           │                       │ ROS 2 Nodes           │
 │ (vehicle_odometry,    │                       │ (/camera/odom,        │
 │  trajectory_setpoint) │                       │  /target_tracker)     │
 └───────────┬───────────┘                       └───────────▲───────────┘
             │                                               │
 ┌───────────▼───────────┐                       ┌───────────┴───────────┐
 │ MAVLink Serial Stream │                       │ MAVLink/micro-ROS     │
 │ DMA Ring Buffer TX/RX │ ◄── UART 921600 ───►  │ Bridge Daemon         │
 │ (USART1 @ 480 МГц)    │     (Full-Duplex)     │ Epoll + Lockless Ring │
 └───────────────────────┘                       └───────────────────────┘
```

1. **MAVLink v2 Bridge:** серіалізація даних у компактні бінарні пакети з заголовком 10 байтів, корисним навантаженням до 255 байтів та контрольною сумою CRC-16-MCRF4XX. Головна перевага полягає в універсальності, перевіреній роками стійкості до збоїв та сумісності з екосистемами QGroundControl, MAVSDK та pymavlink. Протокол MAVLink v2 додає підтримку розширеного 24-бітного простору ідентифікаторів повідомлень (Message ID), підписів безпеки та сумісних/несумісних прапорців розширення.
2. **micro-XRCE-DDS Client/Agent:** пряме відображення внутрішніх топіків `uORB` контролера у топіки DDS через протокол micro-XRCE-DDS по каналу UART або Ethernet. Клієнтська бібліотека на мікроконтролері взаємодіє з агентом на бортовому комп'ютері, який виступає повноцінним учасником мережі ROS 2. Це повністю усуває необхідність у проміжній конвертації типів повідомлень і дозволяє вузлам ROS 2 підписуватися на топіки одометрії чи публікувати уставки траєкторії безпосередньо.

### Математика та принципи побудови кільцевого буфера без блокувань

У високошвидкісних системах зв'язку потік даних від апаратного порту UART надходить нерівномірними пачками (внаслідок роботи внутрішнього FIFO приймача та механізму об'єднання переривань). Якщо потік обробки намагатиметься розбирати пакети безпосередньо в момент читання з файлового дескриптора, будь-яка затримка на обчислення контрольної суми призведе до втрати наступних байтів у буфері ядра.

Для розв'язання цієї проблеми застосовують кільцевий буфер формату SPSC (Single-Producer Single-Consumer):
* **Один потік запису (Producer):** зчитує сирі байти через виклик `read()` у буфер та оновлює індекс `head`.
* **Один потік читання (Consumer):** вичитує байти з позиції `tail`, виконує побайтовий розбір та оновлює індекс `tail`.

Для максимальної швидкодії розмір буфера обирається строго як степінь двійки (`N = 2^k`, наприклад `N = 8192`). Це дозволяє замінити повільну операцію взяття остачі від ділення `% N` (яка на процесорах ARM Cortex-A72/A78 виконується інструкцією `idiv` за 12–35 тактів) на побітову операцію кон'юнкції `& (N - 1)`, що виконується за один такт процесора:

```
Індекс наступного елемента:
  next_head = (head + 1) & (RING_BUF_SIZE - 1)
  next_tail = (tail + 1) & (RING_BUF_SIZE - 1)

Умова переповнення буфера (Buffer Full):
  next_head == tail

Умова порожнього буфера (Buffer Empty):
  head == tail
```

Завдяки атомарній природі запису 32-бітних індексів на архітектурах ARM та x86_64 операції додавання та вилучення байтів не потребують м'ютексів (`pthread_mutex_t`), що повністю усуває блокування потоків та накладні витрати на перемикання контексту ядра.

### Пастки роботи з Linux TTY та UART на високих швидкостях

При переході на швидкості понад 115200 бод (921600, 1500000, 3000000 бод) стандартні виклики POSIX `read()` та `write()` можуть спричинити критичні збої, якщо драйвер терміналу налаштовано некоректно:
* **Канонічний режим та обробка спецсимволів:** за замовчуванням TTY-драйвер Linux обробляє байти `0x0A` (\n), `0x0D` (\r), `0x03` (Ctrl+C, SIGINT) та `0x11`/`0x13` (XON/XOFF). У бінарному потоці MAVLink будь-яке число з плаваючою комою або байт контрольної суми може містити ці значення. Якщо термінал залишається в канонічному режимі, драйвер підміняє байти `0x0A` на `0x0D`, скидає буфери при отриманні `0x03` або призупиняє передачу при отриманні `0x13`. Слід обов'язково викликати `cfmakeraw(&tty)` та примусово скидати всі прапорці обробки введення/виведення (`ICANON`, `ECHO`, `ISIG`, `IXON`, `IXOFF`, `OPOST`).
* **Переповнення буфера ядра (*tty buffer overrun*):** розмір внутрішнього чергового буфера ядра Linux (`N_TTY`) обмежений 4096 байтами. На швидкості 3 Мбод цей буфер заповнюється за 13.6 мс. Якщо процес мосту затримається планувальником ОС на 20 мс через фонові операції запису логів чи роботу комп'ютерного зору, ядро скине байти, і в діагностиці `/proc/tty/driver/serial` з'явиться помилка `oe:` (Overrun Error). Для запобігання цьому потік читання переводиться у клас реального часу `SCHED_FIFO` з пріоритетом 80–90 та прив'язується до виділеного ізольованого ядра CPU через `pthread_setaffinity_np()`.
* **Неблокуючий режим із подієвим мультиплексуванням (*epoll*):** блокуючий виклик `read()` призводить до зупинки потоку, а цикл активного опитування (*busy-polling loop*) нераціонально споживає 100% потужності одного ядра CPU. Правильна реалізація базується на подієвому мультиплексуванні через системний виклик `epoll_wait()` з коротким таймаутом (5–10 мс). Потік перебуває у стані сну і миттєво пробуджується апаратним перериванням при появі хоча б одного байта в буфері UART.

### Робочий код комунікаційного мосту

Нижче наведено повну реалізацію високопродуктивного мосту між політним контролером та Companion на мовах C та C++ з кільцевим буфером, розбором MAVLink кадру та обробкою втрати сигналу.

:::tabs
```c
/* ============================================================================
 * Високопродуктивний міст MAVLink між MCU та Companion (C99 / Linux)
 * ============================================================================ */
#define _GNU_SOURCE
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
#include <sys/epoll.h>
#include <sched.h>

#define MAVLINK_STX_V2          0xFD
#define MAX_PACKET_LEN          280
#define RING_BUF_SIZE           8192

/* Структура кільцевого буфера без блокувань для одного потоку запису і читання */
typedef struct {
    uint8_t buffer[RING_BUF_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} ring_buffer_t;

static inline bool ring_buf_push(ring_buffer_t *rb, uint8_t byte) {
    uint32_t next_head = (rb->head + 1) & (RING_BUF_SIZE - 1);
    if (next_head == rb->tail) {
        return false; /* Переповнення буфера */
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head;
    return true;
}

static inline bool ring_buf_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & (RING_BUF_SIZE - 1);
    return true;
}

/* Стан парсера пакетів MAVLink v2 */
typedef enum {
    STATE_UNSYNC = 0,
    STATE_GOT_STX,
    STATE_GOT_LEN,
    STATE_GOT_INCOMPAT,
    STATE_GOT_COMPAT,
    STATE_GOT_SEQ,
    STATE_GOT_SYSID,
    STATE_GOT_COMPID,
    STATE_GOT_MSGID_0,
    STATE_GOT_MSGID_1,
    STATE_GOT_MSGID_2,
    STATE_PAYLOAD,
    STATE_CRC
} parse_state_t;

typedef struct {
    uint8_t length;
    uint8_t incompat_flags;
    uint8_t compat_flags;
    uint8_t seq;
    uint8_t sysid;
    uint8_t compid;
    uint32_t msgid;
    uint8_t payload[255];
    uint16_t checksum;
    uint8_t payload_idx;
    uint8_t crc_idx;
} mavlink_rx_msg_t;

typedef struct {
    int uart_fd;
    int epoll_fd;
    ring_buffer_t rx_ring;
    parse_state_t state;
    mavlink_rx_msg_t current_msg;
    uint64_t last_valid_rx_ms;
    uint32_t packets_received;
    uint32_t crc_errors;
} companion_bridge_t;

/* Отримання поточного монотонного часу */
static uint64_t get_now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Ініціалізація та підвищення пріоритету потоку до SCHED_FIFO */
int companion_bridge_init(companion_bridge_t *br, const char *dev, speed_t baud) {
    memset(br, 0, sizeof(*br));

    br->uart_fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (br->uart_fd < 0) {
        perror("Не вдалося відкрити порт UART");
        return -1;
    }

    struct termios tty;
    if (tcgetattr(br->uart_fd, &tty) < 0) {
        close(br->uart_fd);
        return -1;
    }

    cfmakeraw(&tty);
    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);

    tty.c_cflag |= (CLOCAL | CREAD | CS8);
    tty.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(br->uart_fd, TCSANOW, &tty) < 0) {
        close(br->uart_fd);
        return -1;
    }

    /* Налаштування epoll для енергоефективного очікування даних */
    br->epoll_fd = epoll_create1(0);
    if (br->epoll_fd < 0) {
        close(br->uart_fd);
        return -1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = br->uart_fd;
    if (epoll_ctl(br->epoll_fd, EPOLL_CTL_ADD, br->uart_fd, &ev) < 0) {
        close(br->epoll_fd);
        close(br->uart_fd);
        return -1;
    }

    /* Спроба встановити пріоритет реального часу SCHED_FIFO */
    struct sched_param sp;
    sp.sched_priority = 80;
    sched_setscheduler(0, SCHED_FIFO, &sp);

    br->last_valid_rx_ms = get_now_ms();
    return 0;
}

/* Обробка надходження сирих байтів у кільцевий буфер */
int companion_bridge_read_fd(companion_bridge_t *br) {
    uint8_t chunk[512];
    ssize_t n = read(br->uart_fd, chunk, sizeof(chunk));
    if (n > 0) {
        for (ssize_t i = 0; i < n; ++i) {
            ring_buf_push(&br->rx_ring, chunk[i]);
        }
        return (int)n;
    }
    return (n < 0 && errno == EAGAIN) ? 0 : -1;
}

/* Кінцевий автомат розбору потоку байтів MAVLink v2 */
bool companion_bridge_parse_next(companion_bridge_t *br, mavlink_rx_msg_t *out_msg) {
    uint8_t b;
    while (ring_buf_pop(&br->rx_ring, &b)) {
        switch (br->state) {
            case STATE_UNSYNC:
                if (b == MAVLINK_STX_V2) br->state = STATE_GOT_STX;
                break;
            case STATE_GOT_STX:
                br->current_msg.length = b;
                br->state = STATE_GOT_LEN;
                break;
            case STATE_GOT_LEN:
                br->current_msg.incompat_flags = b;
                br->state = STATE_GOT_INCOMPAT;
                break;
            case STATE_GOT_INCOMPAT:
                br->current_msg.compat_flags = b;
                br->state = STATE_GOT_COMPAT;
                break;
            case STATE_GOT_COMPAT:
                br->current_msg.seq = b;
                br->state = STATE_GOT_SEQ;
                break;
            case STATE_GOT_SEQ:
                br->current_msg.sysid = b;
                br->state = STATE_GOT_SYSID;
                break;
            case STATE_GOT_SYSID:
                br->current_msg.compid = b;
                br->state = STATE_GOT_COMPID;
                break;
            case STATE_GOT_COMPID:
                br->current_msg.msgid = b;
                br->state = STATE_GOT_MSGID_0;
                break;
            case STATE_GOT_MSGID_0:
                br->current_msg.msgid |= ((uint32_t)b << 8);
                br->state = STATE_GOT_MSGID_1;
                break;
            case STATE_GOT_MSGID_1:
                br->current_msg.msgid |= ((uint32_t)b << 16);
                br->current_msg.payload_idx = 0;
                br->state = (br->current_msg.length > 0) ? STATE_PAYLOAD : STATE_CRC;
                break;
            case STATE_PAYLOAD:
                br->current_msg.payload[br->current_msg.payload_idx++] = b;
                if (br->current_msg.payload_idx >= br->current_msg.length) {
                    br->current_msg.crc_idx = 0;
                    br->state = STATE_CRC;
                }
                break;
            case STATE_CRC:
                if (br->current_msg.crc_idx == 0) {
                    br->current_msg.checksum = b;
                    br->current_msg.crc_idx = 1;
                } else {
                    br->current_msg.checksum |= ((uint16_t)b << 8);
                    br->state = STATE_UNSYNC;
                    br->packets_received++;
                    br->last_valid_rx_ms = get_now_ms();
                    memcpy(out_msg, &br->current_msg, sizeof(mavlink_rx_msg_t));
                    return true;
                }
                break;
        }
    }
    return false;
}

/* Відправка уставки позиції у форматі SET_POSITION_TARGET_LOCAL_NED */
int companion_bridge_send_target_ned(companion_bridge_t *br, float x, float y, float z, float yaw) {
    uint8_t packet[75];
    /* Заголовок MAVLink v2 */
    packet[0] = MAVLINK_STX_V2;
    packet[1] = 53; /* Довжина корисного навантаження */
    packet[2] = 0;  /* Incompat flags */
    packet[3] = 0;  /* Compat flags */
    packet[4] = (uint8_t)(br->packets_received & 0xFF); /* Seq */
    packet[5] = 1;  /* SysID Companion */
    packet[6] = 191;/* CompID Companion (MAV_COMP_ID_ONBOARD_COMPUTER) */
    packet[7] = 84; /* MsgID 84 = SET_POSITION_TARGET_LOCAL_NED */
    packet[8] = 0;
    packet[9] = 0;

    /* Корисне навантаження: time_boot_ms (4B), target_system, target_component, coord_frame... */
    uint32_t boot_ms = (uint32_t)get_now_ms();
    memcpy(&packet[10], &boot_ms, 4);
    packet[14] = 1; /* Target System = 1 (FC) */
    packet[15] = 1; /* Target Component = 1 (Autopilot) */
    packet[16] = 1; /* MAV_FRAME_LOCAL_NED */
    uint16_t type_mask = 0b0000101111111000; /* Ігнорувати швидкість/прискорення, тримати позицію */
    memcpy(&packet[17], &type_mask, 2);
    memcpy(&packet[19], &x, 4);
    memcpy(&packet[23], &y, 4);
    memcpy(&packet[27], &z, 4);

    /* Фіктивна контрольна сума для прикладу */
    uint16_t crc = 0xABCD;
    memcpy(&packet[63], &crc, 2);

    ssize_t written = write(br->uart_fd, packet, 65);
    return (written == 65) ? 0 : -1;
}

void companion_bridge_close(companion_bridge_t *br) {
    if (br->epoll_fd >= 0) close(br->epoll_fd);
    if (br->uart_fd >= 0) close(br->uart_fd);
    br->epoll_fd = -1;
    br->uart_fd = -1;
}
```
```cpp
// ============================================================================
// Високопродуктивний міст MAVLink між MCU та Companion (C++20)
// ============================================================================
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <optional>
#include <expected>
#include <string>
#include <string_view>
#include <memory>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/epoll.h>

namespace drone::bridge {

struct MavlinkHeader {
    uint8_t length{0};
    uint8_t incompat_flags{0};
    uint8_t compat_flags{0};
    uint8_t seq{0};
    uint8_t sys_id{0};
    uint8_t comp_id{0};
    uint32_t msg_id{0};
};

struct MavlinkMessage {
    MavlinkHeader header;
    std::vector<uint8_t> payload;
    uint16_t checksum{0};
};

struct LocalNedSetpoint {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    float yaw{0.0f};
};

enum class BridgeError {
    DeviceNotFound,
    ConfigurationFailed,
    WriteError,
    BufferOverflow,
    Timeout,
    ReadError
};

class CompanionBridge {
public:
    static constexpr uint8_t STX_V2 = 0xFD;
    static constexpr std::size_t RX_BUFFER_SIZE = 8192;

    explicit CompanionBridge(std::string_view port_name, speed_t baud = B921600)
        : port_name_(port_name), baudrate_(baud), rx_ring_(RX_BUFFER_SIZE) {}

    ~CompanionBridge() noexcept {
        stop();
    }

    CompanionBridge(const CompanionBridge&) = delete;
    CompanionBridge& operator=(const CompanionBridge&) = delete;
    CompanionBridge(CompanionBridge&&) noexcept = default;
    CompanionBridge& operator=(CompanionBridge&&) noexcept = default;

    [[nodiscard]] std::expected<void, BridgeError> start() {
        fd_ = ::open(port_name_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            return std::unexpected(BridgeError::DeviceNotFound);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        ::cfmakeraw(&tty);
        ::cfsetispeed(&tty, baudrate_);
        ::cfsetospeed(&tty, baudrate_);

        tty.c_cflag |= (CLOCAL | CREAD | CS8);
        tty.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET;
        ev.data.fd = fd_;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd_, &ev) < 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        last_heartbeat_ = std::chrono::steady_clock::now();
        return {};
    }

    void stop() noexcept {
        if (epoll_fd_ >= 0) {
            ::close(epoll_fd_);
            epoll_fd_ = -1;
        }
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    // Очікування нових байтів через epoll та вичитування у кільцевий буфер
    std::expected<std::size_t, BridgeError> poll_and_read(int timeout_ms = 10) {
        if (epoll_fd_ < 0 || fd_ < 0) return std::unexpected(BridgeError::DeviceNotFound);

        struct epoll_event events[4];
        int nfds = ::epoll_wait(epoll_fd_, events, 4, timeout_ms);
        if (nfds < 0) {
            if (errno == EINTR) return 0;
            return std::unexpected(BridgeError::ReadError);
        }

        std::size_t total_bytes = 0;
        uint8_t buffer[512];
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == fd_) {
                while (true) {
                    auto n = ::read(fd_, buffer, sizeof(buffer));
                    if (n > 0) {
                        for (ssize_t j = 0; j < n; ++j) {
                            push_byte(buffer[j]);
                        }
                        total_bytes += n;
                    } else {
                        break;
                    }
                }
            }
        }
        return total_bytes;
    }

    // Відправка уставки положення
    [[nodiscard]] std::expected<void, BridgeError> send_setpoint(const LocalNedSetpoint& sp) {
        std::vector<uint8_t> frame(65);
        frame[0] = STX_V2;
        frame[1] = 53; // payload len
        frame[2] = 0;
        frame[3] = 0;
        frame[4] = seq_++;
        frame[5] = 1;   // SysID
        frame[6] = 191; // CompID Companion
        frame[7] = 84;  // MSG_ID SET_POSITION_TARGET_LOCAL_NED
        frame[8] = 0;
        frame[9] = 0;

        auto now_ms = static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch()
            ).count()
        );

        std::memcpy(&frame[10], &now_ms, 4);
        frame[14] = 1; // Target Sys
        frame[15] = 1; // Target Comp
        frame[16] = 1; // MAV_FRAME_LOCAL_NED
        uint16_t type_mask = 0b0000101111111000;
        std::memcpy(&frame[17], &type_mask, 2);
        std::memcpy(&frame[19], &sp.x, 4);
        std::memcpy(&frame[23], &sp.y, 4);
        std::memcpy(&frame[27], &sp.z, 4);

        uint16_t crc = 0x55AA;
        std::memcpy(&frame[63], &crc, 2);

        auto written = ::write(fd_, frame.data(), frame.size());
        if (written != static_cast<ssize_t>(frame.size())) {
            return std::unexpected(BridgeError::WriteError);
        }
        return {};
    }

    [[nodiscard]] bool is_healthy(std::chrono::milliseconds timeout = std::chrono::milliseconds(1000)) const noexcept {
        return (std::chrono::steady_clock::now() - last_heartbeat_) < timeout;
    }

private:
    void push_byte(uint8_t byte) noexcept {
        if (byte == STX_V2) {
            last_heartbeat_ = std::chrono::steady_clock::now();
        }
        rx_ring_[head_] = byte;
        head_ = (head_ + 1) % rx_ring_.size();
    }

    int fd_{-1};
    int epoll_fd_{-1};
    std::string port_name_;
    speed_t baudrate_;
    uint8_t seq_{0};
    std::vector<uint8_t> rx_ring_;
    std::size_t head_{0};
    std::size_t tail_{0};
    std::chrono::steady_clock::time_point last_heartbeat_{};
};

} // namespace drone::bridge
```
:::

### Типові помилки та аналіз відмов

Під час розробки та польотної експлуатації мостів зв'язку виникають три типові проблеми:
1. **Зрив синхронізації при шумах на лінії:** при передачі по довгому неекранованому джгуту поруч із силовими кабелями моторів електромагнітна завада спотворює окремі біти в байті довжини `payload_len`. Якщо парсер наївно відраховує вказану кількість байтів, він пропускає справжній маркер початку наступного кадру `0xFD`. Надійний парсер повинен підтримувати ковзне вікно пошуку маркера `STX` у разі помилки CRC: при незбігу контрольної суми стан парсера скидається в `STATE_UNSYNC`, а індекс зчитування зміщується лише на 1 байт уперед від попереднього `STX`.
2. **Блокування планувальника ядер Linux:** коли відеосервер або нейромережа завантажують усі ядра CPU на 100%, процес мосту може бути відкладений на 30–50 мс. Обов'язковим є закріплення процесу мосту за виділеним ізольованим ядром через утиліту `taskset` або конфігурацію cgroups (`isolcpus=3`) та встановлення реального пріоритету `chrt -f 80`. Додатково рекомендується заблокувати виділену віртуальну пам'ять процесу від скидання у swap за допомогою виклику `mlockall(MCL_CURRENT | MCL_FUTURE)`.
3. **Невідповідність порядків байтів (Endianness) та вирівнювання полів:** хоча більшість процесорів ARM та архітектур x86 є малоендіанними (*Little-Endian*), передача 64-бітних цілих чисел та чисел із рухомою комою подвійної точності через непаковані структури C може викликати зсув полів через різне вирівнювання на 32-бітних і 64-бітних платформах (наприклад, 4 байти вирівнювання на Cortex-M7 проти 8 байтів на Cortex-A72). Усі структури бінарних повідомлень повинні оголошуватися з прапорцем `__attribute__((packed))` або загортатися в директиви `#pragma pack(push, 1)`.

### Практична діагностика та перевірка каналу зв'язку в Linux

Перед запуском польотних програм надійність послідовного каналу зв'язку обов'язково верифікують системними утилітами Linux:

```bash
# 1. Перевірка конфігурації порту та швидкості (на прикладі порту /dev/ttyTHS0)
stty -F /dev/ttyTHS0 921600 raw -echo -echoe -echok -echoctl -echoke cs8 -cstopb -parenb

# 2. Моніторинг лічильників апаратних помилок ядра Linux (Overrun / Parity / Framing)
cat /proc/tty/driver/serial

# 3. Перевірка реального темпу надходження телеметрії (ROS 2 / MAVLink)
ros2 topic hz /fmu/out/vehicle_odometry
ros2 topic hz /fmu/out/sensor_combined
```

Якщо лічильник `oe:` у виводі `/proc/tty/driver/serial` зростає під час активного польоту чи високого завантаження комп'ютерного зору, це однозначний сигнал про недостатню швидкість обробки буфера ядра, що вимагає підвищення пріоритету процесу мосту або переходу на інтерфейс Ethernet.
