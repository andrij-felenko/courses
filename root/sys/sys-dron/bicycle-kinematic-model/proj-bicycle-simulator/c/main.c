#include <math.h>
#include <stdbool.h>

/* Геометричні параметри та фізичні обмеження шасі */
typedef struct {
    double l_f;           /* Відстань від центру мас до передньої осі, м */
    double l_r;           /* Відстань від центру мас до задньої осі, м   */
    double max_steer;     /* Максимальний кут вивороту керма, рад       */
    double max_steer_rate;/* Максимальна швидкість перекладки, рад/с    */
    double max_accel;     /* Максимальне лінійне прискорення, м/с^2     */
} BicycleParams;

/* Вектор стану кінематичної моделі */
typedef struct {
    double x;             /* Координата X у світовій системі, м */
    double y;             /* Координата Y у світовій системі, м */
    double theta;         /* Курс (yaw), рад                    */
    double v;             /* Поздовжня лінійна швидкість, м/с   */
    double delta;         /* Поточний кут повороту коліс, рад   */
} BicycleState;

/* Похідні стану за часом */
typedef struct {
    double dx;
    double dy;
    double dtheta;
    double dv;
    double ddelta;
} BicycleDerivatives;

/* Метод чисельного інтегрування */
typedef enum {
    INTEGRATION_EULER,
    INTEGRATION_EXACT_ARC,
    INTEGRATION_RK4
} IntegrationMethod;

/* Обчислення похідних стану відносно центру мас */
static BicycleDerivatives bicycle_eval_derivatives(
    const BicycleState *state,
    double accel,
    double steer_rate,
    const BicycleParams *params)
{
    BicycleDerivatives deriv;
    double L = params->l_f + params->l_r;

    /* Кут зсуву швидкості (side-slip angle beta) */
    double beta = atan((params->l_r / L) * tan(state->delta));

    deriv.dx = state->v * cos(state->theta + beta);
    deriv.dy = state->v * sin(state->theta + beta);
    deriv.dtheta = (state->v / L) * tan(state->delta) * cos(beta);
    deriv.dv = accel;
    deriv.ddelta = steer_rate;

    return deriv;
}

/* Нормалізація кута в діапазон [-pi, pi] */
static double normalize_angle(double angle)
{
    while (angle > M_PI) angle -= 2.0 * M_PI;
    while (angle < -M_PI) angle += 2.0 * M_PI;
    return angle;
}

/* Обмеження величини за модулем */
static double clamp_value(double val, double min_val, double max_val)
{
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/* Один крок симуляції (інтеграція стану на dt) */
bool bicycle_step(
    BicycleState *state,
    double target_v,
    double target_delta,
    double dt,
    const BicycleParams *params,
    IntegrationMethod method)
{
    if (!state || !params || dt <= 0.0) {
        return false;
    }

    /* 1. Розрахунок керуючих похідних з урахуванням обмежень приводу */
    double v_error = target_v - state->v;
    double accel = clamp_value(v_error / dt, -params->max_accel, params->max_accel);

    double delta_clamped = clamp_value(target_delta, -params->max_steer, params->max_steer);
    double delta_error = delta_clamped - state->delta;
    double steer_rate = clamp_value(delta_error / dt, -params->max_steer_rate, params->max_steer_rate);

    if (method == INTEGRATION_EULER) {
        /* Метод Ейлера 1-го порядку */
        BicycleDerivatives d = bicycle_eval_derivatives(state, accel, steer_rate, params);
        state->x += d.dx * dt;
        state->y += d.dy * dt;
        state->theta += d.dtheta * dt;
        state->v += d.dv * dt;
        state->delta += d.ddelta * dt;
    }
    else if (method == INTEGRATION_EXACT_ARC) {
        /* Метод точної кругової дуги для постійної кривини на відрізку dt */
        double L = params->l_f + params->l_r;
        double beta = atan((params->l_r / L) * tan(state->delta));
        double omega = (state->v / L) * tan(state->delta) * cos(beta);
        double delta_theta = omega * dt;

        if (fabs(omega) > 1e-6) {
            double R_cg = state->v / omega;
            state->x += R_cg * (sin(state->theta + beta + delta_theta) - sin(state->theta + beta));
            state->y += R_cg * (-cos(state->theta + beta + delta_theta) + cos(state->theta + beta));
        } else {
            /* Прямолінійний рух при нульовій кутовій швидкості */
            state->x += state->v * cos(state->theta + beta) * dt;
            state->y += state->v * sin(state->theta + beta) * dt;
        }
        state->theta += delta_theta;
        state->v += accel * dt;
        state->delta += steer_rate * dt;
    }
    else if (method == INTEGRATION_RK4) {
        /* Класичний метод Рунге-Кутти 4-го порядку */
        BicycleDerivatives k1 = bicycle_eval_derivatives(state, accel, steer_rate, params);

        BicycleState s2 = {
            .x = state->x + 0.5 * dt * k1.dx,
            .y = state->y + 0.5 * dt * k1.dy,
            .theta = state->theta + 0.5 * dt * k1.dtheta,
            .v = state->v + 0.5 * dt * k1.dv,
            .delta = state->delta + 0.5 * dt * k1.ddelta
        };
        BicycleDerivatives k2 = bicycle_eval_derivatives(&s2, accel, steer_rate, params);

        BicycleState s3 = {
            .x = state->x + 0.5 * dt * k2.dx,
            .y = state->y + 0.5 * dt * k2.dy,
            .theta = state->theta + 0.5 * dt * k2.dtheta,
            .v = state->v + 0.5 * dt * k2.dv,
            .delta = state->delta + 0.5 * dt * k2.ddelta
        };
        BicycleDerivatives k3 = bicycle_eval_derivatives(&s3, accel, steer_rate, params);

        BicycleState s4 = {
            .x = state->x + dt * k3.dx,
            .y = state->y + dt * k3.dy,
            .theta = state->theta + dt * k3.dtheta,
            .v = state->v + dt * k3.dv,
            .delta = state->delta + dt * k3.ddelta
        };
        BicycleDerivatives k4 = bicycle_eval_derivatives(&s4, accel, steer_rate, params);

        state->x += (dt / 6.0) * (k1.dx + 2.0 * k2.dx + 2.0 * k3.dx + k4.dx);
        state->y += (dt / 6.0) * (k1.dy + 2.0 * k2.dy + 2.0 * k3.dy + k4.dy);
        state->theta += (dt / 6.0) * (k1.dtheta + 2.0 * k2.dtheta + 2.0 * k3.dtheta + k4.dtheta);
        state->v += (dt / 6.0) * (k1.dv + 2.0 * k2.dv + 2.0 * k3.dv + k4.dv);
        state->delta += (dt / 6.0) * (k1.ddelta + 2.0 * k2.ddelta + 2.0 * k3.ddelta + k4.ddelta);
    }

    /* Фінальна нормалізація стану */
    state->theta = normalize_angle(state->theta);
    state->delta = clamp_value(state->delta, -params->max_steer, params->max_steer);

    return true;
}
