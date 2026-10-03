#include "esp8266_relay_driver.hpp"
#include <cstdio>
#include <cstring>

// --- Реалізація RelayPinGuard ---

RelayPinGuard::RelayPinGuard(Esp8266RelayDriver& driver, uint8_t pin, LogicLevel safe_level)
    : driver_(&driver), pin_(pin), safe_level_(safe_level), current_level_(safe_level), active_(true) {
}

RelayPinGuard::~RelayPinGuard() {
    if (active_ && driver_) {
        // Гарантовано повертаємо силовий вивід у безпечний стан при знищенні об'єкта
        driver_->writePin(pin_, safe_level_);
    }
}

RelayPinGuard::RelayPinGuard(RelayPinGuard&& other) noexcept
    : driver_(other.driver_),
      pin_(other.pin_),
      safe_level_(other.safe_level_),
      current_level_(other.current_level_),
      active_(other.active_) {
    other.active_ = false;
    other.driver_ = nullptr;
}

RelayPinGuard& RelayPinGuard::operator=(RelayPinGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && driver_) {
            driver_->writePin(pin_, safe_level_);
        }
        driver_ = other.driver_;
        pin_ = other.pin_;
        safe_level_ = other.safe_level_;
        current_level_ = other.current_level_;
        active_ = other.active_;

        other.active_ = false;
        other.driver_ = nullptr;
    }
    return *this;
}

DriverStatus RelayPinGuard::setState(LogicLevel level) {
    if (!active_ || !driver_) {
        return DriverStatus::HardwareError;
    }
    DriverStatus st = driver_->writePin(pin_, level);
    if (st == DriverStatus::Ok) {
        current_level_ = level;
    } else {
        // У разі помилки послідовного зв'язку скидаємо стан у безпечний
        driver_->writePin(pin_, safe_level_);
        current_level_ = safe_level_;
    }
    return st;
}

DriverStatus RelayPinGuard::toggle() {
    LogicLevel next = (current_level_ == LogicLevel::Low) ? LogicLevel::High : LogicLevel::Low;
    return setState(next);
}

// --- Реалізація Esp8266RelayDriver ---

Esp8266RelayDriver::Esp8266RelayDriver(UartRingBuffer<256>& rx_buffer,
                                       UartTxCallback tx_cb,
                                       GetTickMsFn tick_cb,
                                       DelayMsFn delay_cb)
    : rx_buffer_(rx_buffer), tx_cb_(tx_cb), tick_cb_(tick_cb), delay_cb_(delay_cb) {}

bool Esp8266RelayDriver::isStrappingPin(uint8_t pin) noexcept {
    // Вплив на режим завантаження ESP8266 мають виводи GPIO0, GPIO2 та GPIO15
    return (pin == 0 || pin == 2 || pin == 15);
}

DriverStatus Esp8266RelayDriver::initPin(uint8_t pin, GpioMode mode, LogicLevel initial_level) {
    if (pin > 16) {
        return DriverStatus::InvalidPin;
    }

    // Затримка ініціалізації для запобігання хибним спрацьовуванням під час переходів завантаження
    if (isStrappingPin(pin) && delay_cb_) {
        delay_cb_(300);
    }

    char cmd_buf[32];
    std::string_view mode_cmd = formatPinModeCmd(pin, mode, cmd_buf, sizeof(cmd_buf));
    DriverStatus st = sendAtCommand(mode_cmd, 1000);
    if (st != DriverStatus::Ok) {
        return st;
    }

    if (mode == GpioMode::Output) {
        std::string_view write_cmd = formatPinWriteCmd(pin, initial_level, cmd_buf, sizeof(cmd_buf));
        st = sendAtCommand(write_cmd, 1000);
    }

    return st;
}

DriverStatus Esp8266RelayDriver::writePin(uint8_t pin, LogicLevel level) {
    if (pin > 16) {
        return DriverStatus::InvalidPin;
    }

    char cmd_buf[32];
    std::string_view cmd = formatPinWriteCmd(pin, level, cmd_buf, sizeof(cmd_buf));
    return sendAtCommand(cmd, 1000);
}

DriverStatus Esp8266RelayDriver::readPin(uint8_t pin, LogicLevel& out_level) {
    if (pin > 16) {
        return DriverStatus::InvalidPin;
    }

    char cmd_buf[32];
    std::string_view cmd = formatPinReadCmd(pin, cmd_buf, sizeof(cmd_buf));

    rx_buffer_.clear();
    if (tx_cb_) {
        tx_cb_(cmd);
    } else {
        return DriverStatus::HardwareError;
    }

    if (!tick_cb_ || !delay_cb_) {
        return DriverStatus::HardwareError;
    }

    uint32_t start_tick = tick_cb_();
    constexpr uint32_t timeout_ms = 1000;

    char resp_buf[128];
    while ((tick_cb_() - start_tick) < timeout_ms) {
        if (rx_buffer_.find("OK\r\n") || rx_buffer_.find("OK")) {
            size_t len = rx_buffer_.peek_bytes(resp_buf, sizeof(resp_buf) - 1);
            resp_buf[len] = '\0';
            std::string_view response(resp_buf, len);

            if (parsePinReadResponse(response, pin, out_level)) {
                return DriverStatus::Ok;
            }
            return DriverStatus::ErrorResponse;
        }

        if (rx_buffer_.find("ERROR\r\n") || rx_buffer_.find("ERROR")) {
            return DriverStatus::ErrorResponse;
        }

        delay_cb_(2);
    }

    return DriverStatus::Timeout;
}

DriverStatus Esp8266RelayDriver::sendAtCommand(std::string_view cmd, uint32_t timeout_ms) {
    if (!tx_cb_ || !tick_cb_ || !delay_cb_) {
        return DriverStatus::HardwareError;
    }

    rx_buffer_.clear();
    tx_cb_(cmd);

    uint32_t start_tick = tick_cb_();
    while ((tick_cb_() - start_tick) < timeout_ms) {
        if (rx_buffer_.find("OK\r\n") || rx_buffer_.find("OK")) {
            return DriverStatus::Ok;
        }
        if (rx_buffer_.find("ERROR\r\n") || rx_buffer_.find("ERROR")) {
            return DriverStatus::ErrorResponse;
        }
        delay_cb_(2);
    }

    return DriverStatus::Timeout;
}

std::string_view Esp8266RelayDriver::formatPinModeCmd(uint8_t pin, GpioMode mode, char* buf, size_t buf_size) noexcept {
    if (!buf || buf_size < 20) return {};
    int len = std::snprintf(buf, buf_size, "AT+PINMODE=%u,%u\r\n", pin, static_cast<unsigned>(mode));
    if (len < 0 || static_cast<size_t>(len) >= buf_size) return {};
    return std::string_view(buf, static_cast<size_t>(len));
}

std::string_view Esp8266RelayDriver::formatPinWriteCmd(uint8_t pin, LogicLevel level, char* buf, size_t buf_size) noexcept {
    if (!buf || buf_size < 20) return {};
    int len = std::snprintf(buf, buf_size, "AT+PINWRITE=%u,%u\r\n", pin, static_cast<unsigned>(level));
    if (len < 0 || static_cast<size_t>(len) >= buf_size) return {};
    return std::string_view(buf, static_cast<size_t>(len));
}

std::string_view Esp8266RelayDriver::formatPinReadCmd(uint8_t pin, char* buf, size_t buf_size) noexcept {
    if (!buf || buf_size < 20) return {};
    int len = std::snprintf(buf, buf_size, "AT+PINREAD=%u\r\n", pin);
    if (len < 0 || static_cast<size_t>(len) >= buf_size) return {};
    return std::string_view(buf, static_cast<size_t>(len));
}

bool Esp8266RelayDriver::parsePinReadResponse(std::string_view response, uint8_t pin, LogicLevel& out_level) noexcept {
    size_t pos = response.find("+PINREAD:");
    if (pos == std::string_view::npos) {
        return false;
    }

    std::string_view data = response.substr(pos + 9);
    while (!data.empty() && data.front() == ' ') {
        data.remove_prefix(1);
    }

    unsigned parsed_pin = 0;
    size_t i = 0;
    while (i < data.size() && data[i] >= '0' && data[i] <= '9') {
        parsed_pin = parsed_pin * 10 + (data[i] - '0');
        ++i;
    }

    if (i == 0 || parsed_pin != pin || i >= data.size() || data[i] != ',') {
        return false;
    }

    data.remove_prefix(i + 1);

    if (data.empty()) {
        return false;
    }

    if (data.front() == '1') {
        out_level = LogicLevel::High;
        return true;
    } else if (data.front() == '0') {
        out_level = LogicLevel::Low;
        return true;
    }

    return false;
}
