#pragma once

#include "land_detector.hpp"
#include "mission.hpp"
#include "mode.hpp"
#include "params.hpp"
#include "telemetry.hpp"
#include "throttle.hpp"

namespace fm {

/* Каскадний контур із безривковим перемиканням.

   Клас існує заради однієї властивості: у момент зміни режиму цільові уставки
   прирівнюються до поточних значень, а інтегратор вертикального каналу
   передустановлюється тягою висіння. Без цього перший же такт нового режиму
   видав би стрибок керуючого сигналу. Тому enter() — не «ініціалізація для
   охайності», а частина протоколу переходу. */
class ControllerStack {
public:
    void init(const VehicleState& s);

    /* Вхід у режим: фіксація уставок і передустановка інтеграторів.
       Викликається рівно один раз на перехід — ПІСЛЯ дозволу охоронців. */
    void enter(Mode mode, const VehicleState& s, const Params& p);

    /* Зовнішня цілевказівка для Guided і навігатора місії. */
    void setPositionTarget(Mode mode, GeoPoint target, float altRelM);

    /* Один такт контурів; повертає тягу 0..1 після обмежувача наростання. */
    [[nodiscard]] float step(Mode mode, const VehicleState& s, const Params& p,
                             const LandDetector& land, Seconds dt);

    [[nodiscard]] float tiltNorthDeg() const noexcept { return tiltNorthDeg_; }
    [[nodiscard]] float tiltEastDeg() const noexcept { return tiltEastDeg_; }
    [[nodiscard]] float output() const noexcept { return slew_.output(); }

    void cut() noexcept;   // відсічка: жодного плавного зведення

private:
    [[nodiscard]] float stickClimbRate(const VehicleState& s) const noexcept;
    [[nodiscard]] float verticalLoop(float vzSetpoint, const VehicleState& s, Seconds dt);
    void horizontalLoop(const VehicleState& s, Seconds dt);

    // Вертикальний канал
    bool  altEngaged_{false};
    float altTargetM_{0.0F};
    float vzIntegrator_{0.5F};   // у частках тяги

    // Горизонтальний канал
    bool     posEngaged_{false};
    bool     posLatched_{false};
    GeoPoint target_{};
    float    velIntNorth_{0.0F};   // інтегратори контуру швидкості, градуси
    float    velIntEast_{0.0F};
    float    tiltNorthDeg_{0.0F};
    float    tiltEastDeg_{0.0F};

    SlewLimiter slew_{0.0F};
};

}  // namespace fm
