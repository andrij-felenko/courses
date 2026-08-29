#pragma once

#include "i2c_bus.hpp"
#include "sensor_bringup.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace bringup {

// Модель давача на шині: ті самі несправності, які на стенді вносять руками —
// зняттям живлення й повільним наростанням V_DD.
class SimulatedSensor final : public I2cBus {
public:
    struct Faults {
        std::optional<Millis> power_off_at{};  // коли зникає живлення
        std::optional<Millis> power_on_at{};   // коли повертається
        Millis por_ramp{2};                    // час наростання V_DD
    };

    explicit SimulatedSensor(Faults faults = {});

    // Просунути віртуальний час і застосувати заплановані події.
    void advance_to(Millis now);

    WriteResult write(std::uint8_t dev_addr, std::uint8_t reg, std::uint8_t value) override;
    ReadResult read(std::uint8_t dev_addr, std::uint8_t reg) override;
    void recover() override;

    [[nodiscard]] unsigned recoveries() const noexcept { return recoveries_; }
    [[nodiscard]] bool sda_stuck() const noexcept { return sda_stuck_; }

private:
    static constexpr std::size_t kRegCount = 0x20;
    static constexpr Millis kResetCore{5};      // доки ядро в скиданні, чип мовчить
    static constexpr unsigned kStuckBits = 6;   // ведений обірвався на шостому біті
    static constexpr std::uint8_t kOdrMax = 0x50;  // більші коди кремній не приймає

    void load_defaults() noexcept;
    void power_down() noexcept;
    void power_up() noexcept;
    [[nodiscard]] std::optional<BusError> precheck(std::uint8_t dev_addr);

    Faults faults_;
    Millis now_{0};
    bool cut_done_{false};
    bool restore_done_{false};

    bool powered_{true};
    Millis por_ready_{0};
    bool reset_pending_{false};
    Millis core_up_{0};

    bool sda_stuck_{false};
    unsigned stuck_bits_{0};
    unsigned recoveries_{0};
    unsigned scl_edges_{0};

    std::array<std::uint8_t, kRegCount> regs_{};
};

}  // namespace bringup
