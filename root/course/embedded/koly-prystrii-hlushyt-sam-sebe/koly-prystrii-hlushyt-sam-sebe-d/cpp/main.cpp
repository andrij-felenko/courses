#include <cstdint>
#include <cstddef>
#include <array>
#include <functional>
#include <atomic>
#include <span>
#include <string_view>

namespace embedded::rf {

enum class BusPriority : uint8_t {
    Low = 0,     // Дисплей, світлодіоди, фонові логи
    Medium,      // Flash QSPI, EEPROM
    High,        // Критичні сенсори зворотного зв'язку
    Critical     // Аварійні системи
};

enum class ArbiterState : uint8_t {
    Idle = 0,
    BusActive,
    RxQuietActive,
    TimeoutRecovery
};

class BusArbiter {
public:
    static constexpr size_t MaxDevices = 4;
    static constexpr uint32_t RxTimeoutTicks = 5000;

    struct Device {
        std::string_view              name;
        BusPriority                   priority{BusPriority::Low};
        std::function<void(bool pause)> control_cb{};
        bool                          is_paused{false};
    };

    BusArbiter() noexcept
        : state_(ArbiterState::Idle),
          device_count_(0),
          rx_start_tick_(0),
          quiet_window_count_(0),
          timeout_count_(0) {}

    bool register_device(std::string_view name, BusPriority priority,
                         std::function<void(bool pause)> control_cb) noexcept {
        if (device_count_ >= MaxDevices) {
            return false;
        }
        devices_[device_count_++] = Device{name, priority, std::move(control_cb), false};
        return true;
    }

    // Викликається з обробника переривання старту прийому радіопакета
    void on_radio_rx_start(uint32_t current_tick) noexcept {
        state_.store(ArbiterState::RxQuietActive, std::memory_order_release);
        rx_start_tick_ = current_tick;
        ++quiet_window_count_;

        for (size_t i = 0; i < device_count_; ++i) {
            auto &dev = devices_[i];
            if (dev.priority <= BusPriority::Medium && !dev.is_paused) {
                if (dev.control_cb) {
                    dev.control_cb(true); // Призупинити шину
                }
                dev.is_paused = true;
            }
        }
    }

    // Викликається після завершення прийому або помилки CRC
    void on_radio_rx_end() noexcept {
        if (state_.load(std::memory_order_acquire) != ArbiterState::RxQuietActive) {
            return;
        }

        for (size_t i = 0; i < device_count_; ++i) {
            auto &dev = devices_[i];
            if (dev.is_paused) {
                if (dev.control_cb) {
                    dev.control_cb(false); // Відновити роботу шини
                }
                dev.is_paused = false;
            }
        }
        state_.store(ArbiterState::Idle, std::memory_order_release);
    }

    // Сторожовий таймер для запобігання вічному блокуванню шин
    void poll_watchdog(uint32_t current_tick) noexcept {
        if (state_.load(std::memory_order_acquire) == ArbiterState::RxQuietActive) {
            if ((current_tick - rx_start_tick_) > RxTimeoutTicks) {
                ++timeout_count_;
                state_.store(ArbiterState::TimeoutRecovery, std::memory_order_release);
                on_radio_rx_end();
            }
        }
    }

    [[nodiscard]] ArbiterState state() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint32_t quiet_windows() const noexcept {
        return quiet_window_count_;
    }

    [[nodiscard]] uint32_t timeouts() const noexcept {
        return timeout_count_;
    }

private:
    std::atomic<ArbiterState> state_;
    std::array<Device, MaxDevices> devices_{};
    size_t                    device_count_;
    uint32_t                  rx_start_tick_;
    uint32_t                  quiet_window_count_;
    uint32_t                  timeout_count_;
};

// RAII-обгортка для автоматичного контролю вікна прийому в синхронних драйверах
class QuietWindowGuard {
public:
    explicit QuietWindowGuard(BusArbiter &arbiter, uint32_t tick) noexcept
        : arbiter_(arbiter) {
        arbiter_.on_radio_rx_start(tick);
    }

    ~QuietWindowGuard() noexcept {
        arbiter_.on_radio_rx_end();
    }

    QuietWindowGuard(const QuietWindowGuard &) = delete;
    QuietWindowGuard &operator=(const QuietWindowGuard &) = delete;

private:
    BusArbiter &arbiter_;
};

} // namespace embedded::rf
