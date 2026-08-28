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
