#include "bumpless_pid.h"
#include "pid_num.h"

#include <stddef.h>

/* Заповнити знімок телеметрії, коли такт відкинуто й стан не змінювався. */
static void trace_frozen(pid_trace_t *trace, const bumpless_pid_t *pid,
                         float measurement, uint8_t flags)
{
    if (trace == NULL) {
        return;
    }
    trace->setpoint = pid->current_setpoint;
    trace->measurement = measurement;
    trace->error = 0.0f;
    trace->p_term = 0.0f;
    trace->i_term = pid->integral;
    trace->d_term = 0.0f;
    trace->ff_term = 0.0f;
    trace->output = pid->last_output;
    trace->flags = flags;
}

bool bumpless_pid_config_valid(const pid_config_t *cfg)
{
    if (cfg == NULL) {
        return false;
    }
    if (!pid_is_finite(cfg->kp) || !pid_is_finite(cfg->ki) ||
        !pid_is_finite(cfg->kd) || !pid_is_finite(cfg->kff)) {
        return false;
    }
    if (!pid_is_finite(cfg->out_min) || !pid_is_finite(cfg->out_max) ||
        !pid_is_finite(cfg->i_min) || !pid_is_finite(cfg->i_max)) {
        return false;
    }
    if (!pid_is_finite(cfg->slew_rate_max) || cfg->slew_rate_max < 0.0f) {
        return false;
    }
    /* Перевернуті межі зробили б затиск невизначеним. */
    if (cfg->out_min > cfg->out_max || cfg->i_min > cfg->i_max) {
        return false;
    }
    return true;
}

void bumpless_pid_init(bumpless_pid_t *pid, const pid_config_t *cfg)
{
    if (pid == NULL) {
        return;
    }

    pid->cfg = cfg;
    pid->integral = 0.0f;
    pid->prev_measurement = 0.0f;
    pid->target_setpoint = 0.0f;
    pid->current_setpoint = 0.0f;
    pid->last_output = 0.0f;
    pid->flags = 0u;
    /*
     * Регулятор із непридатною конфігурацією лишається вимкненим назавжди:
     * краще мовчазний нуль на приводі, ніж керування за сміттям із Flash.
     */
    pid->is_initialized = bumpless_pid_config_valid(cfg);
}

void bumpless_pid_handover(bumpless_pid_t *pid,
                          float current_measurement,
                          float target_setpoint,
                          float prev_actuator_output)
{
    const pid_config_t *cfg;
    float measurement;
    float u_prev;
    float wanted_integral;
    float integral;
    uint8_t flags = PID_FLAG_FRESH;

    if (pid == NULL || !pid->is_initialized) {
        return;
    }
    cfg = pid->cfg;

    /* Сміття в аргументах не пускаємо в стан: беремо останнє відоме добре. */
    measurement = pid_is_finite(current_measurement) ? current_measurement
                                                     : pid->prev_measurement;
    u_prev = pid_is_finite(prev_actuator_output) ? prev_actuator_output
                                                 : pid->last_output;
    u_prev = pid_clampf(u_prev, cfg->out_min, cfg->out_max);

    /*
     * Ключ безривковості. На першому такті після передачі:
     *   error = current_setpoint − measurement = 0   (уставку кладемо на вимір),
     *   D     = −kd·(meas − prev_meas)/dt   = 0      (історію теж кладемо на вимір),
     *   FF    = kff·current_setpoint       = kff·measurement.
     * Отже u = FF + integral. Розв'язуємо це відносно інтеграла — саме тому
     * внесок прямого зв'язку віднімається, інакше трим було б враховано двічі.
     */
    pid->current_setpoint = measurement;
    pid->prev_measurement = measurement;
    pid->target_setpoint = pid_is_finite(target_setpoint) ? target_setpoint
                                                          : measurement;

    wanted_integral = u_prev - cfg->kff * measurement;
    integral = pid_clampf(wanted_integral, cfg->i_min, cfg->i_max);
    if (integral != wanted_integral) {
        /*
         * Чесна межа гарантії: попередній хід приводу не вкладається
         * в дозволений діапазон інтегратора, тож стик усе-таки буде
         * видно. Викликова сторона бачить це прапорцем.
         */
        flags |= PID_FLAG_I_CLAMPED;
    }

    pid->integral = integral;
    pid->last_output = u_prev;
    pid->flags = flags;
}

/* Спільне тіло update: єдине місце, де живе закон керування. */
static float pid_step(bumpless_pid_t *pid, float measurement, float dt,
                      pid_trace_t *trace)
{
    const pid_config_t *cfg;
    uint8_t fresh;
    uint8_t flags = 0u;
    bool slewing = false;
    bool saturated;
    float setpoint;
    float error;
    float p_term;
    float d_term;
    float ff_term;
    float delta_i;
    float trial_integral;
    float clamped_integral;
    float raw_output;
    float output;

    if (pid == NULL) {
        return 0.0f;
    }
    if (!pid->is_initialized) {
        trace_frozen(trace, pid, measurement, 0u);
        return pid->last_output;
    }
    cfg = pid->cfg;

    /* Службовий біт «щойно після передачі» мусить пережити відкинутий такт. */
    fresh = (uint8_t)(pid->flags & PID_FLAG_FRESH);

    if (!pid_is_finite(dt) || !(dt > 0.0f)) {
        pid->flags = (uint8_t)(PID_FLAG_DT_INVALID | fresh);
        trace_frozen(trace, pid, measurement, PID_FLAG_DT_INVALID);
        return pid->last_output;
    }

    /*
     * Збій шини I2C/SPI видає NaN або ±Inf. Одне таке число, потрапивши
     * в інтегратор, отруює регулятор назавжди: NaN не витісняється
     * жодною подальшою арифметикою. Тому такт відкидаємо цілком —
     * разом із ремпінгом уставки, щоб після відновлення давача
     * ціль не виявилася втеклою вперед.
     */
    if (!pid_is_finite(measurement)) {
        pid->flags = (uint8_t)(PID_FLAG_SENSOR_FAULT | fresh);
        trace_frozen(trace, pid, measurement, PID_FLAG_SENSOR_FAULT);
        return pid->last_output;
    }

    /* 1. Ремпінг уставки. Перший такт після передачі йде без нього:
     *    саме він мусить відтворити попередній хід приводу бітово. */
    if (fresh != 0u) {
        setpoint = pid->current_setpoint;
    } else {
        setpoint = pid_slew_step(pid->current_setpoint, pid->target_setpoint,
                                 cfg->slew_rate_max, dt, &slewing);
    }
    pid->current_setpoint = setpoint;
    if (slewing) {
        flags |= PID_FLAG_SLEWING;
    }

    /* 2. P, D за виміром і прямий зв'язок.
     *    Похідну беремо ВИКЛЮЧНО за виміром: стрибок уставки тоді
     *    не породжує похідного удару по приводу. */
    error = setpoint - measurement;
    p_term = cfg->kp * error;
    d_term = -cfg->kd * (measurement - pid->prev_measurement) / dt;
    ff_term = cfg->kff * setpoint;

    /* 3. Пробне інтегрування із жорстким затиском накопичувача. */
    delta_i = cfg->ki * error * dt;
    trial_integral = pid->integral + delta_i;
    clamped_integral = pid_clampf(trial_integral, cfg->i_min, cfg->i_max);
    if (clamped_integral != trial_integral) {
        flags |= PID_FLAG_I_CLAMPED;
    }

    raw_output = p_term + clamped_integral + d_term + ff_term;
    output = pid_clampf(raw_output, cfg->out_min, cfg->out_max);
    saturated = (output != raw_output);
    if (saturated) {
        flags |= PID_FLAG_SATURATED;
    }

    /*
     * 4. Clamping anti-windup. Привід уже вперся в механічну межу —
     * подальше накопичення площі помилки нічого не додає до тяги,
     * зате розкручує інтеграл, і на зворотному ході його доводиться
     * довго розвантажувати (класичне перерегулювання після насичення).
     * Тому нове значення приймаємо лише тоді, коли воно НЕ жене
     * глибше в той самий бік насичення. Сам вихід лишається обмеженим:
     * перерахунок не змінив би його — він однаково впирається в межу.
     */
    if (saturated &&
        ((raw_output > cfg->out_max && delta_i > 0.0f) ||
         (raw_output < cfg->out_min && delta_i < 0.0f))) {
        flags |= PID_FLAG_I_HELD;
    } else {
        pid->integral = clamped_integral;
    }

    pid->prev_measurement = measurement;
    pid->last_output = output;
    pid->flags = flags;   /* FRESH згорає рівно тут */

    if (trace != NULL) {
        trace->setpoint = setpoint;
        trace->measurement = measurement;
        trace->error = error;
        trace->p_term = p_term;
        trace->i_term = clamped_integral;
        trace->d_term = d_term;
        trace->ff_term = ff_term;
        trace->output = output;
        trace->flags = flags;
    }
    return output;
}

float bumpless_pid_update(bumpless_pid_t *pid, float measurement, float dt)
{
    return pid_step(pid, measurement, dt, NULL);
}

float bumpless_pid_update_traced(bumpless_pid_t *pid, float measurement,
                                 float dt, pid_trace_t *trace)
{
    return pid_step(pid, measurement, dt, trace);
}
