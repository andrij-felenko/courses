#include "controllers.hpp"

#include <algorithm>
#include <cmath>

namespace fm {
namespace {

/* Коефіцієнти контурів — робочі значення для квадрокоптера класу 450 мм. На
   іншій рамі їх переналаштовують, але структура каскаду (позиція → швидкість →
   кут, висота → вертикальна швидкість → тяга) не міняється. */
constexpr float kAltP      = 1.00F;   // м/с на метр помилки висоти
constexpr float kVzMax     = 2.50F;   // межа вертикальної швидкості, м/с
constexpr float kVzP       = 0.25F;   // частка тяги на м/с помилки
constexpr float kVzI       = 0.08F;   // те саме за секунду
constexpr float kPosP      = 0.90F;   // м/с на метр помилки положення
constexpr float kVelMax    = 5.00F;   // межа горизонтальної швидкості, м/с
constexpr float kVelP      = 4.00F;   // градусів нахилу на м/с помилки
constexpr float kVelI      = 0.80F;
constexpr float kTiltMax   = 35.00F;  // межа кута нахилу, градуси
constexpr float kStickDead = 0.10F;   // мертва зона стіків крену й тангажу
constexpr float kThrDead   = 0.10F;   // півширина мертвої зони ручки газу

}  // namespace

void ControllerStack::init(const VehicleState& s)
{
    altEngaged_   = false;
    altTargetM_   = s.vertical.altitudeRelM;
    vzIntegrator_ = s.propulsion.hoverThrottle;
    posEngaged_   = false;
    posLatched_   = false;
    target_       = s.horizontal.position;
    velIntNorth_  = 0.0F;
    velIntEast_   = 0.0F;
    tiltNorthDeg_ = 0.0F;
    tiltEastDeg_  = 0.0F;
    slew_.reset(s.propulsion.motorOutput);
}

void ControllerStack::enter(Mode mode, const VehicleState& s, const Params& p)
{
    altEngaged_ = traits(mode).autoThrottle;
    posEngaged_ = traits(mode).needsPosition;

    // 1. Фіксація уставок: ціль дорівнює тому, що є ЗАРАЗ, у ту саму
    //    мілісекунду перемикання. Інакше регулятор побачить помилку, якої
    //    насправді немає, і відпрацює її повним ходом.
    altTargetM_ = s.vertical.altitudeRelM;
    target_     = s.horizontal.position;
    posLatched_ = posEngaged_;

    // 2. Передустановка інтегратора: вертикальний канал стартує з тієї тяги,
    //    яку мотори вже дають, а не з нуля. Саме це відділяє плавний перехід
    //    від просідання на метр-другий.
    if (altEngaged_) {
        const float hover = (s.propulsion.hoverThrottle > 0.05F) ? s.propulsion.hoverThrottle : 0.5F;
        const float base  = (s.propulsion.motorOutput > 0.05F) ? s.propulsion.motorOutput : hover;

        vzIntegrator_ = std::clamp(base, 0.0F, 1.0F);
    } else {
        vzIntegrator_ = s.sticks.throttle;
    }

    // 3. Інтегратори горизонталі стартують з поточної команди нахилу — апарат
    //    уже летить із якимось креном, і обнуляти його ривком не можна.
    velIntNorth_ = std::clamp(tiltNorthDeg_, -kTiltMax, kTiltMax);
    velIntEast_  = std::clamp(tiltEastDeg_, -kTiltMax, kTiltMax);

    if (mode == Mode::Rtl && s.home) {
        // Повернення: спершу набір безпечної висоти, ціль по горизонталі —
        // точка старту. Висоту не знижуємо ніколи, лише піднімаємо.
        target_     = *s.home;
        altTargetM_ = std::max(s.vertical.altitudeRelM, p.rtlAltM);
        posLatched_ = true;
    }

    if (mode == Mode::Auto && s.mission != nullptr && !s.mission->empty()) {
        // Перша точка плану; далі точки подає навігатор місії.
        const Waypoint& first = s.mission->items().front();

        target_     = first.at;
        altTargetM_ = first.altRelM;
        posLatched_ = true;
    }

    // 4. Обмежувач наростання починає рахувати від фактичного виходу.
    slew_.reset(s.propulsion.motorOutput);
}

void ControllerStack::setPositionTarget(Mode mode, GeoPoint target, float altRelM)
{
    if (mode != Mode::Guided && mode != Mode::Auto) {
        return;   // поза автономними режимами зовнішня точка нічого не означає
    }
    target_ = target;
    if (!std::isnan(altRelM) && altRelM > 0.0F) {
        altTargetM_ = altRelM;
    }
    posLatched_ = true;
}

void ControllerStack::cut() noexcept
{
    altEngaged_   = false;
    posEngaged_   = false;
    vzIntegrator_ = 0.0F;
    tiltNorthDeg_ = 0.0F;
    tiltEastDeg_  = 0.0F;
    slew_.reset(0.0F);
}

/* Вертикальна швидкість, якої просить пілот ручкою газу в режимах з
   автоматичною тягою: центральна мертва зона — утримання висоти. */
float ControllerStack::stickClimbRate(const VehicleState& s) const noexcept
{
    const float centered = s.sticks.throttle - 0.5F;

    if (std::fabs(centered) <= kThrDead) {
        return 0.0F;
    }

    const float span = 0.5F - kThrDead;
    const float rate = (centered - std::copysign(kThrDead, centered)) / span;

    return std::clamp(rate, -1.0F, 1.0F) * kVzMax;
}

/* Внутрішній контур: вертикальна швидкість -> частка тяги, з інтегратором і
   захистом від його розкручування на упорі. */
float ControllerStack::verticalLoop(float vzSetpoint, const VehicleState& s, Seconds dt)
{
    const float err        = vzSetpoint - s.vertical.velocityMs;
    const float unclamped  = vzIntegrator_ + kVzP * err;

    if (unclamped > 0.0F && unclamped < 1.0F) {
        // Інтегруємо лише поки вихід не вперся в межу — інакше інтегратор
        // накопичить те, чого мотори однаково не віддадуть.
        vzIntegrator_ = std::clamp(vzIntegrator_ + kVzI * err * dt.count(), 0.0F, 1.0F);
    }
    return std::clamp(vzIntegrator_ + kVzP * err, 0.0F, 1.0F);
}

/* Каскад горизонталі: помилка положення -> уставка швидкості -> кут нахилу. */
void ControllerStack::horizontalLoop(const VehicleState& s, Seconds dt)
{
    float velSpNorth = 0.0F;
    float velSpEast  = 0.0F;

    const bool sticksMoved = std::fabs(s.sticks.pitch) > kStickDead ||
                             std::fabs(s.sticks.roll) > kStickDead;

    if (sticksMoved) {
        // Пілот веде апарат: стіки задають вектор швидкості, а ціль по
        // координатах буде зафіксована в мить, коли стіки стануть.
        velSpNorth  = std::clamp(s.sticks.pitch, -1.0F, 1.0F) * kVelMax;
        velSpEast   = std::clamp(s.sticks.roll, -1.0F, 1.0F) * kVelMax;
        posLatched_ = false;
    } else {
        if (!posLatched_) {
            target_     = s.horizontal.position;
            posLatched_ = true;
        }

        const NedOffset err = geoOffset(s.horizontal.position, target_);

        velSpNorth = std::clamp(err.north * kPosP, -kVelMax, kVelMax);
        velSpEast  = std::clamp(err.east * kPosP, -kVelMax, kVelMax);
    }

    const float errVn = velSpNorth - s.horizontal.velNorthMs;
    const float errVe = velSpEast - s.horizontal.velEastMs;

    if (std::fabs(velIntNorth_ + kVelP * errVn) < kTiltMax) {
        velIntNorth_ = std::clamp(velIntNorth_ + kVelI * errVn * dt.count(), -kTiltMax, kTiltMax);
    }
    if (std::fabs(velIntEast_ + kVelP * errVe) < kTiltMax) {
        velIntEast_ = std::clamp(velIntEast_ + kVelI * errVe * dt.count(), -kTiltMax, kTiltMax);
    }

    tiltNorthDeg_ = std::clamp(velIntNorth_ + kVelP * errVn, -kTiltMax, kTiltMax);
    tiltEastDeg_  = std::clamp(velIntEast_ + kVelP * errVe, -kTiltMax, kTiltMax);
}

float ControllerStack::step(Mode mode, const VehicleState& s, const Params& p,
                            const LandDetector& land, Seconds dt)
{
    if (dt.count() <= 0.0F) {
        dt = Seconds{0.01F};   // такт 100 Гц як запобіжник від нульового кроку
    }

    if (mode == Mode::Terminate) {
        cut();
        return slew_.output();
    }

    float command = 0.0F;

    if (manualThrottle(mode)) {
        altEngaged_   = false;
        posEngaged_   = false;
        tiltNorthDeg_ = 0.0F;
        tiltEastDeg_  = 0.0F;
        command       = std::clamp(s.sticks.throttle, 0.0F, 1.0F);
    } else if (land.landed()) {
        // Посадку підтверджено: мотори на холостому ходу до роззброєння.
        command       = p.landIdleThrottle;
        vzIntegrator_ = command;
    } else {
        float vzSetpoint = 0.0F;

        if (mode == Mode::Land || mode == Mode::EmergencyLand) {
            vzSetpoint = land.targetClimbRate(p);
        } else if (const float stickVz = stickClimbRate(s); stickVz != 0.0F) {
            // Поки пілот тримає ручку поза мертвою зоною, цільова висота їде за
            // поточною — щоб на відпусканні зафіксуватися саме тут.
            altTargetM_ = s.vertical.altitudeRelM;
            vzSetpoint  = stickVz;
        } else {
            vzSetpoint = std::clamp((altTargetM_ - s.vertical.altitudeRelM) * kAltP,
                                    -kVzMax, kVzMax);
        }

        command = verticalLoop(vzSetpoint, s, dt);

        if (traits(mode).needsPosition) {
            posEngaged_ = true;
            horizontalLoop(s, dt);
        } else {
            posEngaged_   = false;
            tiltNorthDeg_ = 0.0F;
            tiltEastDeg_  = 0.0F;
        }
    }

    // Обмежувач наростання стоїть ПІСЛЯ всіх контурів: він прибирає східчасті
    // стрибки навіть тоді, коли перехід уже пройшов усі охоронці.
    return slew_.step(std::clamp(command, 0.0F, 1.0F), dt, p.throttleSlewPerS);
}

}  // namespace fm
