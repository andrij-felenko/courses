// open_drain.hpp — лінія з відкритим стоком (I2C, «wired-AND», обмін із
// пристроєм на іншій напрузі). Високий рівень дає зовнішній резистор, тому
// перевірка проводки тут не розкіш, а частина запуску.
#pragma once

#include "pin.hpp"

#include <expected>
#include <string_view>
#include <utility>

namespace hw {

enum class BusFault : std::uint8_t {
    StuckLow,  // відпустили, а лінія в нулі: немає підтяжки, КЗ або ведений тримає шину
    StuckHigh, // притиснули, а лінія в одиниці: обрив або перемичка на живлення
    Locked     // не вдалося сконфігурувати сам вивід
};

[[nodiscard]] constexpr std::string_view describe(BusFault f) noexcept
{
    switch (f) {
    case BusFault::StuckLow:  return "лінія не піднімається: немає підтяжки або КЗ на землю";
    case BusFault::StuckHigh: return "лінія не притискається: обрив або перемичка на живлення";
    case BusFault::Locked:    return "конфігурацію виводу замкнено";
    }
    return "невідомий стан шини";
}

template <class PinT>
class OpenDrainLine {
public:
    // riseLoops — скільки чекати фронту: час задає RC підтяжки й ємності шини.
    [[nodiscard]] static std::expected<OpenDrainLine, BusFault> create(
        Speed speed = Speed::Medium, std::uint32_t riseLoops = 200) noexcept
    {
        PinT::high(); // Hi-Z ще до вмикання каскаду — не смикаємо шину

        // Внутрішні 30…50 кОм навмисно вимкнені: вони не витягнуть фронт,
        // зате замаскують відсутній зовнішній резистор.
        const PinConfig cfg{Mode::Output, OutputType::OpenDrain, speed, Pull::None};
        if (auto configured = PinT::configure(cfg); !configured) {
            return std::unexpected(BusFault::Locked);
        }

        return OpenDrainLine{riseLoops};
    }

    OpenDrainLine(const OpenDrainLine&) = delete;
    OpenDrainLine& operator=(const OpenDrainLine&) = delete;

    OpenDrainLine(OpenDrainLine&& other) noexcept
        : riseLoops_{other.riseLoops_}, owns_{std::exchange(other.owns_, false)}
    {
    }

    OpenDrainLine& operator=(OpenDrainLine&& other) noexcept
    {
        if (this != &other) {
            if (owns_) {
                PinT::high();
            }
            riseLoops_ = other.riseLoops_;
            owns_ = std::exchange(other.owns_, false);
        }
        return *this;
    }

    ~OpenDrainLine()
    {
        if (owns_) {
            release(); // мертвий об'єкт не має права тримати чужу шину
        }
    }

    void driveLow() noexcept { PinT::low(); }
    void release() noexcept { PinT::high(); }

    [[nodiscard]] bool level() const noexcept { return PinT::read(); }

    void settle() const noexcept { spin(riseLoops_); }

    // Відпустити → має піднятись; притиснути → має впасти. Хоч би чим
    // скінчилося, шина лишається відпущеною.
    [[nodiscard]] std::expected<void, BusFault> checkWiring() noexcept
    {
        release();
        settle();
        if (!level()) {
            return std::unexpected(BusFault::StuckLow);
        }

        driveLow();
        settle();
        const bool stillHigh = level();

        release();
        settle();

        if (stillHigh) {
            return std::unexpected(BusFault::StuckHigh);
        }
        return {};
    }

    // Тримає лінію в нулі на час області видимості.
    class LowHold {
    public:
        explicit LowHold(OpenDrainLine& line) noexcept : line_{line} { line_.driveLow(); }
        LowHold(const LowHold&) = delete;
        LowHold& operator=(const LowHold&) = delete;
        ~LowHold() { line_.release(); }

    private:
        OpenDrainLine& line_;
    };

    [[nodiscard]] LowHold hold() noexcept { return LowHold{*this}; }

private:
    explicit OpenDrainLine(std::uint32_t riseLoops) noexcept : riseLoops_{riseLoops} {}

    std::uint32_t riseLoops_{200};
    bool owns_{true};
};

} // namespace hw
