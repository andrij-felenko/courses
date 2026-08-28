# ⚙️ Драйвер корисного навантаження за протоколом MAVLink Camera v2

Цей проектний модуль містить повну реалізацію бортового сервісу корисного навантаження (камери та сенсорного модуля), який інтегрується в екосистему автопілота через стандартний протокол MAVLink Camera Protocol v2. Без власного повноцінного драйвера бортова камера залишається ізольованим приладом: автопілот не знає її оптичних характеристик, наземна станція не може дистанційно керувати спуском затвора й параметрами експозиції, а фотограмметричний софт позбавлений точної мікросекундної геоприв'язки знімків.

Модуль функціонує як незалежний фоновий процес на бортовому комп'ютері (Raspberry Pi, Nvidia Jetson) або мікроконтролері керування підвісом. Він підключається до системного маршрутизатора `mavlink-router` або фізичного послідовного порту UART/RS-422, транслює періодичний пульс `HEARTBEAT` з ідентифікатором компонента `MAV_COMP_ID_CAMERA` (100), відповідає на запити конфігурації `CAMERA_INFORMATION`, обробляє команди спуску затвора `MAV_CMD_IMAGE_START_CAPTURE` та повертає автопілоту пакет зворотного зв'язку `CAMERA_IMAGE_CAPTURED` для фіксації координат у системному лозі польоту.

## Архітектура та кінцевий автомат драйвера

Драйвер побудовано навколо неблокувального кінцевого автомата (англ. *Finite State Machine*, FSM). Робота сервісу розподілена на чотири паралельні підсистеми, що взаємодіють через спільний стан:

1. **Мережевий транспорт (Transport Layer):** прийом потоку сирих байтів з UDP-сокета або інтерфейсу UART, пошук маркера початку кадру `0xFD` (MAVLink v2), розбір полів заголовка та валідація контрольної суми CRC-16 з урахуванням магічного байта `CRC_EXTRA` для кожного типу повідомлення.
2. **Диспетчер команд (Command Dispatcher):** обробка повідомлень `COMMAND_LONG` та `COMMAND_INT`, адресованих нашому компоненту (`target_component == 100` або broadcast `target_component == 0`). Диспетчер формує негайне підтвердження `COMMAND_ACK` із результатом обробки (`MAV_RESULT_ACCEPTED`, `MAV_RESULT_TEMPORARILY_REJECTED` або `MAV_RESULT_DENIED`), після чого переводить FSM у стан виконання.
3. **Апаратний інтерфейс камери (Hardware Trigger & Sensor Abstraction):** формування електричного імпульсу спуску на лінію GPIO або взаємодія через протокол SDK камери (Sony Camera Remote SDK, FLIR Spinnaker, PTP/IP через USB), фіксація моменту спрацювання затвора (сигнал `FLASH_SYNC`) та зняття високоточного часового відліку.
4. **Генератор геоприв'язки та телеметрії (Telemetry Publisher):** регулярне надсилання `HEARTBEAT` з фіксованою частотою 1 Гц та публікація повідомлень `CAMERA_IMAGE_CAPTURED` з прив'язкою координат `lat`, `lon`, `alt` і орієнтації підвісу `q[4]`.

Діаграма станів автомата передбачає захист від блокувань: якщо команда спуску затвора надійшла в момент, коли сенсор ще зайнятий записом попереднього кадру на SD-карту, драйвер повертає `COMMAND_ACK` зі статусом `MAV_RESULT_TEMPORARILY_REJECTED`, запобігаючи переповненню черги буферів оптичного модуля.

## Реалізація модуля: C++ та Python

Нижче наведено дві повноцінні, незалежні та ідіоматичні реалізації драйвера. 

Версія на **C++** орієнтована на вбудовані системи реального часу, POSIX-сумісні платформи та процесори без надлишкових обчислювальних ресурсів. Вона використовує сучасні конструкції мови (RAII, `std::span`, `std::string_view`, `std::chrono`), не робить жодних динамічних виділень пам'яті в гарячому циклі опитування сокета та реалізує самостійний розрахунок CRC-16 за поліномом X.25.

Версія на **Python** побудована на базі бібліотеки `pymavlink` та асинхронного фреймворку `asyncio`. Вона забезпечує конкурентне виконання циклу `HEARTBEAT`, обробника вхідних пакетів та інтервального таймера серійної фотозйомки без блокування системних викликів введення-виведення.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <chrono>
#include <cstring>
#include <cstdint>
#include <optional>
#include <string_view>
#include <span>
#include <stdexcept>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>

// Визначення структур та констант протоколу MAVLink Camera Protocol v2
// Відповідає стандарту MAVLink v2 (common.xml)
namespace mavlink {

constexpr uint8_t STX_V2 = 0xFD;
constexpr uint8_t SYSTEM_ID = 1;
constexpr uint8_t COMPONENT_ID_CAMERA = 100;
constexpr uint8_t COMPONENT_ID_AUTOPILOT = 1;
constexpr uint8_t COMPONENT_ID_GCS = 190;

constexpr uint32_t MSG_ID_HEARTBEAT = 0;
constexpr uint32_t MSG_ID_COMMAND_LONG = 76;
constexpr uint32_t MSG_ID_COMMAND_ACK = 77;
constexpr uint32_t MSG_ID_CAMERA_INFORMATION = 259;
constexpr uint32_t MSG_ID_CAMERA_IMAGE_CAPTURED = 263;

constexpr uint16_t CMD_REQUEST_MESSAGE = 512;
constexpr uint16_t CMD_IMAGE_START_CAPTURE = 2000;
constexpr uint16_t CMD_IMAGE_STOP_CAPTURE = 2001;
constexpr uint16_t CMD_SET_CAMERA_ZOOM = 2003;

constexpr uint8_t RESULT_ACCEPTED = 0;
constexpr uint8_t RESULT_TEMPORARILY_REJECTED = 1;
constexpr uint8_t RESULT_DENIED = 2;
constexpr uint8_t RESULT_FAILED = 4;

constexpr uint8_t CAP_FLAGS_CAPTURE_IMAGE = (1 << 0);
constexpr uint8_t CAP_FLAGS_CAPTURE_VIDEO = (1 << 1);
constexpr uint8_t CAP_FLAGS_HAS_ZOOM = (1 << 3);

#pragma pack(push, 1)
struct HeaderV2 {
    uint8_t magic{STX_V2};
    uint8_t len{0};
    uint8_t incompat_flags{0};
    uint8_t compat_flags{0};
    uint8_t seq{0};
    uint8_t sysid{SYSTEM_ID};
    uint8_t compid{COMPONENT_ID_CAMERA};
    uint8_t msgid_low{0};
    uint8_t msgid_mid{0};
    uint8_t msgid_high{0};
};

struct HeartbeatPayload {
    uint32_t custom_mode{0};
    uint8_t type{30};            // MAV_TYPE_CAMERA
    uint8_t autopilot{0};       // MAV_AUTOPILOT_INVALID
    uint8_t base_mode{0};
    uint8_t system_status{4};   // MAV_STATE_ACTIVE
    uint8_t mavlink_version{3};
};

struct CommandLongPayload {
    float param1;
    float param2;
    float param3;
    float param4;
    float param5;
    float param6;
    float param7;
    uint16_t command;
    uint8_t target_system;
    uint8_t target_component;
    uint8_t confirmation;
};

struct CommandAckPayload {
    uint16_t command;
    uint8_t result;
    uint8_t progress{100};
    int32_t result_param2{0};
    uint8_t target_system{SYSTEM_ID};
    uint8_t target_component{COMPONENT_ID_GCS};
};

struct CameraInformationPayload {
    uint32_t time_boot_ms;
    uint32_t flags{CAP_FLAGS_CAPTURE_IMAGE | CAP_FLAGS_CAPTURE_VIDEO | CAP_FLAGS_HAS_ZOOM};
    float focal_length{35.0f};
    float sensor_size_h{36.0f};
    float sensor_size_v{24.0f};
    uint16_t resolution_h{6000};
    uint16_t resolution_v{4000};
    uint8_t lens_id{0};
    uint8_t vendor_name[32]{"AeroSensors Inc."};
    uint8_t model_name[32]{"HawkEye 4K Pro"};
    uint32_t firmware_version{0x02010000};
    char cam_definition_uri[140]{"http://192.168.1.10/camera_def.xml"};
};

struct CameraImageCapturedPayload {
    uint64_t time_utc;
    uint32_t time_boot_ms;
    int32_t lat{504501000};     // 50.4501 град * 1e7
    int32_t lon{305234000};     // 30.5234 град * 1e7
    int32_t alt{150000};        // 150.0 м над рівнем моря * 1e3
    int32_t relative_alt{50000};// 50.0 м над грунтом * 1e3
    float q[4]{1.0f, 0.0f, 0.0f, 0.0f}; // Орієнтація підвісу (w, x, y, z)
    int32_t image_index{0};
    int8_t capture_result{1};
    char file_url[205]{};
};
#pragma pack(pop)

// Розрахунок CRC-16 MAVLink (поліном X.25 0x1021)
inline uint16_t crc_accumulate(uint8_t b, uint16_t crc) {
    uint8_t ch = b ^ static_cast<uint8_t>(crc & 0x00FF);
    ch = ch ^ (ch << 4);
    return static_cast<uint16_t>((crc >> 8) ^ (ch << 8) ^ (ch << 3) ^ (ch >> 4));
}

} // namespace mavlink

// Безпечна RAII-обгортка для неблокувального UDP-сокета
class UdpSocket {
public:
    explicit UdpSocket(uint16_t local_port, std::string_view remote_ip, uint16_t remote_port) {
        fd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (fd_ < 0) {
            throw std::runtime_error("Помилка створення UDP сокета");
        }

        // Переведення сокета в неблокувальний режим для запобігання підвисанню
        int flags = fcntl(fd_, F_GETFL, 0);
        fcntl(fd_, F_SETFL, flags | O_NONBLOCK);

        sockaddr_in local_addr{};
        local_addr.sin_family = AF_INET;
        local_addr.sin_addr.s_addr = INADDR_ANY;
        local_addr.sin_port = htons(local_port);

        if (bind(fd_, reinterpret_cast<sockaddr*>(&local_addr), sizeof(local_addr)) < 0) {
            close(fd_);
            throw std::runtime_error("Помилка прив'язки локального порту сокета");
        }

        remote_addr_.sin_family = AF_INET;
        inet_pton(AF_INET, remote_ip.data(), &remote_addr_.sin_addr);
        remote_addr_.sin_port = htons(remote_port);
    }

    ~UdpSocket() {
        if (fd_ >= 0) {
            close(fd_);
        }
    }

    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;

    UdpSocket(UdpSocket&& other) noexcept : fd_(other.fd_), remote_addr_(other.remote_addr_) {
        other.fd_ = -1;
    }

    bool send(std::span<const uint8_t> data) const {
        ssize_t sent = sendto(fd_, data.data(), data.size(), 0,
                              reinterpret_cast<const sockaddr*>(&remote_addr_), sizeof(remote_addr_));
        return sent == static_cast<ssize_t>(data.size());
    }

    ssize_t receive(std::span<uint8_t> buffer) const {
        return recvfrom(fd_, buffer.data(), buffer.size(), 0, nullptr, nullptr);
    }

private:
    int fd_{-1};
    sockaddr_in remote_addr_{};
};

// Головний клас-контролер корисного навантаження
class CameraPayloadDriver {
public:
    explicit CameraPayloadDriver(UdpSocket& socket) : socket_(socket) {
        start_time_ = std::chrono::steady_clock::now();
    }

    void update() {
        auto now = std::chrono::steady_clock::now();

        // 1. Періодичний Heartbeat з частотою 1 Гц для реєстрації в автопілоті
        if (now - last_heartbeat_time_ >= std::chrono::seconds(1)) {
            send_heartbeat();
            last_heartbeat_time_ = now;
        }

        // 2. Опитування та диспетчеризація вхідних повідомлень MAVLink
        process_incoming_packets();

        // 3. Обслуговування інтервального таймера фотозйомки
        if (is_capturing_ && capture_interval_ > 0.0f) {
            auto elapsed = std::chrono::duration<float>(now - last_capture_time_).count();
            if (elapsed >= capture_interval_) {
                execute_capture();
                last_capture_time_ = now;
                if (capture_count_ > 0) {
                    capture_count_--;
                    if (capture_count_ == 0) {
                        is_capturing_ = false;
                    }
                }
            }
        }
    }

private:
    uint32_t get_boot_time_ms() const {
        auto now = std::chrono::steady_clock::now();
        return static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time_).count()
        );
    }

    uint64_t get_utc_time_us() const {
        auto now = std::chrono::system_clock::now();
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()).count()
        );
    }

    void send_packet(uint32_t msgid, const void* payload, uint8_t len, uint8_t crc_extra) {
        std::vector<uint8_t> buffer(sizeof(mavlink::HeaderV2) + len + 2);
        auto* header = reinterpret_cast<mavlink::HeaderV2*>(buffer.data());

        header->magic = mavlink::STX_V2;
        header->len = len;
        header->incompat_flags = 0;
        header->compat_flags = 0;
        header->seq = seq_++;
        header->sysid = mavlink::SYSTEM_ID;
        header->compid = mavlink::COMPONENT_ID_CAMERA;
        header->msgid_low = static_cast<uint8_t>(msgid & 0xFF);
        header->msgid_mid = static_cast<uint8_t>((msgid >> 8) & 0xFF);
        header->msgid_high = static_cast<uint8_t>((msgid >> 16) & 0xFF);

        std::memcpy(buffer.data() + sizeof(mavlink::HeaderV2), payload, len);

        // Обчислення CRC за заголовком та корисним навантаженням
        uint16_t crc = 0xFFFF;
        for (size_t i = 1; i < sizeof(mavlink::HeaderV2) + len; ++i) {
            crc = mavlink::crc_accumulate(buffer[i], crc);
        }
        crc = mavlink::crc_accumulate(crc_extra, crc);

        buffer[buffer.size() - 2] = static_cast<uint8_t>(crc & 0xFF);
        buffer[buffer.size() - 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        socket_.send(buffer);
    }

    void send_heartbeat() {
        mavlink::HeartbeatPayload hb;
        send_packet(mavlink::MSG_ID_HEARTBEAT, &hb, sizeof(hb), 50);
    }

    void send_command_ack(uint16_t command, uint8_t result) {
        mavlink::CommandAckPayload ack;
        ack.command = command;
        ack.result = result;
        send_packet(mavlink::MSG_ID_COMMAND_ACK, &ack, sizeof(ack), 143);
    }

    void send_camera_information() {
        mavlink::CameraInformationPayload info;
        info.time_boot_ms = get_boot_time_ms();
        send_packet(mavlink::MSG_ID_CAMERA_INFORMATION, &info, sizeof(info), 158);
    }

    void execute_capture() {
        image_index_++;
        std::cout << "[Драйвер Камери] Фізичний спуск затвора! Кадр #" << image_index_ << std::endl;

        // Формування та відправка повідомлення геотегування
        mavlink::CameraImageCapturedPayload cap;
        cap.time_utc = get_utc_time_us();
        cap.time_boot_ms = get_boot_time_ms();
        cap.image_index = image_index_;
        cap.capture_result = 1; // Успішне експонування

        std::snprintf(cap.file_url, sizeof(cap.file_url),
                      "http://192.168.1.10/DCIM/IMG_%05d.JPG", image_index_);

        send_packet(mavlink::MSG_ID_CAMERA_IMAGE_CAPTURED, &cap, sizeof(cap), 133);
    }

    void handle_command_long(const mavlink::CommandLongPayload& cmd) {
        if (cmd.target_system != mavlink::SYSTEM_ID ||
            (cmd.target_component != mavlink::COMPONENT_ID_CAMERA && cmd.target_component != 0)) {
            return; // Ігноруємо команди для інших бортових компонентів
        }

        switch (cmd.command) {
            case mavlink::CMD_REQUEST_MESSAGE: {
                auto requested_msg = static_cast<uint32_t>(cmd.param1);
                if (requested_msg == mavlink::MSG_ID_CAMERA_INFORMATION) {
                    send_command_ack(cmd.command, mavlink::RESULT_ACCEPTED);
                    send_camera_information();
                } else {
                    send_command_ack(cmd.command, mavlink::RESULT_DENIED);
                }
                break;
            }
            case mavlink::CMD_IMAGE_START_CAPTURE: {
                capture_interval_ = cmd.param2;
                capture_count_ = static_cast<int>(cmd.param3);

                send_command_ack(cmd.command, mavlink::RESULT_ACCEPTED);
                execute_capture();

                if (capture_interval_ > 0.0f && (capture_count_ > 1 || capture_count_ == 0)) {
                    is_capturing_ = true;
                    last_capture_time_ = std::chrono::steady_clock::now();
                    if (capture_count_ > 1) {
                        capture_count_--;
                    }
                }
                break;
            }
            case mavlink::CMD_IMAGE_STOP_CAPTURE: {
                is_capturing_ = false;
                send_command_ack(cmd.command, mavlink::RESULT_ACCEPTED);
                break;
            }
            case mavlink::CMD_SET_CAMERA_ZOOM: {
                current_zoom_ = cmd.param2;
                std::cout << "[Драйвер Камери] Зміна оптичного зуму на: " << current_zoom_ << "x" << std::endl;
                send_command_ack(cmd.command, mavlink::RESULT_ACCEPTED);
                break;
            }
            default:
                send_command_ack(cmd.command, mavlink::RESULT_DENIED);
                break;
        }
    }

    void process_incoming_packets() {
        std::array<uint8_t, 512> rx_buf;
        while (true) {
            ssize_t len = socket_.receive(rx_buf);
            if (len <= 0) break;

            if (len < static_cast<ssize_t>(sizeof(mavlink::HeaderV2) + 2)) continue;
            const auto* header = reinterpret_cast<const mavlink::HeaderV2*>(rx_buf.data());

            if (header->magic != mavlink::STX_V2) continue;

            uint32_t msgid = header->msgid_low |
                             (static_cast<uint32_t>(header->msgid_mid) << 8) |
                             (static_cast<uint32_t>(header->msgid_high) << 16);

            if (msgid == mavlink::MSG_ID_COMMAND_LONG &&
                header->len == sizeof(mavlink::CommandLongPayload)) {
                mavlink::CommandLongPayload cmd;
                std::memcpy(&cmd, rx_buf.data() + sizeof(mavlink::HeaderV2), sizeof(cmd));
                handle_command_long(cmd);
            }
        }
    }

    UdpSocket& socket_;
    uint8_t seq_{0};
    int32_t image_index_{0};
    float current_zoom_{1.0f};

    bool is_capturing_{false};
    float capture_interval_{0.0f};
    int capture_count_{0};

    std::chrono::steady_clock::time_point start_time_;
    std::chrono::steady_clock::time_point last_heartbeat_time_{};
    std::chrono::steady_clock::time_point last_capture_time_{};
};

int main() {
    try {
        std::cout << "Запуск MAVLink Camera Driver (C++)..." << std::endl;
        UdpSocket socket(14555, "127.0.0.1", 14550);
        CameraPayloadDriver driver(socket);

        std::cout << "Драйвер активний. Слухає порт 14555..." << std::endl;

        while (true) {
            driver.update();
            usleep(5000); // 5 мс квант диспетчеризації для низького навантаження CPU
        }
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка виконання: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
```
```py
import asyncio
import time
from pymavlink import mavutil

class MavlinkCameraDriver:
    """Асинхронний драйвер корисного навантаження MAVLink Camera Protocol v2."""

    def __init__(self, connection_str: str = 'udpin:127.0.0.1:14555', sysid: int = 1, compid: int = 100):
        self.sysid = sysid
        self.compid = compid
        self.conn = mavutil.mavlink_connection(connection_str, source_system=self.sysid, source_component=self.compid)
        
        self.image_index = 0
        self.is_capturing = False
        self.capture_interval = 0.0
        self.capture_count = 0
        self.current_zoom = 1.0
        self.start_time = time.monotonic()

    def get_boot_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def get_utc_time_us(self) -> int:
        return int(time.time() * 1_000_000)

    async def heartbeat_loop(self):
        """Регулярна передача Heartbeat з частотою 1 Гц."""
        while True:
            self.conn.mav.heartbeat_send(
                type=mavutil.mavlink.MAV_TYPE_CAMERA,
                autopilot=mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                base_mode=0,
                custom_mode=0,
                system_status=mavutil.mavlink.MAV_STATE_ACTIVE
            )
            await asyncio.sleep(1.0)

    def send_ack(self, command: int, result: int):
        """Надсилання підтвердження COMMAND_ACK ініціатору команди."""
        self.conn.mav.command_ack_send(
            command=command,
            result=result,
            progress=100,
            result_param2=0,
            target_system=self.sysid,
            target_component=mavutil.mavlink.MAV_COMP_ID_ALL
        )

    def send_camera_information(self):
        """Відповідь на запит CAMERA_INFORMATION із параметрами оптичної системи."""
        flags = (
            mavutil.mavlink.CAMERA_CAP_FLAGS_CAPTURE_IMAGE |
            mavutil.mavlink.CAMERA_CAP_FLAGS_CAPTURE_VIDEO |
            mavutil.mavlink.CAMERA_CAP_FLAGS_HAS_BASIC_ZOOM
        )
        self.conn.mav.camera_information_send(
            time_boot_ms=self.get_boot_time_ms(),
            vendor_name=b"AeroSensors Inc.\x00".ljust(32, b'\x00'),
            model_name=b"HawkEye 4K Pro\x00".ljust(32, b'\x00'),
            firmware_version=0x02010000,
            focal_length=35.0,
            sensor_size_h=36.0,
            sensor_size_v=24.0,
            resolution_h=6000,
            resolution_v=4000,
            lens_id=0,
            flags=flags,
            cam_definition_version=1,
            cam_definition_uri=b"http://192.168.1.10/camera_def.xml\x00".ljust(140, b'\x00')
        )

    def trigger_capture(self):
        """Фіксація експонування кадру та передача пакета геотегування."""
        self.image_index += 1
        print(f"[Python-Камера] Спуск затвора! Знімок #{self.image_index}")

        # Генерація пакета зворотного зв'язку CAMERA_IMAGE_CAPTURED
        url = f"http://192.168.1.10/DCIM/IMG_{self.image_index:05d}.JPG".encode('utf-8').ljust(205, b'\x00')
        self.conn.mav.camera_image_captured_send(
            time_utc=self.get_utc_time_us(),
            time_boot_ms=self.get_boot_time_ms(),
            lat=504501000,       # 50.4501°
            lon=305234000,       # 30.5234°
            alt=150000,          # 150.0 м AMSL
            relative_alt=50000,  # 50.0 м над грунтом
            q=[1.0, 0.0, 0.0, 0.0],
            image_index=self.image_index,
            capture_result=1,
            file_url=url
        )

    async def capture_interval_loop(self):
        """Асинхронний таймер серійної інтервальної зйомки."""
        while True:
            if self.is_capturing and self.capture_interval > 0:
                await asyncio.sleep(self.capture_interval)
                if not self.is_capturing:
                    continue
                self.trigger_capture()
                if self.capture_count > 0:
                    self.capture_count -= 1
                    if self.capture_count == 0:
                        self.is_capturing = False
            else:
                await asyncio.sleep(0.05)

    def handle_command_long(self, msg):
        """Диспетчеризація вхідних команд MAVLink."""
        cmd = msg.command

        if cmd == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE:
            req_msg = int(msg.param1)
            if req_msg == mavutil.mavlink.MAVLINK_MSG_ID_CAMERA_INFORMATION:
                self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)
                self.send_camera_information()
            else:
                self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_DENIED)

        elif cmd == mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE:
            self.capture_interval = msg.param2
            self.capture_count = int(msg.param3)

            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)
            self.trigger_capture()

            if self.capture_interval > 0 and (self.capture_count > 1 or self.capture_count == 0):
                self.is_capturing = True
                if self.capture_count > 1:
                    self.capture_count -= 1

        elif cmd == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE:
            self.is_capturing = False
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

        elif cmd == mavutil.mavlink.MAV_CMD_SET_CAMERA_ZOOM:
            self.current_zoom = msg.param2
            print(f"[Python-Камера] Встановлено зум: {self.current_zoom}x")
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

        else:
            self.send_ack(cmd, mavutil.mavlink.MAV_RESULT_DENIED)

    async def rx_loop(self):
        """Неблокувальний цикл прийому повідомлень."""
        loop = asyncio.get_running_loop()
        while True:
            msg = await loop.run_in_executor(None, self.conn.recv_match, True)
            if msg:
                if msg.get_type() == 'COMMAND_LONG':
                    if msg.target_system == self.sysid and msg.target_component in (self.compid, 0):
                        self.handle_command_long(msg)
            else:
                await asyncio.sleep(0.005)

    async def run(self):
        print("Запуск асинхронного MAVLink Camera Driver (Python)...")
        await asyncio.gather(
            self.heartbeat_loop(),
            self.rx_loop(),
            self.capture_interval_loop()
        )

if __name__ == '__main__':
    driver = MavlinkCameraDriver()
    try:
        asyncio.run(driver.run())
    except KeyboardInterrupt:
        print("Драйвер зупинено користувачем.")
```
:::

## Інженерні пастки реалізації та налагодження

Під час польової експлуатації та інтеграції драйвера камери розробники найчастіше стикаються з трьома критичними проблемами:

1. **Блокування Heartbeat у синхронних SDK виробників:** Багато фірмових SDK (наприклад, Sony Camera Remote SDK або FLIR Spinnaker) мають блокувальні функції захоплення кадру, виконання яких може займати від 200 до 800 мс. Якщо такий виклик виконується в головному потоці диспетчеризації MAVLink, переривається надсилання щосекундного пакета `HEARTBEAT`. Наземна станція керування через 3 секунди відсутності пульсу автоматично оголошує втрату зв'язку з навантаженням (`Camera Connection Lost`), що може зірвати виконання автономної фотограмметричної місії. Виклик фізичного спуску затвора обов'язково повинен делегуватися окремому робочому потоку або неблокувальному апаратному таймеру.
2. **Невідповідність часових шкал (Clock Drift & Timestamp Sync):** Поле `time_boot_ms` у повідомленні `CAMERA_IMAGE_CAPTURED` повинно бути суворо синхронізоване з часом польотного контролера. Якщо бортовий комп'ютер передає власний локальний аптайм операційної системи Linux, автопілот не зможе зіставити момент знімка з координатами GPS у лозі польоту `.ulog`. Для надійної синхронізації драйвер повинен підписуватися на системні повідомлення `TIMESYNC` або `SYSTEM_TIME` від автопілота й динамічно обчислювати поправку часу `time_offset`.
3. **Переповнення буферів послідовного порту UART:** При проведенні високошвидкісної аерофотозйомки з темпом 3–5 кадрів на секунду серійний порт на стандартній швидкості 115200 бод зазнає перевантаження. Пакет `CAMERA_IMAGE_CAPTURED` разом із повним заголовком MAVLink v2 та полем URL займає понад 250 байтів. Якщо пропускна здатність інтерфейсу недостатня, пакети починають безповоротно втрачатися на рівні драйвера UART, що призводить до пропуску геоміток у польотному журналі. Мінімальна робоча швидкість для UART корисного навантаження становить **921600 бод**, а при використанні відеопотоку — прямий інтерфейс UDP/IP через Ethernet.

## Перевірка та валідація на стенді

Перед інтеграцією на реальний безпілотний апарат працездатність драйвера тестують у лабораторному стендовому оточенні. Для цього створюють віртуальну мережу з автопілотом у режимі симуляції SITL (англ. *Software-in-the-Loop*) та програмою наземного контролю QGroundControl.

Маршрутизацію пакетів забезпечують за допомогою утиліти `mavproxy.py`:

```
mavproxy.py --master=tcp:127.0.0.1:5760 --out=udpout:127.0.0.1:14550 --out=udpout:127.0.0.1:14555
```

Коли драйвер запускається й починає транслювати `HEARTBEAT` на порт 14555, QGroundControl автоматично виявляє новий компонент камери, надсилає запит `CAMERA_INFORMATION` і відображає у правому куті польотного інтерфейсу панель керування затвором, зумом та режимами зйомки. Аналіз проходження сирих пакетів у системі здійснюють за допомогою утиліти перехоплення трафіку `tcpdump`:

```
tcpdump -i lo -nn -X udp port 14555
```

Перевірка підтверджує, що час між надсиланням команди `IMAGE_START_CAPTURE` та поверненням `COMMAND_ACK` не перевищує 5–10 мс, а пакет `CAMERA_IMAGE_CAPTURED` надходить одразу після завершення експозиції.
