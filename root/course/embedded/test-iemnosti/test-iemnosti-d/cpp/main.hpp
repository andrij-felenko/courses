// Обчислення параметрів розряду та кулонометрії (C++20)
#include <cstdint>
#include <chrono>

namespace BatteryAnalytics {

using namespace std::chrono_literals;

class DischargeTracker {
public:
    constexpr DischargeTracker() noexcept = default;

    void update(uint32_t cellVoltageMv, uint32_t loadCurrentMa, std::chrono::milliseconds dt) noexcept {
        currentVoltageMv_ = cellVoltageMv;
        currentCurrentMa_ = loadCurrentMa;

        const auto dtMs = static_cast<uint64_t>(dt.count());
        accumulatedMicroampSeconds_ += static_cast<uint64_t>(loadCurrentMa) * 1000ULL * dtMs / 1000ULL;

        const uint32_t powerMw = (cellVoltageMv * loadCurrentMa) / 1000UL;
        accumulatedMicrowattSeconds_ += static_cast<uint64_t>(powerMw) * 1000ULL * dtMs / 1000ULL;
    }

    [[nodiscard]] constexpr uint32_t capacityMah() const noexcept {
        return static_cast<uint32_t>(accumulatedMicroampSeconds_ / 3'600'000ULL);
    }

    [[nodiscard]] constexpr uint32_t energyMwh() const noexcept {
        return static_cast<uint32_t>(accumulatedMicrowattSeconds_ / 3'600'000ULL);
    }

    [[nodiscard]] constexpr uint32_t voltageMv() const noexcept { return currentVoltageMv_; }
    [[nodiscard]] constexpr uint32_t currentMa() const noexcept { return currentCurrentMa_; }

private:
    uint32_t currentVoltageMv_{0};
    uint32_t currentCurrentMa_{0};
    uint64_t accumulatedMicroampSeconds_{0};
    uint64_t accumulatedMicrowattSeconds_{0};
};

} // namespace BatteryAnalytics
