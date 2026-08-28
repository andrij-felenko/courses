# ⚙️ Практичний міст зв'язку супутнього комп'ютера на C++ та Python

Супутній комп'ютер під керуванням Linux повинен взаємодіяти з польотним контролером у режимі реального часу: безперервно приймати потоки телеметрії, регулярно надсилати підтвердження працездатності (heartbeat) та транслювати просторові уставки з фіксованою частотою не менше двадцяти герців. Розгляньмо побудову повнофункціонального моста зв'язку (Companion Bridge) для взаємодії через апаратний порт UART на швидкості 921 600 бод з апаратним керуванням потоком CTS/RTS на мовах C, C++ та Python, а також методи діагностики та налагодження низькорівневого каналу.

---

### Архітектура мостової програми

Міст зв'язку супутнього комп'ютера розв'язує три взаємопов'язані задачі, кожна з яких має власний часовий профіль та вимоги до детермінізму:

```
                  +----------------------------------------------+
                  |  Супутній комп'ютер (Companion Bridge App)  |
                  +----------------------------------------------+
                                         |
     +-----------------------------------+-----------------------------------+
     |                                   |                                   |
     v                                   v                                   v
+-----------------------+   +-------------------------+   +-------------------------+
|  Потік прийому (RX)   |   |   Потік пульсу (HB)     |   |  Потік уставок (TX)     |
|  - вичитка TTY        |   |   - надсилання HEARTBEAT|   |   - генерація SET_POS   |
|  - mavlink_parse_char |   |   - частота 1 Гц        |   |   - частота 20 Гц       |
|  - оновлення стану FC |   |   - compid = 191        |   |   - type_mask керування |
+-----------------------+   +-------------------------+   +-------------------------+
     |                                   |                                   |
     +-----------------------------------+-----------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   /dev/ttyAMA0 (921600 8N1)   |
                         |   Апаратний CTS/RTS + DMA     |
                         +-------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |      Польотний контролер      |
                         |    (PX4 Offboard / ArduPilot) |
                         +-------------------------------+
```

1. **Потік прийому (RX Task):** блокується на виклику `read()` або системному мультиплексорі `poll()`, безперервно зчитує сирі байти з черги драйвера TTY ядра Linux, згодовує їх у кінцевий автомат `mavlink_parse_char()`, розпаковує структури повідомлень, фільтрує за `msgid` та атомарно оновлює стан орієнтації, координат і заряду батареї.
2. **Потік пульсу (Heartbeat Task):** один раз на секунду (1 Гц) формує та надсилає повідомлення `HEARTBEAT` із власним ідентифікатором компонента `compid = 191` (`MAV_COMP_ID_ONBOARD_COMPUTER`), сигналізуючи автопілоту, що високорівневий обчислювач активний та готовий до керування.
3. **Потік передачі уставок (Setpoint Task):** прокидається строго кожні 50 мілісекунд (20 Гц) за системним таймером і транслює повідомлення `SET_POSITION_TARGET_LOCAL_NED` із розрахованими швидкостями або цільовими координатами, запобігаючи спрацьовуванню тайм-ауту втрати зв'язку (Setpoint Timeout) на стороні автопілота.

---

### Робота кінцевого автомата розбору MAVLink

Парсер MAVLink v2 реалізовано як потоковий кінцевий автомат (Finite State Machine, FSM), що обробляє потік байт-за-байтом без потреби накопичення всього пакета в проміжному буфері:

```
[Початок] ──> Пошук STX (0xFD) ──> Зчитування LEN (0..255) ──> Прапорці INC/CMP
                 │
                 v
      Зчитування SEQ, SYSID, COMPID ──> 24-бітний MSG ID (3 байти)
                 │
                 v
      Накопичення PAYLOAD (LEN байтів) ──> Перевірка CRC16 (MCRF4XX + CRC_EXTRA)
                 │
                 ├──[CRC збігся]──> Пакет валідний (виклик обробника)
                 └──[CRC помилка]─> Скидання стану в UNINIT, пошук наступного STX
```

Ключовим елементом надійності MAVLink є поле `CRC_EXTRA`: при кодогенерації для кожного типу повідомлення обчислюється однобайтний хеш від його структури в XML. Цей байт додається до розрахунку контрольної суми пакета. Якщо польотний контролер і супутній комп'ютер мають різні версії визначення повідомлення (наприклад, різний порядок полів або типи даних), `CRC_EXTRA` не збігається, і парсер автоматично відкидає несумісний пакет, захищаючи пам'ять від пошкодження некоректними даними.

---

### Налаштування POSIX TTY та апаратного CTS/RTS

Для коректної роботи послідовного порту на швидкості 921 600 бод стандартна конфігурація термінала Linux повинна бути повністю очищена від спадщини телетайпів:

- **Прапорець `CRTSCTS`:** вмикає апаратне керування лініями RTS/CTS. Приймач автоматично скидає рівень RTS у логічну одиницю (активний низький рівень у RS-232, але прямий високий у 3.3V LVTTL), коли його внутрішній FIFO заповнюється на 3/4. Передавач апаратно зупиняє видачу байтів, якщо лінія CTS неактивна.
- **Вимкнення програмного контролю `IXON | IXOFF`:** у бінарному протоколі MAVLink байти корисного навантаження можуть випадково набувати значень `0x11` (ASCII XON) або `0x13` (ASCII XOFF). Якщо програмний контроль увімкнено, драйвер TTY Linux сприйме цей байт як команду зупинки передачі й заблокує весь канал зв'язку.
- **Вимкнення обробки символів `ICRNL | ONLCR | OPOST`:** запобігає автоматичній заміні байта `0x0A` (`\n`) на пару `0x0D 0x0A` (`\r\n`), що спотворило б бінарні байти MAVLink.
- **Параметри `VMIN = 0` та `VTIME = 1`:** забезпечують неблокуюче читання з максимальним часом очікування 100 мс, що дозволяє потоку прийому періодично перевіряти прапорець зупинки програми без зависання в системному виклику.

---

### Реалізація моста на C та C++

У системному програмуванні на C та C++ критично важливо правильно налаштувати структури `termios`, забезпечити коректне закриття дескрипторів за принципом RAII (Resource Acquisition Is Initialization) та виключити стан гонитви (data race) між потоками читання та запису.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <linux/serial.h>
#include <mavlink.h>

#define SERIAL_PORT "/dev/ttyAMA0"
#define SYSTEM_ID   1
#define COMPONENT_ID MAV_COMP_ID_ONBOARD_COMPUTER

typedef struct {
    int fd;
    volatile bool running;
    pthread_t rx_thread;
    pthread_t hb_thread;
    pthread_t tx_thread;
    float current_yaw;
} companion_bridge_t;

static int configure_serial(int fd) {
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) return -1;

    // 921600 бод, 8N1, апаратний flow control CTS/RTS
    cfsetospeed(&tty, B921600);
    cfsetispeed(&tty, B921600);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD | CRTSCTS);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB);

    // Сирий (raw) режим без перетворень байтів
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF | IXANY);
    tty.c_oflag &= ~(OPOST | ONLCR);
    tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 1; // таймаут 100 мс

    if (tcsetattr(fd, TCSANOW, &tty) != 0) return -1;

    // Зниження затримки ядра Linux
    struct serial_struct ser_info;
    if (ioctl(fd, TIOCGSERIAL, &ser_info) == 0) {
        ser_info.flags |= ASYNC_LOW_LATENCY;
        ioctl(fd, TIOCSSERIAL, &ser_info);
    }
    return 0;
}

static void* rx_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[512];
    mavlink_message_t msg;
    mavlink_status_t status;

    while (b->running) {
        ssize_t n = read(b->fd, buf, sizeof(buf));
        if (n > 0) {
            for (ssize_t i = 0; i < n; ++i) {
                if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)) {
                    if (msg.msgid == MAVLINK_MSG_ID_ATTITUDE) {
                        mavlink_attitude_t att;
                        mavlink_msg_attitude_decode(&msg, &att);
                        b->current_yaw = att.yaw;
                    }
                }
            }
        }
    }
    return NULL;
}

static void* hb_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_message_t msg;

    while (b->running) {
        mavlink_msg_heartbeat_pack(SYSTEM_ID, COMPONENT_ID, &msg,
                                   MAV_TYPE_ONBOARD_CONTROLLER,
                                   MAV_AUTOPILOT_INVALID,
                                   MAV_MODE_FLAG_SAFETY_ARMED,
                                   0, MAV_STATE_ACTIVE);
        uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
        write(b->fd, buf, len);
        sleep(1);
    }
    return NULL;
}

static void* tx_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_message_t msg;

    // Маска керування вектором швидкості (Vx=1.0 м/с вперед, Vy=0, Vz=0)
    // Ігнорувати позицію та прискорення: (1<<0)|(1<<1)|(1<<2)|(1<<6)|(1<<7)|(1<<8) = 0x01C7
    uint16_t type_mask = 0x01C7;

    while (b->running) {
        mavlink_msg_set_position_target_local_ned_pack(
            SYSTEM_ID, COMPONENT_ID, &msg,
            0, 1, 1, MAV_FRAME_LOCAL_NED,
            type_mask,
            0.0f, 0.0f, 0.0f,       // X, Y, Z (ігноруються)
            1.0f, 0.0f, 0.0f,       // Vx = 1.0 м/с, Vy = 0, Vz = 0
            0.0f, 0.0f, 0.0f,       // Ax, Ay, Az (ігноруються)
            0.0f, 0.0f              // Yaw, Yaw_Rate
        );
        uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
        write(b->fd, buf, len);
        usleep(50000); // 20 Гц (50 мс)
    }
    return NULL;
}

int main(void) {
    int fd = open(SERIAL_PORT, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        perror("Не вдалося відкрити послідовний порт");
        return 1;
    }

    if (configure_serial(fd) != 0) {
        perror("Помилка конфігурації termios");
        close(fd);
        return 1;
    }

    companion_bridge_t bridge = {.fd = fd, .running = true, .current_yaw = 0.0f};

    pthread_create(&bridge.rx_thread, NULL, rx_worker, &bridge);
    pthread_create(&bridge.hb_thread, NULL, hb_worker, &bridge);
    pthread_create(&bridge.tx_thread, NULL, tx_worker, &bridge);

    printf("Companion Bridge запущено. Натисніть Enter для зупинки...\n");
    getchar();

    bridge.running = false;
    pthread_join(bridge.rx_thread, NULL);
    pthread_join(bridge.hb_thread, NULL);
    pthread_join(bridge.tx_thread, NULL);

    close(fd);
    printf("Companion Bridge коректно зупинено.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <atomic>
#include <thread>
#include <chrono>
#include <span>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <linux/serial.h>
#include <mavlink.h>

class SerialPort {
public:
    explicit SerialPort(std::string_view path, speed_t baud = B921600) {
        fd_ = ::open(path.data(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити порт");
        }
        configure(baud);
    }

    ~SerialPort() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;
    SerialPort(SerialPort&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SerialPort& operator=(SerialPort&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] ssize_t read(std::span<uint8_t> buffer) const {
        return ::read(fd_, buffer.data(), buffer.size());
    }

    [[nodiscard]] ssize_t write(std::span<const uint8_t> data) const {
        return ::write(fd_, data.data(), data.size());
    }

private:
    int fd_{-1};

    void configure(speed_t baud) const {
        termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            throw std::system_error(errno, std::generic_category(), "tcgetattr error");
        }

        ::cfsetospeed(&tty, baud);
        ::cfsetispeed(&tty, baud);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
        tty.c_cflag |= (CLOCAL | CREAD | CRTSCTS);
        tty.c_cflag &= ~(PARENB | PARODD | CSTOPB);

        tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF | IXANY);
        tty.c_oflag &= ~(OPOST | ONLCR);
        tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 1;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            throw std::system_error(errno, std::generic_category(), "tcsetattr error");
        }

        serial_struct ser_info{};
        if (::ioctl(fd_, TIOCGSERIAL, &ser_info) == 0) {
            ser_info.flags |= ASYNC_LOW_LATENCY;
            ::ioctl(fd_, TIOCSSERIAL, &ser_info);
        }
    }
};

class CompanionBridge {
public:
    explicit CompanionBridge(std::string_view port_path)
        : port_(port_path) {}

    void start() {
        running_.store(true, std::memory_order_release);

        rx_thread_ = std::jthread([this](std::stop_token st) { rx_loop(st); });
        hb_thread_ = std::jthread([this](std::stop_token st) { hb_loop(st); });
        tx_thread_ = std::jthread([this](std::stop_token st) { tx_loop(st); });
    }

    void stop() {
        running_.store(false, std::memory_order_release);
        if (rx_thread_.joinable()) rx_thread_.request_stop();
        if (hb_thread_.joinable()) hb_thread_.request_stop();
        if (tx_thread_.joinable()) tx_thread_.request_stop();
    }

    [[nodiscard]] float get_yaw() const noexcept {
        return yaw_.load(std::memory_order_relaxed);
    }

private:
    static constexpr uint8_t SYSTEM_ID = 1;
    static constexpr uint8_t COMPONENT_ID = MAV_COMP_ID_ONBOARD_COMPUTER;

    SerialPort port_;
    std::atomic<bool> running_{false};
    std::atomic<float> yaw_{0.0f};

    std::jthread rx_thread_;
    std::jthread hb_thread_;
    std::jthread tx_thread_;

    void rx_loop(std::stop_token st) {
        std::array<uint8_t, 512> rx_buf{};
        mavlink_message_t msg{};
        mavlink_status_t status{};

        while (!st.stop_requested() && running_.load(std::memory_order_relaxed)) {
            ssize_t bytes_read = port_.read(rx_buf);
            if (bytes_read > 0) {
                for (ssize_t i = 0; i < bytes_read; ++i) {
                    if (mavlink_parse_char(MAVLINK_COMM_0, rx_buf[i], &msg, &status)) {
                        if (msg.msgid == MAVLINK_MSG_ID_ATTITUDE) {
                            mavlink_attitude_t att{};
                            mavlink_msg_attitude_decode(&msg, &att);
                            yaw_.store(att.yaw, std::memory_order_relaxed);
                        }
                    }
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }

    void hb_loop(std::stop_token st) {
        std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> tx_buf{};
        mavlink_message_t msg{};

        while (!st.stop_requested() && running_.load(std::memory_order_relaxed)) {
            mavlink_msg_heartbeat_pack(
                SYSTEM_ID, COMPONENT_ID, &msg,
                MAV_TYPE_ONBOARD_CONTROLLER,
                MAV_AUTOPILOT_INVALID,
                MAV_MODE_FLAG_SAFETY_ARMED,
                0, MAV_STATE_ACTIVE
            );
            uint16_t len = mavlink_msg_to_send_buffer(tx_buf.data(), &msg);
            port_.write(std::span<const uint8_t>(tx_buf.data(), len));

            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    void tx_loop(std::stop_token st) {
        std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> tx_buf{};
        mavlink_message_t msg{};
        constexpr uint16_t type_mask = 0x01C7; // Керування вектором швидкості (Vx, Vy, Vz)

        while (!st.stop_requested() && running_.load(std::memory_order_relaxed)) {
            auto next_time = std::chrono::steady_clock::now() + std::chrono::milliseconds(50);

            mavlink_msg_set_position_target_local_ned_pack(
                SYSTEM_ID, COMPONENT_ID, &msg,
                0, 1, 1, MAV_FRAME_LOCAL_NED,
                type_mask,
                0.0f, 0.0f, 0.0f, // X, Y, Z (ігноруються)
                1.0f, 0.0f, 0.0f, // Vx = 1.0 м/с вперед, Vy = 0, Vz = 0
                0.0f, 0.0f, 0.0f, // Ax, Ay, Az (ігноруються)
                0.0f, 0.0f        // Yaw, Yaw_Rate
            );
            uint16_t len = mavlink_msg_to_send_buffer(tx_buf.data(), &msg);
            port_.write(std::span<const uint8_t>(tx_buf.data(), len));

            std::this_thread::sleep_until(next_time); // Рівно 20 Гц
        }
    }
};

int main() {
    try {
        CompanionBridge bridge("/dev/ttyAMA0");
        bridge.start();

        std::cout << "C++20 Companion Bridge активний. Натисніть Enter для виходу...\n";
        std::cin.get();

        bridge.stop();
        std::cout << "Міст успішно завершив роботу.\n";
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

### Реалізація моста на Python (asyncio + pymavlink)

Для швидкого прототипування автономних алгоритмів та інтеграції з бібліотеками комп'ютерного зору (OpenCV, PyTorch) застосовують асинхронний міст на базі модуля `asyncio` та бібліотеки `pymavlink`:

```py
import asyncio
from pymavlink import mavutil

class AsyncCompanionBridge:
    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 921600):
        self.port = port
        self.baud = baud
        self.master = None
        self.running = False
        self.current_yaw = 0.0

    async def connect(self):
        # Відкриття MAVLink з'єднання через послідовний порт
        self.master = mavutil.mavlink_connection(
            self.port,
            baud=self.baud,
            autoreconnect=True,
            source_system=1,
            source_component=mavutil.mavlink.MAV_COMP_ID_ONBOARD_COMPUTER
        )
        self.running = True
        print(f"З'єднання з {self.port} на {self.baud} бод встановлено.")

    async def rx_loop(self):
        loop = asyncio.get_running_loop()
        while self.running:
            # Читання без блокування основного Event Loop
            msg = await loop.run_in_executor(
                None, self.master.recv_match, False, 0.05
            )
            if msg is not None:
                msg_type = msg.get_type()
                if msg_type == "ATTITUDE":
                    self.current_yaw = msg.yaw
                elif msg_type == "STATUSTEXT":
                    print(f"[FC Log]: {msg.text}")
            await asyncio.sleep(0.001)

    async def hb_loop(self):
        while self.running:
            self.master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED,
                0,
                mavutil.mavlink.MAV_STATE_ACTIVE
            )
            await asyncio.sleep(1.0) # 1 Гц

    async def tx_setpoint_loop(self):
        # Маска керування вектором швидкості (0x01C7)
        # Ігноруємо X, Y, Z, Ax, Ay, Az
        type_mask = (
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_X_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_Y_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_Z_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE |
            mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE
        )

        while self.running:
            # Уставка: швидкість 1.0 м/с вперед за віссю X (North)
            self.master.mav.set_position_target_local_ned_send(
                0,                               # time_boot_ms
                1,                               # target_system
                1,                               # target_component
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                type_mask,
                0.0, 0.0, 0.0,                   # x, y, z
                1.0, 0.0, 0.0,                   # vx, vy, vz (1 м/с вперед)
                0.0, 0.0, 0.0,                   # afx, afy, afz
                0.0, 0.0                         # yaw, yaw_rate
            )
            await asyncio.sleep(0.05) # Строго 20 Гц (50 мс)

    async def run(self):
        await self.connect()
        await asyncio.gather(
            self.rx_loop(),
            self.hb_loop(),
            self.tx_setpoint_loop()
        )

    def stop(self):
        self.running = False
        if self.master:
            self.master.close()


if __name__ == "__main__":
    bridge = AsyncCompanionBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        bridge.stop()
        print("Python Companion Bridge зупинено.")
```

---

### Діагностика каналу зв'язку в Linux

Перед запуском мостової програми роботу апаратного UART та ліній керування потоком перевіряють штатними утилітами Linux:

#### 1. Перевірка налаштувань порту за допомогою `stty`
```bash
# Перевірка поточної конфігурації
stty -F /dev/ttyAMA0 -a

# Ручне примусове встановлення швидкості та CTS/RTS
stty -F /dev/ttyAMA0 921600 crtscts cs8 -cstopb -parenb raw -echo
```

#### 2. Моніторинг апаратних помилок і лічильників ядра
Стан черг та апаратні помилки драйвера послідовного порту (переповнення FIFO, помилки кадрування) фіксуються в системній файловій системі `/proc`:

```bash
cat /proc/tty/driver/serial
# або для контролера PL011 на Raspberry Pi:
cat /proc/tty/driver/amba_pl011
```

У виводі звертають увагу на лічильники `oe` (Overrun Error — переповнення буфера через затримку обробки) та `fe` (Framing Error — невідповідність швидкості або відсутність стоп-біта). Значення `oe > 0` свідчить про те, що лінія CTS/RTS не під'єднана фізично або вимкнена в конфігурації `termios`.

---

### Інженерні пастки та їх подолання

Під час інтеграції супутнього комп'ютера з польотним контролером виникають класичні помилки, які призводять до відмов або непередбачуваної поведінки апарата:

#### 1. Спроба входу в режим Offboard до початку потоку уставок
У прошивці PX4 команда перемикання в режим `Offboard` (`MAV_CMD_DO_SET_MODE`) буде **відхилена з помилкою NACK**, якщо польотний контролер не отримує регулярного потоку уставок протягом щонайменше однієї секунди *до* моменту надсилання команди.

*Правильний алгоритм активації:*
1. Запустити потік генерації `SET_POSITION_TARGET_LOCAL_NED` із частотою 20 Гц.
2. Зачекати щонайменше 1000 мс (переконатися, що автопілот стабільно прийняв понад 20 пакетів).
3. Надіслати команду перемикання польотного режиму на `Offboard` (PX4) або `Guided` (ArduPilot).
4. Надіслати команду розблокування моторів (arming, `MAV_CMD_COMPONENT_ARM_DISARM`).

#### 2. Блокування потоку передачі важкими розрахунками
Якщо алгоритм детекції нейромережі (YOLO) або обробки хмари точок лідара виконується в тому самому потоці, що й генерація уставок MAVLink, затримка інференсу на 100–150 мілісекунд призведе до спрацьовування таймера втрати зв'язку (Setpoint Timeout) на контролері. Автопілот миттєво скине режим Offboard у Hold/Loiter.

*Правильне рішення:* повністю відокремлювати контур комп'ютерного зору від контуру відправлення MAVLink. Потік передачі уставок повинен прокидатися за власним точним таймером `std::this_thread::sleep_until()` або корутиною `asyncio.sleep()`, транслюючи останнє розраховане валідне значення швидкості, навіть якщо новий відеокадр ще перебуває на стадії обробки нейромережею.

#### 3. Помилка інверсії бітів у `type_mask`
У протоколі MAVLink логіка бітів `type_mask` повідомлення `SET_POSITION_TARGET_LOCAL_NED` є **інверсною**: встановлений біт `1` означає «ігнорувати це поле» (Ignore), а біт `0` — «керувати цим полем». Якщо розробник записує `1` у біт швидкості `Vx`, вважаючи, що вмикає керування швидкістю, польотний контролер повністю проігнорує швидкість і спробує відпрацювати координати `(x=0, y=0, z=0)`, що призведе до різкого ривка дрона в бік точки старту.

#### 4. Методика перевірки відмовостійкості (Failsafe Verification Protocol)
Перед першим автономним польотом на відкритому полі обов'язково проводять стендовий тест на реакцію автопілота при аварійному зависанні супутнього комп'ютера:
1. Запустити симуляцію (SITL) або під'єднати реальний борт на стенді без пропелерів.
2. Перевести апарат у режим Offboard та переконатися у прийомі уставок.
3. Примусово заморозити процес моста за допомогою сигналу зупинки Linux: `killall -STOP companion_bridge` (імітація повного підвисання процесу або дедлоку).
4. Зафіксувати в журналі польотного контролера перехід через 500 мс у режим `HOLD`, а через 3000 мс — ініціалізацію процедури повернення додому `RTL`.
5. Відновити процес командою `killall -CONT companion_bridge` і перевірити безпеку повторного входу в режим керування.
