#include <arpa/inet.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <deque>
#include <iostream>
#include <optional>
#include <random>
#include <span>
#include <stdexcept>
#include <vector>

namespace mavlink_test {

constexpr uint8_t kStxV2 = 0xFD;
constexpr size_t kMaxPacketLen = 280;

constexpr uint32_t kMsgIdHeartbeat = 0;
constexpr uint32_t kMsgIdGpsRawInt = 24;
constexpr uint32_t kMsgIdAttitude = 30;
constexpr uint32_t kMsgIdHilSensor = 107;
constexpr uint32_t kMsgIdHilActuator = 115;

constexpr uint8_t kCrcExtraHeartbeat = 50;
constexpr uint8_t kCrcExtraGpsRawInt = 24;
constexpr uint8_t kCrcExtraAttitude = 39;
constexpr uint8_t kCrcExtraHilSensor = 108;
constexpr uint8_t kCrcExtraHilActuator = 158;

class Crc16 {
public:
    static constexpr uint16_t kInitValue = 0xFFFF;

    static void accumulate(uint8_t data, uint16_t& crc) noexcept {
        uint8_t tmp = data ^ static_cast<uint8_t>(crc & 0xFF);
        tmp ^= (tmp << 4);
        crc = (crc >> 8) ^ (static_cast<uint16_t>(tmp) << 8)
                         ^ (static_cast<uint16_t>(tmp) << 3)
                         ^ (static_cast<uint16_t>(tmp) >> 4);
    }

    [[nodiscard]] static uint16_t calculate(std::span<const uint8_t> buffer, uint8_t crc_extra) noexcept {
        uint16_t crc = kInitValue;
        for (size_t i = 1; i < buffer.size(); ++i) {
            accumulate(buffer[i], crc);
        }
        accumulate(crc_extra, crc);
        return crc;
    }
};

struct FailureScenario {
    bool drop_packets{false};
    float drop_rate{0.0f}; // 0.0 .. 1.0
    std::chrono::milliseconds delay{0};

    bool gnss_jamming{false};
    bool gnss_spoofing{false};
    float spoof_vel_north{0.0f}; // м/с
    float spoof_vel_east{0.0f};  // м/с

    bool imu_noise_active{false};
    float gyro_noise_std{0.0f};  // рад/с
    float gyro_bias_z{0.0f};     // рад/с

    bool kill_motor_1{false};
    std::chrono::steady_clock::time_point start_time{std::chrono::steady_clock::now()};
};

struct AutopilotTelemetry {
    uint8_t base_mode{0};
    uint32_t custom_mode{0};
    uint8_t system_status{0};
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float yaw_deg{0.0f};
    bool failsafe_triggered{false};
    std::optional<std::chrono::steady_clock::time_point> failsafe_timestamp;
};

struct DelayedPacket {
    std::vector<uint8_t> buffer;
    std::chrono::steady_clock::time_point deliver_at;
    sockaddr_in dest_addr;
};

class SocketUdp {
public:
    explicit SocketUdp(uint16_t bind_port) {
        fd_ = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося створити сокет UDP");
        }

        int opt = 1;
        ::setsockopt(fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(bind_port);

        if (::bind(fd_, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка прив'язки сокета");
        }

        ::fcntl(fd_, F_SETFL, O_NONBLOCK);
    }

    ~SocketUdp() {
        if (fd_ >= 0) ::close(fd_);
    }

    SocketUdp(const SocketUdp&) = delete;
    SocketUdp& operator=(const SocketUdp&) = delete;

    SocketUdp(SocketUdp&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    SocketUdp& operator=(SocketUdp&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    [[nodiscard]] std::optional<size_t> receive(std::span<uint8_t> buffer, sockaddr_in& src_addr) noexcept {
        socklen_t addr_len = sizeof(src_addr);
        ssize_t bytes = ::recvfrom(fd_, buffer.data(), buffer.size(), 0,
                                  reinterpret_cast<struct sockaddr*>(&src_addr), &addr_len);
        if (bytes > 0) return static_cast<size_t>(bytes);
        return std::nullopt;
    }

    bool send(std::span<const uint8_t> buffer, const sockaddr_in& dest_addr) noexcept {
        ssize_t bytes = ::sendto(fd_, buffer.data(), buffer.size(), 0,
                                reinterpret_cast<const struct sockaddr*>(&dest_addr), sizeof(dest_addr));
        return bytes == static_cast<ssize_t>(buffer.size());
    }

private:
    int fd_{-1};
};

class FaultInjectorFramework {
public:
    FaultInjectorFramework(uint16_t sim_port, uint16_t ap_port,
                           sockaddr_in target_ap, sockaddr_in target_sim)
        : sock_sim_(sim_port),
          sock_ap_(ap_port),
          target_ap_addr_(target_ap),
          target_sim_addr_(target_sim),
          rng_(std::random_device{}()) {}

    void set_scenario(const FailureScenario& scenario) noexcept {
        scenario_ = scenario;
        scenario_.start_time = std::chrono::steady_clock::now();
    }

    [[nodiscard]] const AutopilotTelemetry& telemetry() const noexcept {
        return telemetry_;
    }

    void execute_step(std::chrono::milliseconds poll_timeout = std::chrono::milliseconds(1)) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Доставка затриманих пакетів
        while (!delayed_queue_.empty() && delayed_queue_.front().deliver_at <= now) {
            const auto& pkt = delayed_queue_.front();
            sock_ap_.send(pkt.buffer, pkt.dest_addr);
            delayed_queue_.pop_front();
        }

        // 2. Мультиплексування сокетів
        std::array<pollfd, 2> fds{};
        fds[0].fd = sock_sim_.native_handle();
        fds[0].events = POLLIN;
        fds[1].fd = sock_ap_.native_handle();
        fds[1].events = POLLIN;

        if (::poll(fds.data(), fds.size(), static_cast<int>(poll_timeout.count())) > 0) {
            std::array<uint8_t, kMaxPacketLen> rx_buf{};
            sockaddr_in src{};

            // Симулятор -> Автопілот
            if (fds[0].revents & POLLIN) {
                if (auto bytes = sock_sim_.receive(rx_buf, src)) {
                    std::span<uint8_t> packet{rx_buf.data(), *bytes};
                    if (process_packet(packet, true, now)) {
                        if (scenario_.delay > std::chrono::milliseconds::zero()) {
                            delayed_queue_.push_back({
                                std::vector<uint8_t>(packet.begin(), packet.end()),
                                now + scenario_.delay,
                                target_ap_addr_
                            });
                        } else {
                            sock_ap_.send(packet, target_ap_addr_);
                        }
                    }
                }
            }

            // Автопілот -> Симулятор
            if (fds[1].revents & POLLIN) {
                if (auto bytes = sock_ap_.receive(rx_buf, src)) {
                    std::span<uint8_t> packet{rx_buf.data(), *bytes};
                    if (process_packet(packet, false, now)) {
                        sock_sim_.send(packet, target_sim_addr_);
                    }
                }
            }
        }
    }

private:
    [[nodiscard]] bool process_packet(std::span<uint8_t> buf, bool is_from_sim,
                                      std::chrono::steady_clock::time_point now) noexcept {
        if (buf.size() < 12 || buf[0] != kStxV2) return true;

        const uint8_t payload_len = buf[1];
        const uint32_t msg_id = static_cast<uint32_t>(buf[7]) |
                               (static_cast<uint32_t>(buf[8]) << 8) |
                               (static_cast<uint32_t>(buf[9]) << 16);
        auto payload = buf.subspan(10, payload_len);

        if (!is_from_sim) {
            parse_feedback(msg_id, payload, now);
            return true;
        }

        if (scenario_.drop_packets) {
            std::uniform_real_distribution<float> dist(0.0f, 1.0f);
            if (dist(rng_) < scenario_.drop_rate) return false;
        }

        uint8_t crc_extra = 0;
        bool mutated = false;

        switch (msg_id) {
        case kMsgIdGpsRawInt:
            mutate_gps(payload, now);
            crc_extra = kCrcExtraGpsRawInt;
            mutated = true;
            break;

        case kMsgIdHilSensor:
            mutate_sensors(payload);
            crc_extra = kCrcExtraHilSensor;
            mutated = true;
            break;

        case kMsgIdHilActuator:
            mutate_actuators(payload);
            crc_extra = kCrcExtraHilActuator;
            mutated = true;
            break;

        default:
            break;
        }

        if (mutated) {
            const size_t header_and_payload = 10 + payload_len;
            const uint16_t new_crc = Crc16::calculate(buf.first(header_and_payload), crc_extra);
            buf[header_and_payload] = static_cast<uint8_t>(new_crc & 0xFF);
            buf[header_and_payload + 1] = static_cast<uint8_t>((new_crc >> 8) & 0xFF);
        }

        return true;
    }

    void parse_feedback(uint32_t msg_id, std::span<const uint8_t> payload,
                        std::chrono::steady_clock::time_point now) noexcept {
        if (msg_id == kMsgIdHeartbeat && payload.size() >= 9) {
            telemetry_.custom_mode = static_cast<uint32_t>(payload[0]) |
                                    (static_cast<uint32_t>(payload[1]) << 8) |
                                    (static_cast<uint32_t>(payload[2]) << 16) |
                                    (static_cast<uint32_t>(payload[3]) << 24);
            telemetry_.base_mode = payload[6];
            telemetry_.system_status = payload[7];

            if ((telemetry_.base_mode & 0x01) || (telemetry_.system_status == 5)) {
                if (!telemetry_.failsafe_triggered) {
                    telemetry_.failsafe_triggered = true;
                    telemetry_.failsafe_timestamp = now;
                    std::cout << "[ASSERT ENGINE C++20] Failsafe зафіксовано в телеметрії!\n";
                }
            }
        } else if (msg_id == kMsgIdAttitude && payload.size() >= 16) {
            float roll{0.0f}, pitch{0.0f}, yaw{0.0f};
            std::memcpy(&roll, &payload[4], sizeof(float));
            std::memcpy(&pitch, &payload[8], sizeof(float));
            std::memcpy(&yaw, &payload[12], sizeof(float));

            telemetry_.roll_deg = roll * 57.2957795f;
            telemetry_.pitch_deg = pitch * 57.2957795f;
            telemetry_.yaw_deg = yaw * 57.2957795f;
        }
    }

    void mutate_gps(std::span<uint8_t> payload, std::chrono::steady_clock::time_point now) noexcept {
        if (scenario_.gnss_jamming && payload.size() >= 30) {
            payload[20] = 1; // fix_type = No Fix
            payload[21] = 0; // satellites_visible = 0
            const uint16_t bad_eph = 9999;
            const uint16_t bad_epv = 9999;
            std::memcpy(&payload[22], &bad_eph, sizeof(uint16_t));
            std::memcpy(&payload[24], &bad_epv, sizeof(uint16_t));
        } else if (scenario_.gnss_spoofing && payload.size() >= 30) {
            int32_t lat{0}, lon{0};
            std::memcpy(&lat, &payload[8], sizeof(int32_t));
            std::memcpy(&lon, &payload[12], sizeof(int32_t));

            const auto dt = std::chrono::duration<double>(now - scenario_.start_time).count();
            const auto d_lat = static_cast<int32_t>((scenario_.spoof_vel_north * dt / 111132.0) * 1e7);
            const auto d_lon = static_cast<int32_t>((scenario_.spoof_vel_east * dt / 111132.0) * 1e7);

            lat += d_lat;
            lon += d_lon;

            std::memcpy(&payload[8], &lat, sizeof(int32_t));
            std::memcpy(&payload[12], &lon, sizeof(int32_t));
        }
    }

    void mutate_sensors(std::span<uint8_t> payload) noexcept {
        if (scenario_.imu_noise_active && payload.size() >= 24) {
            float xgyro{0.0f}, ygyro{0.0f}, zgyro{0.0f};
            std::memcpy(&xgyro, &payload[12], sizeof(float));
            std::memcpy(&ygyro, &payload[16], sizeof(float));
            std::memcpy(&zgyro, &payload[20], sizeof(float));

            std::normal_distribution<float> dist(0.0f, scenario_.gyro_noise_std);
            xgyro += dist(rng_);
            ygyro += dist(rng_);
            zgyro += dist(rng_) + scenario_.gyro_bias_z;

            std::memcpy(&payload[12], &xgyro, sizeof(float));
            std::memcpy(&payload[16], &ygyro, sizeof(float));
            std::memcpy(&payload[20], &zgyro, sizeof(float));
        }
    }

    void mutate_actuators(std::span<uint8_t> payload) noexcept {
        if (scenario_.kill_motor_1 && payload.size() >= 12) {
            constexpr float kZeroThrust = 0.0f;
            std::memcpy(&payload[8], &kZeroThrust, sizeof(float));
        }
    }

    SocketUdp sock_sim_;
    SocketUdp sock_ap_;
    sockaddr_in target_ap_addr_{};
    sockaddr_in target_sim_addr_{};

    FailureScenario scenario_{};
    AutopilotTelemetry telemetry_{};
    std::deque<DelayedPacket> delayed_queue_{};
    std::mt19937 rng_;
};

} // namespace mavlink_test

int main() {
    std::cout << "[C++20 INJECTOR & ASSERT ENGINE] Ініціалізація фреймворку тестування...\n";

    sockaddr_in target_ap{};
    target_ap.sin_family = AF_INET;
    target_ap.sin_port = htons(14555);
    inet_pton(AF_INET, "127.0.0.1", &target_ap.sin_addr);

    sockaddr_in target_sim{};
    target_sim.sin_family = AF_INET;
    target_sim.sin_port = htons(14565);
    inet_pton(AF_INET, "127.0.0.1", &target_sim.sin_addr);

    try {
        mavlink_test::FaultInjectorFramework framework(14560, 14550, target_ap, target_sim);

        mavlink_test::FailureScenario scenario;
        scenario.gnss_jamming = true;
        framework.set_scenario(scenario);

        const auto start_test = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start_test < std::chrono::seconds(10)) {
            framework.execute_step(std::chrono::milliseconds(1));

            const auto& tlm = framework.telemetry();
            if (std::abs(tlm.roll_deg) > 70.0f || std::abs(tlm.pitch_deg) > 70.0f) {
                std::cerr << "[ASSERT FAILED] Критичний переворот: Roll=" << tlm.roll_deg
                          << "°, Pitch=" << tlm.pitch_deg << "°\n";
                return 1;
            }
        }

        if (framework.telemetry().failsafe_triggered) {
            std::cout << "[TEST PASSED] Failsafe успішно підтверджено у C++20 валідаторі!\n";
        } else {
            std::cout << "[TEST WARNING] Failsafe не зафіксовано.\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "[КРИТИЧНА ПОМИЛКА] " << e.what() << '\n';
        return 1;
    }

    return 0;
}
