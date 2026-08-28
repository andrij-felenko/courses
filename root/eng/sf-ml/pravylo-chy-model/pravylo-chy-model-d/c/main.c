#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SPEED_RAD_S        150.0f
#define MAX_ACCEL_RAD_S2       300.0f
#define MAX_CURRENT_AMPS        15.0f
#define MAX_TEMP_CELSIUS        80.0f
#define CONFIDENCE_THRESHOLD     0.75f

typedef struct {
    float speed_rad_s;
    float current_amps;
    float temperature_c;
} Telemetry_t;

typedef struct {
    float proposed_speed;
    float confidence;
    bool  inference_valid;
} MlProposal_t;

typedef enum {
    SOURCE_ML_OPTIMAL    = 0,
    SOURCE_RULE_CLAMPED  = 1,
    SOURCE_RULE_FALLBACK = 2
} DecisionSource_t;

typedef struct {
    float last_applied_speed;
    uint32_t fallback_counter;
    bool  emergency_state;
} ArbiterState_t;

typedef struct {
    float            applied_speed;
    DecisionSource_t source;
} ArbiterResult_t;

ArbiterResult_t Arbiter_ProcessStep(
    ArbiterState_t*       state,
    const Telemetry_t*    telem,
    const MlProposal_t*   ml,
    float                 dt_sec
) {
    ArbiterResult_t result;
    float safe_speed = 0.0f;

    // 1. Апаратний захист від критичного перегріву та надструму (Hard Rules)
    if (telem->temperature_c >= MAX_TEMP_CELSIUS || telem->current_amps >= MAX_CURRENT_AMPS) {
        state->emergency_state = true;
        state->fallback_counter++;
        result.applied_speed = 0.0f; // Екстрена зупинка
        result.source = SOURCE_RULE_FALLBACK;
        state->last_applied_speed = 0.0f;
        return result;
    }

    // 2. Верифікація статусу та впевненості нейромережі
    bool ml_acceptable = ml->inference_valid && 
                         (ml->confidence >= CONFIDENCE_THRESHOLD) &&
                         (!state->emergency_state);

    if (ml_acceptable) {
        float target = ml->proposed_speed;

        // 3. Обмеження абсолютного значення швидкості (Safety Envelope)
        if (target > MAX_SPEED_RAD_S) {
            target = MAX_SPEED_RAD_S;
        } else if (target < -MAX_SPEED_RAD_S) {
            target = -MAX_SPEED_RAD_S;
        }

        // 4. Обмеження темпу наростання швидкості (Slew Rate / Прискорення)
        float max_delta = MAX_ACCEL_RAD_S2 * dt_sec;
        float actual_delta = target - state->last_applied_speed;

        if (actual_delta > max_delta) {
            safe_speed = state->last_applied_speed + max_delta;
            result.source = SOURCE_RULE_CLAMPED;
        } else if (actual_delta < -max_delta) {
            safe_speed = state->last_applied_speed - max_delta;
            result.source = SOURCE_RULE_CLAMPED;
        } else {
            safe_speed = target;
            result.source = SOURCE_ML_OPTIMAL;
        }
    } else {
        // 5. Детермінований Fallback: плавне гальмування до повної зупинки
        float max_delta = MAX_ACCEL_RAD_S2 * dt_sec;
        if (state->last_applied_speed > max_delta) {
            safe_speed = state->last_applied_speed - max_delta;
        } else if (state->last_applied_speed < -max_delta) {
            safe_speed = state->last_applied_speed + max_delta;
        } else {
            safe_speed = 0.0f;
        }
        state->fallback_counter++;
        result.source = SOURCE_RULE_FALLBACK;
    }

    state->last_applied_speed = safe_speed;
    result.applied_speed = safe_speed;
    return result;
}
