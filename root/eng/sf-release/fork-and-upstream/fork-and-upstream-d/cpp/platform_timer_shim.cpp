// platform_timer_shim.cpp — Ідіоматичний C++ фасад із RAII та обробкою помилок
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <memory>

namespace product::bsp {

enum class HardwareError : uint8_t {
    InvalidConfiguration,
    InitializationFailed,
    BusBusy,
    Timeout
};

// Внутрішній C-інтерфейс операційної системи
struct NativeKernelTimerHandle {
    void* mmio_address{nullptr};
    uint32_t frequency_hz{0};
    uint32_t irq_flags{0};
};

extern "C" {
    int os_kernel_timer_configure(NativeKernelTimerHandle* h, uint32_t freq);
    void os_kernel_timer_release(NativeKernelTimerHandle* h);
}

class SystemTimerFacade final {
public:
    explicit SystemTimerFacade(uint32_t target_freq_hz) noexcept
        : target_frequency_{target_freq_hz} {}

    ~SystemTimerFacade() noexcept {
        if (active_) {
            os_kernel_timer_release(&native_handle_);
        }
    }

    // Заборона небезпечного копіювання ресурсу обладнання
    SystemTimerFacade(const SystemTimerFacade&) = delete;
    SystemTimerFacade& operator=(const SystemTimerFacade&) = delete;

    // Дозвіл безпечного переміщення (Move semantics)
    SystemTimerFacade(SystemTimerFacade&& other) noexcept
        : native_handle_{other.native_handle_},
          target_frequency_{other.target_frequency_},
          active_{other.active_} {
        other.active_ = false;
        other.native_handle_ = {};
    }

    SystemTimerFacade& operator=(SystemTimerFacade&& other) noexcept {
        if (this != &other) {
            if (active_) {
                os_kernel_timer_release(&native_handle_);
            }
            native_handle_ = other.native_handle_;
            target_frequency_ = other.target_frequency_;
            active_ = other.active_;
            other.active_ = false;
            other.native_handle_ = {};
        }
        return *this;
    }

    [[nodiscard]] std::expected<void, HardwareError> start() noexcept {
        if (target_frequency_ == 0) {
            return std::unexpected(HardwareError::InvalidConfiguration);
        }

        native_handle_.frequency_hz = target_frequency_;
        native_handle_.irq_flags = 0x01;

        const int ret = os_kernel_timer_configure(&native_handle_, target_frequency_);
        if (ret != 0) {
            return std::unexpected(HardwareError::InitializationFailed);
        }

        active_ = true;
        return {};
    }

    [[nodiscard]] bool is_running() const noexcept {
        return active_;
    }

    [[nodiscard]] uint32_t get_frequency() const noexcept {
        return target_frequency_;
    }

private:
    NativeKernelTimerHandle native_handle_{};
    uint32_t target_frequency_{0};
    bool active_{false};
};

} // namespace product::bsp
