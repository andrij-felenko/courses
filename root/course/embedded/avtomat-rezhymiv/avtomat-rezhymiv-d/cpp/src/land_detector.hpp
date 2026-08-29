#pragma once

#include <string_view>

#include "debounce.hpp"
#include "params.hpp"
#include "telemetry.hpp"

namespace fm {

/* Детектор посадки. Барометр біля землі бреше на метр-другий через екранний
   ефект, тож момент торкання визначають не висотою, а збігом трьох незалежних
   ознак, витриманих у часі. */
class LandDetector {
public:
    enum class Phase : std::uint8_t {
        Idle,           // режим посадки не активний
        Descent,        // керований спуск зі швидкістю LAND_SPEED
        GroundContact,  // ознаки торкання зібралися, триває витримка
        Landed          // посадку підтверджено, час гасити мотори
    };

    void update(const VehicleState& s, const Params& p, bool landingMode, bool inAir);

    /* Скидання при виході з режимів посадки: недокручена витримка не має права
       пережити зміну режиму й спрацювати наступного разу. Подію роззброєння не
       гасимо — її мусить забрати автомат, а не з'їсти зміна режиму. */
    void reset() noexcept;

    [[nodiscard]] bool consumeDisarmEvent() noexcept;

    [[nodiscard]] Phase phase() const noexcept { return phase_; }
    [[nodiscard]] bool  landed() const noexcept { return phase_ == Phase::Landed; }

    /* Цільова вертикальна швидкість фази спуску (від'ємна — вниз). */
    [[nodiscard]] float targetClimbRate(const Params& p) const noexcept;

    [[nodiscard]] static std::string_view name(Phase phase) noexcept;

private:
    [[nodiscard]] static bool contactSignature(const VehicleState& s, const Params& p) noexcept;

    Phase     phase_{Phase::Idle};
    Debounce  contact_{false};
    TimePoint contactSince_{};
    bool      disarmEvent_{false};
};

}  // namespace fm
