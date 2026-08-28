/* modem_controller.cpp — Ідіоматична C++20 реалізація контролера з'єднання */
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <thread>
#include <format>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/select.h>

namespace cellular {

enum class ModemError {
    SerialIoError,
    Timeout,
    SimNotReady,
    RegistrationFailed,
    PdpActivationFailed,
    InvalidResponse
};

class SerialPort {
public:
    explicit SerialPort(std::string_view device_path) {
        fd_ = ::open(device_path.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    }

    ~SerialPort() {
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

    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    bool write_command(std::string_view command) const {
        if (fd_ < 0) return false;
        std::string payload = std::format("{}\r\n", command);
        ssize_t written = ::write(fd_, payload.data(), payload.size());
        return written == static_cast<ssize_t>(payload.size());
    }

    std::optional<std::string> read_response(std::chrono::milliseconds timeout) const {
        if (fd_ < 0) return std::nullopt;
        std::string buffer;
        buffer.resize(1024);
        size_t total_read = 0;
        auto remaining_time = timeout;

        while (remaining_time.count() > 0) {
            fd_set read_fds;
            FD_ZERO(&read_fds);
            FD_SET(fd_, &read_fds);

            struct timeval tv{};
            tv.tv_sec = std::chrono::duration_cast<std::chrono::seconds>(remaining_time).count();
            tv.tv_usec = (remaining_time.count() % 1000) * 1000;

            int res = ::select(fd_ + 1, &read_fds, nullptr, nullptr, &tv);
            if (res > 0 && FD_ISSET(fd_, &read_fds)) {
                ssize_t n = ::read(fd_, buffer.data() + total_read, buffer.size() - total_read - 1);
                if (n > 0) {
                    total_read += static_cast<size_t>(n);
                    std::string_view current_view(buffer.data(), total_read);
                    if (current_view.contains("\r\nOK\r\n") || current_view.contains("\r\nERROR\r\n") ||
                        current_view.contains("+CME ERROR:")) {
                        buffer.resize(total_read);
                        return buffer;
                    }
                }
            } else {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            remaining_time -= std::chrono::milliseconds(50);
        }
        return (total_read > 0) ? std::make_optional(buffer.substr(0, total_read)) : std::nullopt;
    }

private:
    int fd_{-1};
};

struct PdpSession {
    std::string ip_address;
    int cid{1};
    std::string apn;
};

class ModemController {
public:
    explicit ModemController(SerialPort port) : port_(std::move(port)) {}

    std::expected<PdpSession, ModemError> activate_data_session(std::string_view apn, std::string_view pdp_type = "IP") {
        if (!port_.is_open()) {
            return std::unexpected(ModemError::SerialIoError);
        }

        /* 1. Перевірка AT */
        if (!exec_command("AT", std::chrono::milliseconds(1000))) {
            return std::unexpected(ModemError::Timeout);
        }

        exec_command("AT+CMEE=1", std::chrono::milliseconds(1000));

        /* 2. Перевірка SIM */
        auto pin_resp = exec_command("AT+CPIN?", std::chrono::milliseconds(3000));
        if (!pin_resp || !pin_resp->contains("+CPIN: READY")) {
            return std::unexpected(ModemError::SimNotReady);
        }

        /* 3. Очікування реєстрації LTE */
        bool registered = false;
        for (int i = 0; i < 15; ++i) {
            auto reg_resp = exec_command("AT+CEREG?", std::chrono::milliseconds(2000));
            if (reg_resp && (reg_resp->contains(",1") || reg_resp->contains(",5"))) {
                registered = true;
                break;
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        if (!registered) {
            return std::unexpected(ModemError::RegistrationFailed);
        }

        /* 4. Задання PDP Context */
        std::string set_pdp_cmd = std::format("AT+CGDCONT=1,\"{}\",\"{}\"", pdp_type, apn);
        if (!exec_command(set_pdp_cmd, std::chrono::milliseconds(3000))) {
            return std::unexpected(ModemError::PdpActivationFailed);
        }

        /* 5. Активація Context */
        if (!exec_command("AT+CGACT=1,1", std::chrono::milliseconds(10000))) {
            return std::unexpected(ModemError::PdpActivationFailed);
        }

        /* 6. Зчитування IP */
        auto ip_resp = exec_command("AT+CGPADDR=1", std::chrono::milliseconds(3000));
        if (ip_resp) {
            std::string_view resp_view{*ip_resp};
            auto pos = resp_view.find("+CGPADDR: 1,\"");
            if (pos != std::string_view::npos) {
                auto start = pos + 13;
                auto end = resp_view.find('\"', start);
                if (end != std::string_view::npos) {
                    PdpSession session;
                    session.cid = 1;
                    session.apn = std::string(apn);
                    session.ip_address = std::string(resp_view.substr(start, end - start));
                    return session;
                }
            }
        }
        return std::unexpected(ModemError::InvalidResponse);
    }

private:
    std::optional<std::string> exec_command(std::string_view cmd, std::chrono::milliseconds timeout) {
        if (!port_.write_command(cmd)) {
            return std::nullopt;
        }
        auto resp = port_.read_response(timeout);
        if (resp && resp->contains("OK")) {
            return resp;
        }
        return std::nullopt;
    }

    SerialPort port_;
};

} // namespace cellular
