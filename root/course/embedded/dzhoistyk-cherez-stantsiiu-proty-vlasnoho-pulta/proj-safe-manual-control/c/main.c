#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RC_DEADBAND_NORM            50      // 5% від діапазону [-1000..1000]
#define GCS_TIMEOUT_DEGRADE_MS      250     // Поріг м'якої нейтралізації (мс)
#define GCS_TIMEOUT_FAILSAFE_MS     1000    // Поріг повного аварійного режиму (мс)
#define MAX_AXIS_SLEW_PER_SEC       4000.0f // Максимальна швидкість зміни (одиниць/с)

typedef enum {
    SOURCE_NONE = 0,
    SOURCE_DIRECT_RC,
    SOURCE_GCS_MANUAL
} ControlSource;

typedef enum {
    STATE_DISARMED = 0,
    STATE_RC_ACTIVE,
    STATE_GCS_ACTIVE,
    STATE_GCS_DEGRADED,
    STATE_FAILSAFE
} ArbiterState;

typedef struct {
    int16_t roll;      // [-1000 .. 1000] (крен: позитивний — вправо)
    int16_t pitch;     // [-1000 .. 1000] (тангаж: позитивний — вперед)
    int16_t throttle;  // [0 .. 1000]      (тяга)
    int16_t yaw;       // [-1000 .. 1000] (рискання: позитивний — за годинниковою)
    uint16_t buttons;  // Бітова маска кнопок
} ControlAxes;

typedef struct {
    ArbiterState state;
    ControlAxes current_output;
    ControlAxes raw_rc;
    ControlAxes raw_gcs;
    uint32_t last_rc_time_ms;
    uint32_t last_gcs_time_ms;
    bool rc_link_lost;
} SafeControlArbiter;

static int16_t clamp_int16(int16_t val, int16_t min_v, int16_t max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

static bool is_rc_stick_deflected(const ControlAxes *rc) {
    if (rc->roll < -RC_DEADBAND_NORM || rc->roll > RC_DEADBAND_NORM) return true;
    if (rc->pitch < -RC_DEADBAND_NORM || rc->pitch > RC_DEADBAND_NORM) return true;
    if (rc->yaw < -RC_DEADBAND_NORM || rc->yaw > RC_DEADBAND_NORM) return true;
    // Відхилення газу вище 10% від базового нульового положення
    if (rc->throttle > 100) return true;
    return false;
}

static int16_t apply_slew_rate(int16_t current, int16_t target, float dt_sec) {
    float max_delta = MAX_AXIS_SLEW_PER_SEC * dt_sec;
    float diff = (float)(target - current);
    if (diff > max_delta) return current + (int16_t)max_delta;
    if (diff < -max_delta) return current - (int16_t)max_delta;
    return target;
}

void arbiter_init(SafeControlArbiter *arb) {
    memset(arb, 0, sizeof(SafeControlArbiter));
    arb->state = STATE_DISARMED;
    arb->rc_link_lost = true;
}

void arbiter_feed_direct_rc(SafeControlArbiter *arb, const ControlAxes *rc, uint32_t now_ms) {
    arb->raw_rc = *rc;
    arb->last_rc_time_ms = now_ms;
    arb->rc_link_lost = false;
}

void arbiter_feed_mavlink_manual_control(SafeControlArbiter *arb, 
                                        int16_t x, int16_t y, int16_t z, int16_t r, 
                                        uint16_t buttons, uint32_t now_ms) {
    // MAVLink MANUAL_CONTROL #69: x=pitch, y=roll, z=throttle, r=yaw
    arb->raw_gcs.pitch = clamp_int16(x, -1000, 1000);
    arb->raw_gcs.roll = clamp_int16(y, -1000, 1000);
    arb->raw_gcs.throttle = clamp_int16(z, 0, 1000);
    arb->raw_gcs.yaw = clamp_int16(r, -1000, 1000);
    arb->raw_gcs.buttons = buttons;
    arb->last_gcs_time_ms = now_ms;
}

void arbiter_update(SafeControlArbiter *arb, uint32_t now_ms, float dt_sec) {
    uint32_t gcs_age = now_ms - arb->last_gcs_time_ms;
    uint32_t rc_age = now_ms - arb->last_rc_time_ms;

    if (rc_age > 100) {
        arb->rc_link_lost = true;
    }

    // 1. Апаратний пріоритет прямого пульта
    bool rc_has_control = !arb->rc_link_lost && is_rc_stick_deflected(&arb->raw_rc);

    if (rc_has_control) {
        arb->state = STATE_RC_ACTIVE;
        // Прямий пульт не підлягає штучному slew-rate, щоб зберегти миттєву реакцію
        arb->current_output = arb->raw_rc;
        return;
    }

    // 2. Обробка команд від наземної станції
    if (gcs_age < GCS_TIMEOUT_DEGRADE_MS) {
        arb->state = STATE_GCS_ACTIVE;
        arb->current_output.roll = apply_slew_rate(arb->current_output.roll, arb->raw_gcs.roll, dt_sec);
        arb->current_output.pitch = apply_slew_rate(arb->current_output.pitch, arb->raw_gcs.pitch, dt_sec);
        arb->current_output.yaw = apply_slew_rate(arb->current_output.yaw, arb->raw_gcs.yaw, dt_sec);
        arb->current_output.throttle = apply_slew_rate(arb->current_output.throttle, arb->raw_gcs.throttle, dt_sec);
        arb->current_output.buttons = arb->raw_gcs.buttons;
    } else if (gcs_age < GCS_TIMEOUT_FAILSAFE_MS) {
        // М'яка деградація: нейтралізація кутів, фіксація тяги на рівні зависання (500)
        arb->state = STATE_GCS_DEGRADED;
        arb->current_output.roll = apply_slew_rate(arb->current_output.roll, 0, dt_sec);
        arb->current_output.pitch = apply_slew_rate(arb->current_output.pitch, 0, dt_sec);
        arb->current_output.yaw = apply_slew_rate(arb->current_output.yaw, 0, dt_sec);
        arb->current_output.throttle = apply_slew_rate(arb->current_output.throttle, 500, dt_sec);
    } else {
        // Повний аварійний таймаут
        arb->state = STATE_FAILSAFE;
        arb->current_output.roll = 0;
        arb->current_output.pitch = 0;
        arb->current_output.yaw = 0;
        arb->current_output.throttle = 0;
    }
}
