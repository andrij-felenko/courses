#include <iostream>
#include <chrono>
#include <optional>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>

enum class FrameType : uint8_t {
    Data = 0x01,
    Ping = 0x02,
    Pong = 0x03
};

class HeartbeatTracker {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    HeartbeatTracker(int socket_fd, std::chrono::seconds interval, std::chrono::seconds timeout)
        : fd_(socket_fd), ping_interval_(interval), pong_timeout_(timeout), last_rx_time_(Clock::now()) {}

    void on_frame_received(FrameType type) {
        last_rx_time_ = Clock::now();
        if (type == FrameType::Pong) {
            ping_pending_ = false;
        } else if (type == FrameType::Ping) {
            send_frame(FrameType::Pong);
        }
    }

    [[nodiscard]] bool tick() {
        const auto now = Clock::now();

        if (ping_pending_) {
            if (now - ping_sent_time_ >= pong_timeout_) {
                // Сервер не відповів на PONG у межах дозволеного вікна
                return false;
            }
        } else {
            if (now - last_rx_time_ >= ping_interval_) {
                if (send_frame(FrameType::Ping)) {
                    ping_pending_ = true;
                    ping_sent_time_ = now;
                } else {
                    return false;
                }
            }
        }
        return true;
    }

private:
    bool send_frame(FrameType type) {
        const auto byte = static_cast<uint8_t>(type);
        const ::ssize_t ret = ::send(fd_, &byte, sizeof(byte), MSG_NOSIGNAL);
        return ret == sizeof(byte);
    }

    int fd_;
    std::chrono::seconds ping_interval_;
    std::chrono::seconds pong_timeout_;
    TimePoint last_rx_time_;
    TimePoint ping_sent_time_{};
    bool ping_pending_{false};
};
