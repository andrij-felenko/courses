#include <cstdint>
#include <functional>

enum class SS41FPole : uint8_t {
    Unknown = 0,
    South   = 1, // LOW level
    North   = 2  // HIGH level
};

enum class SS41FStatus : uint8_t {
    Ok = 0,
    InvalidArg,
    AlreadyInitialized,
    HardwareError
};

class SS41FDriver {
public:
    using EventCallback = std::function<void(SS41FPole pole, uint32_t timestamp_us)>;

    struct Config {
        uint16_t gpio_pin;
        void* gpio_port;
        uint32_t debounce_window_us;
        EventCallback callback;
    };

    SS41FDriver() = default;

    SS41FStatus init(const Config& config) {
        if (initialized_) {
            return SS41FStatus::AlreadyInitialized;
        }
        config_ = config;
        last_change_us_ = 0;
        event_count_ = 0;

        // Зчитування початкового стану та налаштування периферії
        current_pole_ = SS41FPole::South;
        initialized_ = true;
        return SS41FStatus::Ok;
    }

    SS41FPole getCurrentPole() const { return current_pole_; }
    uint32_t getEventCount() const { return event_count_; }

private:
    Config config_{};
    volatile SS41FPole current_pole_{SS41FPole::Unknown};
    volatile uint32_t last_change_us_{0};
    volatile uint32_t event_count_{0};
    bool initialized_{false};
};
