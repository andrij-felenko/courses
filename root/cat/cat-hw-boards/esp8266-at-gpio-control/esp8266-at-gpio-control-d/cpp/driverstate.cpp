#include <cstdint>
#include <cstring>
#include <cstdio>

enum class DriverState {
    Idle,
    WaitResponse,
    TimeoutRecovery
};

class Esp8266GpioDriver {
public:
    Esp8266GpioDriver() : state_(DriverState::Idle), timerMs_(0), timeoutLimitMs_(500) {}

    void parseLine(const char* line) {
        if (std::strncmp(line, "+GPIO_INT:", 10) == 0) {
            int pin = 0, level = 0;
            if (std::sscanf(line, "+GPIO_INT:%d,%d", &pin, &level) == 2) {
                onGpioInterrupt(pin, level);
            }
            return;
        }

        if (std::strcmp(line, "OK") == 0) {
            responseOk_ = true;
        } else if (std::strcmp(line, "ERROR") == 0) {
            responseError_ = true;
        }
    }

    void process(uint32_t deltaMs) {
        if (state_ == DriverState::WaitResponse) {
            timerMs_ += deltaMs;
            if (responseOk_) {
                state_ = DriverState::Idle;
            } else if (responseError_ || timerMs_ >= timeoutLimitMs_) {
                state_ = DriverState::TimeoutRecovery;
            }
        }
    }

private:
    void onGpioInterrupt(int pin, int level) {
        // Обробка події переривання від вхідного контакту
    }

    DriverState state_;
    uint32_t timerMs_;
    uint32_t timeoutLimitMs_;
    bool responseOk_{false};
    bool responseError_{false};
};
