#include <cstdint>
#include <cstddef>
#include <span>

namespace low_power {

inline constexpr std::uintptr_t kGpioaBase   = 0x48000000U;
inline constexpr std::uintptr_t kPwrBase     = 0x40007000U;
inline constexpr std::uintptr_t kDwtCtrl     = 0xE0001000U;
inline constexpr std::uintptr_t kDwtCyccnt   = 0xE0001004U;
inline constexpr std::uintptr_t kDemcr       = 0xE000EDFCU;
inline constexpr std::uintptr_t kContextAddr = 0x10000000U;

inline constexpr std::uint32_t kPinMarkerDebug  = 1U << 0;
inline constexpr std::uint32_t kPinSensorVccEn  = 1U << 2;
inline constexpr std::uint32_t kContextMagic    = 0xC001CAFEU;
inline constexpr std::size_t   kBufferSize      = 32;

struct FastWakeContext {
    std::uint32_t signature;
    std::uint32_t wake_count;
    std::uint16_t sensor_buffer[kBufferSize];
    std::uint16_t adc_calibration_offset;
};

class HardwareProfiler {
public:
    static void init_cycle_counter() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(kDemcr) |= (1U << 24);
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCtrl) |= (1U << 0);
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt) = 0;
    }

    [[nodiscard]] static std::uint32_t elapsed_cycles() noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt);
    }

    static void spin_wait_cycles(std::uint32_t target_cycles) noexcept {
        while (elapsed_cycles() < target_cycles) {
            // Очікування заряду фільтрувальних ємностей
        }
    }
};

class [[nodiscard]] SensorPowerRailGuard {
public:
    SensorPowerRailGuard() noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        bsrr = kPinMarkerDebug | kPinSensorVccEn;
    }

    ~SensorPowerRailGuard() noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        bsrr = (kPinMarkerDebug << 16) | (kPinSensorVccEn << 16);
    }

    SensorPowerRailGuard(const SensorPowerRailGuard&) = delete;
    SensorPowerRailGuard& operator=(const SensorPowerRailGuard&) = delete;
};

class RetentionStore {
public:
    explicit RetentionStore(std::uintptr_t base_address) noexcept
        : ctx_(*reinterpret_cast<FastWakeContext*>(base_address)) {
        if (ctx_.signature != kContextMagic) {
            ctx_.signature = kContextMagic;
            ctx_.wake_count = 0;
            ctx_.adc_calibration_offset = 12;
        }
    }

    void append_sample(std::uint16_t sample) noexcept {
        std::size_t index = ctx_.wake_count % kBufferSize;
        ctx_.sensor_buffer[index] = sample;
        ctx_.wake_count++;
    }

    [[nodiscard]] std::uint16_t calibration_offset() const noexcept {
        return ctx_.adc_calibration_offset;
    }

    [[nodiscard]] std::span<const std::uint16_t> buffered_samples() const noexcept {
        return {ctx_.sensor_buffer, kBufferSize};
    }

private:
    FastWakeContext& ctx_;
};

class WakeupPipeline {
public:
    static void run() noexcept {
        HardwareProfiler::init_cycle_counter();
        RetentionStore store(kContextAddr);

        std::uint16_t result = 0;
        {
            SensorPowerRailGuard rail_guard{};

            // Очікування стабілізації: 100 мкс на 16 МГц = 1600 тактів
            HardwareProfiler::spin_wait_cycles(1600U);

            result = acquire_adc_sample(store.calibration_offset());
        } // rail_guard гарантовано вимикає живлення датчика тут

        store.append_sample(result);
        enter_stop2_sleep();
    }

private:
    [[nodiscard]] static std::uint16_t acquire_adc_sample(std::uint16_t offset) noexcept {
        volatile std::uint32_t accumulator = 0;
        for (std::size_t i = 0; i < 16; ++i) {
            accumulator += static_cast<std::uint32_t>(2048U + offset + i * 2);
        }
        return static_cast<std::uint16_t>(accumulator >> 4);
    }

    static void enter_stop2_sleep() noexcept {
        auto& pwr_scr = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x18U);
        auto& pwr_cr1 = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x00U);

        pwr_scr = (1U << 0);       // Clear WUF
        pwr_cr1 |= (1U << 14);     // Stop 2 Mode

        asm volatile ("wfi");
    }
};

} // namespace low_power

extern "C" void execute_fast_wake_pipeline(void) {
    low_power::WakeupPipeline::run();
}
