#ifndef WATER_PUMP_CONTROLLER_H
#define WATER_PUMP_CONTROLLER_H

#include <chrono>
#include <cstdint>

// Абстракція апаратного ШІМ-каналу
class IPwmChannel {
public:
    virtual ~IPwmChannel() = default;
    virtual void setDutyCycle(uint8_t duty) = 0;
};

class WaterPumpController {
public:
    struct Config {
        std::chrono::milliseconds softStartDuration;
        std::chrono::milliseconds watchdogTimeout; // Час до вимкнення при сухому ході
        uint8_t minDutyCycle; // Мінімальний ШІМ для старту
        uint8_t maxDutyCycle; // Максимальний ШІМ
    };

    WaterPumpController(IPwmChannel& pwm, const Config& config);

    void start();
    void stop();
    void update(); // Неблокуючий метод, має викликатися в головному циклі
    void resetWatchdog(); // Сигнал, що помпа качає воду (наприклад, від датчика потоку)

    bool isFault() const;

private:
    IPwmChannel& pwmChannel_;
    Config config_;
    
    enum class State { Stopped, Starting, Running, Fault };
    State state_;

    std::chrono::steady_clock::time_point stateStartTime_;
    std::chrono::steady_clock::time_point lastWatchdogReset_;
};

#endif // WATER_PUMP_CONTROLLER_H
