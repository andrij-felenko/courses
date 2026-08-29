#pragma once

#include "debounce.hpp"
#include "guards.hpp"
#include "params.hpp"
#include "telemetry.hpp"

namespace fm {

/* Детектор польоту й арбітр озброєння. Ці дві речі нероздільні: заборона
   роззброїтися в повітрі має сенс рівно настільки, наскільки чесно автомат
   знає, що апарат таки в повітрі. */
class ArmingState {
public:
    /* Один такт детектора; повертає витриманий вердикт «у повітрі». */
    bool update(const VehicleState& s, const Params& p);

    /* Детектор посадки підтвердив, що апарат стоїть: знімаємо вердикт негайно,
       не чекаючи витримки згасання. */
    void notifyLanded() noexcept { inAir_.reset(false); }

    [[nodiscard]] bool inAir() const noexcept { return inAir_.state(); }
    [[nodiscard]] bool armed() const noexcept { return armed_; }

    [[nodiscard]] GuardResult requestArm(const VehicleState& s);

    /* Запит роззброєння комбінацією стіків або командою станції.
       У повітрі — відмова, і це не налаштовується. */
    [[nodiscard]] GuardResult requestDisarm();

    /* Роззброєння за рішенням автомата після підтвердженої посадки:
       перевірку «у повітрі» обходить законно. */
    void disarmAfterLanding() noexcept;

    /* Апаратна відсічка: єдиний шлях зупинити мотори в польоті. Тумблер працює
       повз автомат — тут ми лише приводимо власну картину світу у відповідність
       до того, що вже сталося на рівні співпроцесора вводу-виводу. */
    void kill() noexcept;

private:
    [[nodiscard]] bool inAirSignature(const VehicleState& s, const Params& p) const noexcept;

    Debounce inAir_{false};
    bool     armed_{false};
    bool     killLatched_{false};
};

}  // namespace fm
