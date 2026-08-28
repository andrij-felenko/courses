#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace power_audit {

// Апаратні адреси регістрів
inline constexpr std::uintptr_t kRccBase   = 0x40021000U;
inline constexpr std::uintptr_t kGpioaBase = 0x48000000U;
inline constexpr std::uintptr_t kPwrBase   = 0x40007000U;
inline constexpr std::uintptr_t kDwtCtrl   = 0xE0001000U;
inline constexpr std::uintptr_t kDwtCyccnt = 0xE0001004U;
inline constexpr std::uintptr_t kDemcr     = 0xE000EDFCU;

// Бітові маски ліній
inline constexpr std::uint32_t kPinMarkerCpu  = 1U << 0;
inline constexpr std::uint32_t kPinMarkerAnlg = 1U << 1;
inline constexpr std::uint32_t kPinLoadSwitch = 1U << 2;

inline constexpr std::uint32_t kRetentionMagic = 0x57414B45U; // "WAKE"
inline constexpr std::size_t   kHistoryDepth   = 64;

struct RetentionStorage {
    std::uint32_t boot_magic;
    std::uint32_t wake_counter;
    std::uint16_t adc_history[kHistoryDepth];
    std::uint32_t last_duration_cycles;
};

// Регістровий драйвер GPIO через BSRR
class FastMarkerPort {
public:
    static void set_cpu_active(bool active) noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        bsrr = active ? kPinMarkerCpu : (kPinMarkerCpu << 16);
    }

    static void set_sensor_power(bool enable) noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        std::uint32_t mask = kPinLoadSwitch | kPinMarkerAnlg;
        bsrr = enable ? mask : (mask << 16);
    }
};

// RAII-обгортка для гарантованого вимкнення живлення периферії
class [[nodiscard]] SensorPowerRailGuard {
public:
    SensorPowerRailGuard() noexcept {
        FastMarkerPort::set_sensor_power(true);
    }

    ~SensorPowerRailGuard() noexcept {
        FastMarkerPort::set_sensor_power(false);
    }

    SensorPowerRailGuard(const SensorPowerRailGuard&) = delete;
    SensorPowerRailGuard& operator=(const SensorPowerRailGuard&) = delete;
};

// Апаратний лічильник тактів Cortex-M
class CycleCounter {
public:
    static void init() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(kDemcr) |= (1U << 24);
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCtrl) |= (1U << 0);
    }

    static void reset() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt) = 0;
    }

    [[nodiscard]] static std::uint32_t get() noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt);
    }

    static void wait_cycles(std::uint32_t cycles) noexcept {
        std::uint32_t start = get();
        while ((get() - start) < cycles) {
            // Очікування встановлення шини
        }
    }
};

// Контейнер збереженої пам'яті
class BackupDomain {
public:
    explicit BackupDomain(std::uintptr_t base_address) noexcept
        : storage_(*reinterpret_cast<RetentionStorage*>(base_address)) {
        if (storage_.boot_magic != kRetentionMagic) {
            storage_.boot_magic = kRetentionMagic;
            storage_.wake_counter = 0;
        }
    }

    void record_sample(std::uint16_t value, std::uint32_t duration_cycles) noexcept {
        std::size_t idx = storage_.wake_counter % kHistoryDepth;
        storage_.adc_history[idx] = value;
        storage_.wake_counter++;
        storage_.last_duration_cycles = duration_cycles;
    }

    [[nodiscard]] std::span<const std::uint16_t> history() const noexcept {
        return {storage_.adc_history, kHistoryDepth};
    }

private:
    RetentionStorage& storage_;
};

// Основний конвеєр швидкого пробудження
class FastWakeupController {
public:
    static void execute_fast_cycle() noexcept {
        FastMarkerPort::set_cpu_active(true);
        CycleCounter::reset();

        BackupDomain backup(0x10000000U);

        std::uint16_t sample_value = 0;
        {
            SensorPowerRailGuard rail_guard{};

            // Очікування стабілізації: 120 мкс на 16 МГц = 1920 тактів
            CycleCounter::wait_cycles(1920U);

            sample_value = sample_analog_input();
        } // rail_guard автоматично знеструмлює датчик при виході з блоку

        backup.record_sample(sample_value, CycleCounter::get());

        FastMarkerPort::set_cpu_active(false);
        enter_deep_sleep();
    }

private:
    [[nodiscard]] static std::uint16_t sample_analog_input() noexcept {
        volatile std::uint32_t accumulator = 0;
        for (std::size_t i = 0; i < 16; ++i) {
            accumulator += static_cast<std::uint32_t>(2048U + i * 3);
        }
        return static_cast<std::uint16_t>(accumulator >> 4);
    }

    static void enter_deep_sleep() noexcept {
        auto& pwr_scr = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x18U);
        auto& pwr_cr1 = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x00U);

        pwr_scr = (1U << 0);       // Clear WUF
        pwr_cr1 |= (1U << 14);     // Stop 2 Mode

        asm volatile ("wfi");
    }
};

} // namespace power_audit

extern "C" void fast_wakeup_sequence(void) {
    power_audit::FastWakeupController::execute_fast_cycle();
}
