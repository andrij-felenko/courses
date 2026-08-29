// services/power_manager.hpp — служба керування живленням.
// Підписана на EventType::SensorFault: витягнувши подію несправності, вона
// знеструмлює лінію давачів і піднімає її знову — без перезавантаження прошивки.
#pragma once

#include <chrono>
#include <cstdint>
#include <optional>

#include "bsp/power_rail.hpp"
#include "hal/clock.hpp"
#include "services/dispatcher.hpp"

namespace services {

// Служба не знає, який саме пристрій вона перезапускає: конкретний давач
// ховається за цим інтерфейсом.
class IRecoverable {
public:
    virtual ~IRecoverable() = default;

    IRecoverable() = default;
    IRecoverable(const IRecoverable&) = delete;
    IRecoverable& operator=(const IRecoverable&) = delete;

    // Підняти пристрій після подання живлення. false — не піднявся.
    virtual bool reinitialize() = 0;

    // Сказати верхньому шару, що можна починати спочатку.
    virtual void on_recovered() = 0;
};

class PowerManager final : public IEventHandler {
public:
    PowerManager(bsp::PowerRail& rail, hal::IClock& clock, IRecoverable& recovery,
                 std::chrono::milliseconds min_interval) noexcept
        : rail_(rail), clock_(clock), recovery_(recovery), min_interval_(min_interval)
    {
    }

    void on_event(const Event& evt) override;

    std::uint32_t cycles_done() const noexcept { return cycles_done_; }
    std::uint32_t cycles_failed() const noexcept { return cycles_failed_; }
    std::uint32_t cycles_suppressed() const noexcept { return cycles_suppressed_; }

    static constexpr EventMask subscription() { return EventMask{EventType::SensorFault}; }

private:
    bsp::PowerRail& rail_;
    hal::IClock& clock_;
    IRecoverable& recovery_;
    std::chrono::milliseconds min_interval_;
    std::optional<std::chrono::milliseconds> last_cycle_{};

    std::uint32_t cycles_done_{0};
    std::uint32_t cycles_failed_{0};
    std::uint32_t cycles_suppressed_{0};
};

}  // namespace services
