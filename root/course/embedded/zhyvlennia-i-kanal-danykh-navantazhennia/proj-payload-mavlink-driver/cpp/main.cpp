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
