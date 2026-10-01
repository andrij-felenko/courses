#include "esp8266_at_gpio.hpp"
#include <iostream>
#include <sstream>

// ---------- UrcParser ----------

void UrcParser::feedChar(char c) {
    if (c == '\r') {
        return; // Ігноруємо символи повернення каретки
    }
    if (c == '\n') {
        if (!rxBuffer_.empty()) {
            processLine(rxBuffer_);
            rxBuffer_.clear();
        }
        return;
    }
    rxBuffer_ += c;
}

void UrcParser::processLine(std::string_view line) {
    if (line == "OK") {
        lastStatus_ = AtResponseStatus::Ok;
    } else if (line == "ERROR") {
        lastStatus_ = AtResponseStatus::Error;
    } else if (line.find("+GPIOINDB:") != std::string_view::npos) {
        parseUrc(line);
    }
}

void UrcParser::parseUrc(std::string_view line) {
    // Формат: +GPIOINDB:<pin>,<level>
    auto pos = line.find(':');
    if (pos == std::string_view::npos) return;

    std::string_view params = line.substr(pos + 1);
    auto comma = params.find(',');
    if (comma == std::string_view::npos) return;

    int pin = std::stoi(std::string(params.substr(0, comma)));
    int levelVal = std::stoi(std::string(params.substr(comma + 1)));

    if (urcCallback_) {
        urcCallback_(pin, static_cast<GpioLevel>(levelVal));
    }
}

AtResponseStatus UrcParser::popResponseStatus() {
    AtResponseStatus st = lastStatus_;
    lastStatus_ = AtResponseStatus::None;
    return st;
}

// ---------- Esp8266GpioDriver ----------

Esp8266GpioDriver::Esp8266GpioDriver(TxFunc txFunc)
    : txFunc_(std::move(txFunc)) {}

void Esp8266GpioDriver::feedRx(std::string_view data) {
    for (char c : data) {
        parser_.feedChar(c);
    }
}

bool Esp8266GpioDriver::setPinDirection(int pin, GpioMode mode) {
    if (isBusy()) return false;
    activePin_ = pin;
    targetMode_ = mode;
    state_ = DriverState::SendingSetDir;
    return true;
}

bool Esp8266GpioDriver::writePin(int pin, GpioLevel level) {
    if (isBusy()) return false;
    activePin_ = pin;
    targetLevel_ = level;
    state_ = DriverState::SendingWritePin;
    return true;
}

bool Esp8266GpioDriver::readPin(int pin) {
    if (isBusy()) return false;
    activePin_ = pin;
    state_ = DriverState::SendingReadPin;
    return true;
}

void Esp8266GpioDriver::tick(uint32_t currentMillis) {
    switch (state_) {
    case DriverState::Idle:
        break;

    case DriverState::SendingSetDir: {
        std::string cmd = "AT+SYSGPIODIR=" + std::to_string(activePin_) + "," +
                          std::to_string(static_cast<int>(targetMode_)) + "\r\n";
        txFunc_(cmd);
        commandStartMs_ = currentMillis;
        state_ = DriverState::WaitingSetDirResponse;
        break;
    }

    case DriverState::WaitingSetDirResponse: {
        AtResponseStatus st = parser_.popResponseStatus();
        if (st == AtResponseStatus::Ok) {
            std::cout << "[FSM] Напрямок GPIO" << activePin_ << " успішно встановлено.\n";
            state_ = DriverState::Idle;
        } else if (st == AtResponseStatus::Error || (currentMillis - commandStartMs_ > TIMEOUT_MS)) {
            std::cout << "[FSM] Помилка або таймаут встановлення напрямку GPIO" << activePin_ << "!\n";
            state_ = DriverState::Idle;
        }
        break;
    }

    case DriverState::SendingWritePin: {
        std::string cmd = "AT+SYSGPIOWR=" + std::to_string(activePin_) + "," +
                          std::to_string(static_cast<int>(targetLevel_)) + "\r\n";
        txFunc_(cmd);
        commandStartMs_ = currentMillis;
        state_ = DriverState::WaitingWritePinResponse;
        break;
    }

    case DriverState::WaitingWritePinResponse: {
        AtResponseStatus st = parser_.popResponseStatus();
        if (st == AtResponseStatus::Ok) {
            std::cout << "[FSM] Рівень GPIO" << activePin_ << " успішно записано.\n";
            state_ = DriverState::Idle;
        } else if (st == AtResponseStatus::Error || (currentMillis - commandStartMs_ > TIMEOUT_MS)) {
            std::cout << "[FSM] Помилка або таймаут запису GPIO" << activePin_ << "!\n";
            state_ = DriverState::Idle;
        }
        break;
    }

    case DriverState::SendingReadPin: {
        std::string cmd = "AT+SYSGPIORD=" + std::to_string(activePin_) + "\r\n";
        txFunc_(cmd);
        commandStartMs_ = currentMillis;
        state_ = DriverState::WaitingReadPinResponse;
        break;
    }

    case DriverState::WaitingReadPinResponse: {
        AtResponseStatus st = parser_.popResponseStatus();
        if (st == AtResponseStatus::Ok) {
            std::cout << "[FSM] Рівень GPIO" << activePin_ << " успішно прочитано.\n";
            state_ = DriverState::Idle;
        } else if (st == AtResponseStatus::Error || (currentMillis - commandStartMs_ > TIMEOUT_MS)) {
            std::cout << "[FSM] Помилка або таймаут читання GPIO" << activePin_ << "!\n";
            state_ = DriverState::Idle;
        }
        break;
    }
    }
}
