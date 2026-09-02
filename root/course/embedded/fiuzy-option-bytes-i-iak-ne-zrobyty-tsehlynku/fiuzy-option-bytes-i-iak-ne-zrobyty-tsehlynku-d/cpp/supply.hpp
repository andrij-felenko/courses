#pragma once

#include <cstdint>

#include "mmio.hpp"

// Перевірка живлення перед записом службової сторінки. Беремо штатний
// детектор PVD: він порівнює VDD із внутрішнім опорним джерелом і відповідає
// «вище / нижче» без АЦП і без калібрувальних констант.
namespace supply {

enum class Threshold : std::uint8_t {
    V2_0 = 0,
    V2_2 = 1,
    V2_4 = 2,
    V2_5 = 3,
    V2_6 = 4,
    V2_8 = 5,
    V2_9 = 6,
};

// RAII: конструктор вмикає PVD (і, якщо треба, тактування PWR), деструктор
// повертає обидва в той стан, у якому їх знайшли.
class Monitor {
public:
    explicit Monitor(Threshold level) noexcept
        : clock_was_on_((hal::rcc_apb1enr1() & hal::kRccPwrEn) != 0UL)
    {
        if (!clock_was_on_) {
            hal::rcc_apb1enr1() |= hal::kRccPwrEn;
            [[maybe_unused]] volatile std::uint32_t readback = hal::rcc_apb1enr1();
        }

        std::uint32_t cr2 = hal::pwr().CR2;
        cr2 &= ~hal::kPvdLevelMask;
        cr2 |= (static_cast<std::uint32_t>(level) << hal::kPvdLevelShift) & hal::kPvdLevelMask;
        cr2 |= hal::raw(hal::PwrCr2::PvdEnable);
        hal::pwr().CR2 = cr2;

        // компаратор виходить на режим за одиниці мікросекунд
        for (volatile std::uint32_t spin = 0; spin < kSettleLoops; ++spin) {
        }
    }

    ~Monitor() noexcept
    {
        hal::pwr().CR2 &= ~hal::raw(hal::PwrCr2::PvdEnable);
        if (!clock_was_on_) {
            hal::rcc_apb1enr1() &= ~hal::kRccPwrEn;
        }
    }

    Monitor(const Monitor&) = delete;
    Monitor& operator=(const Monitor&) = delete;

    // PVDO = 1 означає «VDD нижче порога» — інверсія, на якій легко спіткнутися.
    [[nodiscard]] bool vdd_above_threshold() const noexcept
    {
        return (hal::pwr().SR2 & hal::raw(hal::PwrSr2::PvdOutput)) == 0UL;
    }

private:
    static constexpr std::uint32_t kSettleLoops = 4000UL;

    bool clock_was_on_;
};

} // namespace supply
