#include "control/bumpless_pid.hpp"
#include "control/numeric.hpp"

namespace control {

namespace {

constexpr PidFlag strip_fresh(PidFlag flags) noexcept
{
    return static_cast<PidFlag>(static_cast<std::uint8_t>(flags) &
                                static_cast<std::uint8_t>(~static_cast<std::uint8_t>(PidFlag::Fresh)));
}

} // namespace

bool is_sane(const PidConfig& config) noexcept
{
    using num::finite;

    if (!finite(config.kp) || !finite(config.ki) ||
        !finite(config.kd) || !finite(config.kff)) {
        return false;
    }
    if (!finite(config.out_min) || !finite(config.out_max) ||
        !finite(config.i_min) || !finite(config.i_max)) {
        return false;
    }
    if (!finite(config.slew_rate_max) || config.slew_rate_max < 0.0f) {
        return false;
    }
    // Перевернуті межі зробили б затиск невизначеним.
    return config.out_min <= config.out_max && config.i_min <= config.i_max;
}

BumplessPidController::BumplessPidController(const PidConfig& config) noexcept
    : cfg_{config}
{
    /*
     * Регулятор із непридатною конфігурацією лишається вимкненим назавжди:
     * краще мовчазний нуль на приводі, ніж керування за сміттям із Flash.
     */
    initialized_ = is_sane(config);
}

PidFlag BumplessPidController::flags() const noexcept
{
    return strip_fresh(flags_);
}

void BumplessPidController::freeze(PidTelemetry* trace, float measurement,
                                   PidFlag flags) const noexcept
{
    if (trace == nullptr) {
        return;
    }
    *trace = PidTelemetry{};
    trace->setpoint = current_setpoint_;
    trace->measurement = measurement;
    trace->i_term = integral_;
    trace->output = last_output_;
    trace->flags = flags;
}

void BumplessPidController::handover(float current_measurement,
                                     float target_setpoint,
                                     float prev_actuator_output) noexcept
{
    if (!initialized_) {
        return;
    }
    const PidConfig& cfg = cfg_.get();

    // Сміття в аргументах не пускаємо в стан: беремо останнє відоме добре.
    const float measurement = num::finite(current_measurement) ? current_measurement
                                                               : prev_measurement_;
    float u_prev = num::finite(prev_actuator_output) ? prev_actuator_output
                                                     : last_output_;
    u_prev = num::clamp_to(u_prev, cfg.out_min, cfg.out_max);

    /*
     * Ключ безривковості. На першому такті після передачі:
     *   error = current_setpoint − measurement = 0   (уставку кладемо на вимір),
     *   D     = −kd·(meas − prev_meas)/dt   = 0      (історію теж кладемо на вимір),
     *   FF    = kff·current_setpoint       = kff·measurement.
     * Отже u = FF + integral. Розв'язуємо це відносно інтеграла — саме тому
     * внесок прямого зв'язку віднімається, інакше трим було б враховано двічі.
     */
    current_setpoint_ = measurement;
    prev_measurement_ = measurement;
    target_setpoint_ = num::finite(target_setpoint) ? target_setpoint : measurement;

    const float wanted = u_prev - cfg.kff * measurement;
    const float integral = num::clamp_to(wanted, cfg.i_min, cfg.i_max);

    PidFlag flags = PidFlag::Fresh;
    if (integral != wanted) {
        /*
         * Чесна межа гарантії: попередній хід приводу не вкладається
         * в дозволений діапазон інтегратора, тож стик усе-таки буде видно.
         * Викликова сторона бачить це прапорцем.
         */
        flags |= PidFlag::IntegralClamped;
    }

    integral_ = integral;
    last_output_ = u_prev;
    flags_ = flags;
}

float BumplessPidController::update(float measurement, float dt) noexcept
{
    return step(measurement, dt, nullptr);
}

float BumplessPidController::update(float measurement, float dt,
                                    PidTelemetry& trace) noexcept
{
    return step(measurement, dt, &trace);
}

float BumplessPidController::step(float measurement, float dt,
                                  PidTelemetry* trace) noexcept
{
    if (!initialized_) {
        freeze(trace, measurement, PidFlag::None);
        return last_output_;
    }
    const PidConfig& cfg = cfg_.get();

    // Службовий біт «щойно після передачі» мусить пережити відкинутий такт.
    const PidFlag fresh = flags_ & PidFlag::Fresh;
    PidFlag flags = PidFlag::None;

    if (!num::finite(dt) || !(dt > 0.0f)) {
        flags_ = PidFlag::InvalidDt | fresh;
        freeze(trace, measurement, PidFlag::InvalidDt);
        return last_output_;
    }

    /*
     * Збій шини I2C/SPI видає NaN або ±Inf. Одне таке число, потрапивши
     * в інтегратор, отруює регулятор назавжди: NaN не витісняється жодною
     * подальшою арифметикою. Тому такт відкидаємо цілком — разом із
     * ремпінгом уставки, щоб після відновлення давача ціль не виявилася
     * втеклою вперед.
     */
    if (!num::finite(measurement)) {
        ++fault_count_;
        flags_ = PidFlag::SensorFault | fresh;
        freeze(trace, measurement, PidFlag::SensorFault);
        return last_output_;
    }

    // 1. Ремпінг уставки. Перший такт після передачі йде без нього:
    //    саме він мусить відтворити попередній хід приводу бітово.
    float setpoint = current_setpoint_;
    if (!holds(fresh, PidFlag::Fresh)) {
        const auto slewed = num::slew_step(current_setpoint_, target_setpoint_,
                                           cfg.slew_rate_max, dt);
        setpoint = slewed.value;
        if (slewed.limited) {
            flags |= PidFlag::Slewing;
        }
    }
    current_setpoint_ = setpoint;

    // 2. P, D за виміром і прямий зв'язок. Похідну беремо ВИКЛЮЧНО за
    //    виміром: стрибок уставки тоді не породжує похідного удару.
    const float error = setpoint - measurement;
    const float p_term = cfg.kp * error;
    const float d_term = -cfg.kd * (measurement - prev_measurement_) / dt;
    const float ff_term = cfg.kff * setpoint;

    // 3. Пробне інтегрування із жорстким затиском накопичувача.
    const float delta_i = cfg.ki * error * dt;
    const float trial = integral_ + delta_i;
    const float clamped = num::clamp_to(trial, cfg.i_min, cfg.i_max);
    if (clamped != trial) {
        flags |= PidFlag::IntegralClamped;
    }

    const float raw_output = p_term + clamped + d_term + ff_term;
    const float output = num::clamp_to(raw_output, cfg.out_min, cfg.out_max);
    const bool saturated = (output != raw_output);
    if (saturated) {
        flags |= PidFlag::Saturated;
    }

    /*
     * 4. Clamping anti-windup. Привід уже вперся в механічну межу —
     * подальше накопичення площі помилки нічого не додає до тяги, зате
     * розкручує інтеграл, і на зворотному ході його доводиться довго
     * розвантажувати (класичне перерегулювання після насичення). Тому нове
     * значення приймаємо лише тоді, коли воно НЕ жене глибше в той самий
     * бік насичення. Сам вихід лишається обмеженим: перерахунок не змінив
     * би його — він однаково впирається в межу.
     */
    const bool pushing_deeper =
        saturated && ((raw_output > cfg.out_max && delta_i > 0.0f) ||
                      (raw_output < cfg.out_min && delta_i < 0.0f));
    if (pushing_deeper) {
        flags |= PidFlag::IntegralHeld;
    } else {
        integral_ = clamped;
    }

    prev_measurement_ = measurement;
    last_output_ = output;
    flags_ = flags;   // Fresh згорає рівно тут

    if (trace != nullptr) {
        trace->setpoint = setpoint;
        trace->measurement = measurement;
        trace->error = error;
        trace->p_term = p_term;
        trace->i_term = clamped;
        trace->d_term = d_term;
        trace->ff_term = ff_term;
        trace->output = output;
        trace->flags = flags;
    }
    return output;
}

} // namespace control
