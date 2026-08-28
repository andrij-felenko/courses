#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <mutex>
#include <optional>
#include <span>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/timerfd.h>
#include <pthread.h>
#include <common/mavlink.h>

struct VelocityCommand {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};
    float yaw{0.0f};
};

class SerialPort {
public:
    explicit SerialPort(std::string_view port_name, speed_t baud) {
        fd_ = ::open(port_name.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити послідовний порт");
        }

        termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка зчитування атрибутів termios");
        }

        ::cfmakeraw(&tty);
        ::cfsetispeed(&tty, baud);
        ::cfsetospeed(&tty, baud);
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~CRTSCTS;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка застосування налаштувань порту");
        }
    }

    ~SerialPort() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    void write(std::span<const uint8_t> data) const {
        if (fd_ >= 0 && !data.empty()) {
            ::write(fd_, data.data(), data.size());
        }
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

class OffboardStreamer {
public:
    enum class State {
        Idle,
        PreStreaming,
        RequestMode,
        ActiveStreaming,
        HoldFallback
    };

    OffboardStreamer(std::string_view port, uint8_t sys_id = 240, uint8_t comp_id = 1)
        : port_(port, B921600), sys_id_(sys_id), comp_id_(comp_id) {
        timer_fd_ = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
        if (timer_fd_ < 0) {
            throw std::runtime_error("Помилка створення дескриптора timerfd");
        }
    }

    ~OffboardStreamer() noexcept {
        stop();
        if (timer_fd_ >= 0) {
            ::close(timer_fd_);
        }
    }

    void start() {
        running_.store(true, std::memory_order_release);
        state_ = State::PreStreaming;
        prestream_counter_ = 0;

        worker_thread_ = std::jthread([this](std::stop_token st) {
            set_realtime_priority();
            run_loop(st);
        });
    }

    void stop() {
        running_.store(false, std::memory_order_release);
        if (worker_thread_.joinable()) {
            worker_thread_.request_stop();
        }
    }

    void update_target(const VelocityCommand& cmd) {
        std::lock_guard lock(target_mutex_);
        target_ = cmd;
        last_target_time_ = std::chrono::steady_clock::now();
    }

private:
    void set_realtime_priority() {
        sched_param param{};
        param.sched_priority = 45; // Пріоритет реального часу для Linux RT
        pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
    }

    void send_velocity_target(const VelocityCommand& cmd) {
        mavlink_set_position_target_local_ned_t sp{};
        sp.target_system = 1;
        sp.target_component = MAV_COMP_ID_AUTOPILOT1;
        sp.coordinate_frame = MAV_FRAME_LOCAL_NED;
        // Маска: активні лише швидкості та кут yaw
        sp.type_mask = 0x0001 | 0x0002 | 0x0004 | 0x0040 | 0x0080 | 0x0100 | 0x0800;
        sp.vx = cmd.vx;
        sp.vy = cmd.vy;
        sp.vz = cmd.vz;
        sp.yaw = cmd.yaw;

        mavlink_message_t msg{};
        mavlink_msg_set_position_target_local_ned_encode(sys_id_, comp_id_, &msg, &sp);

        uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
        port_.write(std::span<const uint8_t>(buffer, len));
    }

    void send_offboard_request() {
        mavlink_command_long_t cmd{};
        cmd.target_system = 1;
        cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
        cmd.command = MAV_CMD_DO_SET_MODE;
        cmd.param1 = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
        cmd.param2 = 6.0f; // PX4 OFFBOARD

        mavlink_message_t msg{};
        mavlink_msg_command_long_encode(sys_id_, comp_id_, &msg, &cmd);

        uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
        port_.write(std::span<const uint8_t>(buffer, len));
    }

    void run_loop(std::stop_token st) {
        itimerspec period{};
        period.it_interval.tv_nsec = 50'000'000; // 20 Гц (50 мс)
        period.it_value = period.it_interval;
        ::timerfd_settime(timer_fd_, 0, &period, nullptr);

        while (!st.stop_requested() && running_.load(std::memory_order_acquire)) {
            uint64_t expirations = 0;
            if (::read(timer_fd_, &expirations, sizeof(expirations)) <= 0) {
                continue;
            }

            VelocityCommand active_cmd{};
            bool is_fresh = false;
            {
                std::lock_guard lock(target_mutex_);
                auto age = std::chrono::steady_clock::now() - last_target_time_;
                if (age <= std::chrono::milliseconds(250)) {
                    active_cmd = target_;
                    is_fresh = true;
                }
            }

            switch (state_) {
            case State::Idle:
                break;
            case State::PreStreaming:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                if (++prestream_counter_ >= 16) {
                    state_ = State::RequestMode;
                }
                break;
            case State::RequestMode:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                send_offboard_request();
                state_ = State::ActiveStreaming;
                break;
            case State::ActiveStreaming:
                if (!is_fresh) {
                    state_ = State::HoldFallback;
                    send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                } else {
                    send_velocity_target(active_cmd);
                }
                break;
            case State::HoldFallback:
                send_velocity_target(VelocityCommand{0.0f, 0.0f, 0.0f, active_cmd.yaw});
                if (is_fresh) {
                    state_ = State::ActiveStreaming;
                }
                break;
            }
        }
    }

    SerialPort port_;
    int timer_fd_{-1};
    uint8_t sys_id_{240};
    uint8_t comp_id_{1};
    std::atomic<bool> running_{false};
    State state_{State::Idle};
    size_t prestream_counter_{0};

    std::mutex target_mutex_;
    VelocityCommand target_{};
    std::chrono::steady_clock::time_point last_target_time_{};
    std::jthread worker_thread_;
};
