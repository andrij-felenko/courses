#include <cstdint>
#include <array>
#include <span>

enum class BootStage : uint8_t {
    Reset = 0,
    SysInitDone,
    StaticInitDone,
    DriversReady,
    FirstFrameSent,
    Count
};

class BootProfiler {
public:
    static constexpr uintptr_t DwtCtrlAddr   = 0xE0001000U;
    static constexpr uintptr_t DwtCyccntAddr = 0xE0001004U;
    static constexpr uintptr_t DemCrAddr     = 0xE000EDFCU;

    explicit constexpr BootProfiler(uint32_t cpu_freq_hz) noexcept 
        : cpu_freq_hz_(cpu_freq_hz), timestamps_{} {}

    void start() noexcept {
        auto& dem_cr   = *reinterpret_cast<volatile uint32_t*>(DemCrAddr);
        auto& dwt_ctrl = *reinterpret_cast<volatile uint32_t*>(DwtCtrlAddr);
        auto& dwt_cyc  = *reinterpret_cast<volatile uint32_t*>(DwtCyccntAddr);

        dem_cr |= (1U << 24);   // TRCENA
        dwt_cyc = 0;
        dwt_ctrl |= (1U << 0);  // Enable CYCCNT
        timestamps_[static_cast<size_t>(BootStage::Reset)] = 0;
    }

    void mark(BootStage stage) noexcept {
        const auto idx = static_cast<size_t>(stage);
        if (idx < timestamps_.size()) {
            const auto& dwt_cyc = *reinterpret_cast<const volatile uint32_t*>(DwtCyccntAddr);
            timestamps_[idx] = dwt_cyc;
        }
    }

    [[nodiscard]] uint32_t duration_us(BootStage stage) const noexcept {
        const auto idx = static_cast<size_t>(stage);
        if (idx >= timestamps_.size() || cpu_freq_hz_ == 0) {
            return 0;
        }
        const uint64_t cycles = timestamps_[idx];
        return static_cast<uint32_t>((cycles * 1'000'000ULL) / cpu_freq_hz_);
    }

private:
    uint32_t cpu_freq_hz_{0};
    std::array<uint32_t, static_cast<size_t>(BootStage::Count)> timestamps_{};
};
