#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_MISSION_ITEMS 32
#define DEG_TO_RAD (3.14159265358979323846f / 180.0f)
#define EARTH_RADIUS_M 6371000.0f

typedef enum {
    MISSION_TYPE_WAYPOINT,
    MISSION_TYPE_STATION_KEEP,
    MISSION_TYPE_ACTUATE,
    MISSION_TYPE_WAIT_CONDITION,
    MISSION_TYPE_SAFE_PARK
} MissionType;

typedef enum {
    ENGINE_IDLE,
    ENGINE_NAVIGATING,
    ENGINE_STATION_KEEPING,
    ENGINE_ACTUATING,
    ENGINE_WAITING,
    ENGINE_COMPLETED,
    ENGINE_FAILSAFE
} EngineState;

typedef struct {
    MissionType type;
    int32_t lat_e7;         // широта * 1e7 (для вейпойнтів)
    int32_t lon_e7;         // довгота * 1e7
    float target_param;     // радіус / поріг / кут
    uint32_t duration_ms;   // тривалість витримки / тайм-аут
    uint8_t actuator_mask;  // бітова маска реле/клапанів
} MissionItem;

typedef struct {
    int32_t lat_e7;
    int32_t lon_e7;
    float yaw_rad;
    float speed_mps;
    float battery_v;
    float roll_deg;
    float pitch_deg;
    float sensor_val;
} VehicleState;

typedef struct {
    float steering_norm;    // -1.0 (ліворуч) .. +1.0 (праворуч)
    float throttle_norm;    // -1.0 (реверс) .. +1.0 (вперед)
    uint8_t actuator_out;   // стан реле/клапанів
} VehicleControlOutput;

typedef struct {
    MissionItem items[MAX_MISSION_ITEMS];
    uint8_t item_count;
    uint8_t current_index;
    EngineState state;
    uint32_t state_enter_time_ms;
    uint32_t last_thrust_pulse_ms;
    bool thrust_pulse_active;
} MissionEngine;

// Нормалізація кута у діапазон [-pi, +pi]
static float wrap_pi(float angle_rad) {
    while (angle_rad > 3.14159265358979323846f) angle_rad -= 2.0f * 3.14159265358979323846f;
    while (angle_rad < -3.14159265358979323846f) angle_rad += 2.0f * 3.14159265358979323846f;
    return angle_rad;
}

// Розрахунок пласкої відстані та азимута до цілі
static void calc_bearing_distance(int32_t lat1, int32_t lon1, 
                                  int32_t lat2, int32_t lon2, 
                                  float* dist_m, float* bearing_rad) {
    float d_lat = (float)(lat2 - lat1) * 1e-7f * DEG_TO_RAD;
    float d_lon = (float)(lon2 - lon1) * 1e-7f * DEG_TO_RAD;
    float lat_mean = (float)(lat1 + lat2) * 0.5f * 1e-7f * DEG_TO_RAD;

    float north = d_lat * EARTH_RADIUS_M;
    float east = d_lon * EARTH_RADIUS_M * cosf(lat_mean);

    *dist_m = sqrtf(north * north + east * east);
    *bearing_rad = atan2f(east, north);
}

void mission_engine_init(MissionEngine* engine) {
    engine->item_count = 0;
    engine->current_index = 0;
    engine->state = ENGINE_IDLE;
    engine->state_enter_time_ms = 0;
    engine->last_thrust_pulse_ms = 0;
    engine->thrust_pulse_active = false;
}

bool mission_engine_load_item(MissionEngine* engine, const MissionItem* item) {
    if (engine->item_count >= MAX_MISSION_ITEMS) return false;
    engine->items[engine->item_count++] = *item;
    return true;
}

void mission_engine_start(MissionEngine* engine, uint32_t now_ms) {
    if (engine->item_count == 0) {
        engine->state = ENGINE_COMPLETED;
        return;
    }
    engine->current_index = 0;
    engine->state_enter_time_ms = now_ms;
    engine->state = ENGINE_NAVIGATING;
}

void mission_engine_update(MissionEngine* engine, 
                           const VehicleState* state, 
                           uint32_t now_ms, 
                           VehicleControlOutput* out) {
    out->steering_norm = 0.0f;
    out->throttle_norm = 0.0f;
    out->actuator_out = 0;

    // Глобальний Failsafe захист від перекидання та критичного розряду
    if (fabsf(state->roll_deg) > 30.0f || fabsf(state->pitch_deg) > 25.0f || state->battery_v < 10.5f) {
        engine->state = ENGINE_FAILSAFE;
    }

    if (engine->state == ENGINE_FAILSAFE) {
        out->throttle_norm = 0.0f;
        out->steering_norm = 0.0f;
        out->actuator_out = 0;
        return;
    }

    if (engine->state == ENGINE_IDLE || engine->state == ENGINE_COMPLETED) {
        return;
    }

    if (engine->current_index >= engine->item_count) {
        engine->state = ENGINE_COMPLETED;
        return;
    }

    const MissionItem* cur = &engine->items[engine->current_index];

    switch (cur->type) {
        case MISSION_TYPE_WAYPOINT: {
            float dist_m = 0.0f, bearing_rad = 0.0f;
            calc_bearing_distance(state->lat_e7, state->lon_e7, 
                                  cur->lat_e7, cur->lon_e7, 
                                  &dist_m, &bearing_rad);

            float heading_err = wrap_pi(bearing_rad - state->yaw_rad);

            // Керування неголономним наведенням (Pure Pursuit / P-контролер курсу)
            out->steering_norm = heading_err * 1.2f;
            if (out->steering_norm > 1.0f) out->steering_norm = 1.0f;
            if (out->steering_norm < -1.0f) out->steering_norm = -1.0f;

            // Пригальмовування на крутих поворотах
            float speed_scale = cosf(heading_err);
            if (speed_scale < 0.2f) speed_scale = 0.2f;
            out->throttle_norm = 0.6f * speed_scale;

            // Перевірка досягнення радіуса прийняття точки
            if (dist_m <= cur->target_param) {
                engine->current_index++;
                engine->state_enter_time_ms = now_ms;
            }
            break;
        }

        case MISSION_TYPE_STATION_KEEP: {
            float dist_m = 0.0f, bearing_rad = 0.0f;
            calc_bearing_distance(state->lat_e7, state->lon_e7, 
                                  cur->lat_e7, cur->lon_e7, 
                                  &dist_m, &bearing_rad);

            float r_inner = cur->target_param;
            float r_outer = r_inner * 2.0f;

            // Віртуальний якір: орієнтація на ціль + імпульсне повернення
            float heading_err = wrap_pi(bearing_rad - state->yaw_rad);
            out->steering_norm = heading_err * 1.5f;
            if (out->steering_norm > 1.0f) out->steering_norm = 1.0f;
            if (out->steering_norm < -1.0f) out->steering_norm = -1.0f;

            if (dist_m > r_outer && !engine->thrust_pulse_active) {
                engine->thrust_pulse_active = true;
                engine->last_thrust_pulse_ms = now_ms;
            }

            if (engine->thrust_pulse_active) {
                out->throttle_norm = 0.5f; // імпульс повернення
                if (dist_m <= r_inner || (now_ms - engine->last_thrust_pulse_ms) > 4000) {
                    engine->thrust_pulse_active = false;
                }
            } else {
                out->throttle_norm = 0.0f; // дрейф у мертвій зоні
            }

            // Перевірка тайм-ауту утримання станції
            if (cur->duration_ms > 0 && (now_ms - engine->state_enter_time_ms) >= cur->duration_ms) {
                engine->thrust_pulse_active = false;
                engine->current_index++;
                engine->state_enter_time_ms = now_ms;
            }
            break;
        }

        case MISSION_TYPE_ACTUATE: {
            out->throttle_norm = 0.0f;
            out->steering_norm = 0.0f;
            out->actuator_out = cur->actuator_mask;

            if ((now_ms - engine->state_enter_time_ms) >= cur->duration_ms) {
                out->actuator_out = 0;
                engine->current_index++;
                engine->state_enter_time_ms = now_ms;
            }
            break;
        }

        case MISSION_TYPE_WAIT_CONDITION: {
            out->throttle_norm = 0.0f;
            out->steering_norm = 0.0f;

            // Очікування умови або вичерпання загального тайм-ауту
            bool condition_met = (state->sensor_val >= cur->target_param);
            bool timeout = (cur->duration_ms > 0 && (now_ms - engine->state_enter_time_ms) >= cur->duration_ms);

            if (condition_met || timeout) {
                engine->current_index++;
                engine->state_enter_time_ms = now_ms;
            }
            break;
        }

        case MISSION_TYPE_SAFE_PARK: {
            out->throttle_norm = 0.0f;
            out->steering_norm = 0.0f;
            out->actuator_out = 0;
            engine->state = ENGINE_COMPLETED;
            break;
        }
    }
}
