#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAFETY_DT_SEC          0.010f  // Період такту: 10 мс (100 Гц)
#define SAFETY_HOLD_TICKS      20U     // Час стабілізації: 20 тактів (200 мс)
#define SAFETY_HYST_DIST_M     0.30f   // Просторовий гістерезис: 30 см
#define SAFETY_WATCHDOG_TICKS  50U     // Таймаут планувальника: 500 мс

typedef enum {
    ZONE_OBSERVATION = 0,  // Вільний рух за глобальним планом
    ZONE_WARNING,          // Плавне змішування векторів та гальмування
    ZONE_ESTOP             // Аварійне переривання та повний стоп
} SafetyZone;

typedef struct {
    float x;
    float y;
} Vector2D;

typedef struct {
    float max_accel;        // Максимальне сповільнення, м/с² (типово 2.5)
    float reaction_time;    // Затримка реакції приводу, с (типово 0.05)
    float planner_period;   // Очікуваний період планувальника, с (типово 0.20)
    float stop_margin;      // Фізичний зазор зупинки, м (типово 0.40)
    float warn_buffer;      // Буфер зони застереження, м (типово 0.80)
} SafetyParams;

typedef struct {
    SafetyZone current_zone;
    uint32_t   hold_counter;
    uint32_t   planner_watchdog;
    Vector2D   last_cmd_vel;
    bool       override_active;
    bool       planner_timed_out;
} SafetyArbiter;

static inline float vec2d_len(Vector2D v) {
    return sqrtf(v.x * v.x + v.y * v.y);
}

static inline Vector2D vec2d_scale(Vector2D v, float s) {
    Vector2D out = { v.x * s, v.y * s };
    return out;
}

static inline Vector2D vec2d_add(Vector2D a, Vector2D b) {
    Vector2D out = { a.x + b.x, a.y + b.y };
    return out;
}

void safety_arbiter_init(SafetyArbiter *arb) {
    arb->current_zone = ZONE_OBSERVATION;
    arb->hold_counter = 0;
    arb->planner_watchdog = 0;
    arb->last_cmd_vel.x = 0.0f;
    arb->last_cmd_vel.y = 0.0f;
    arb->override_active = false;
    arb->planner_timed_out = false;
}

void safety_arbiter_feed_planner_heartbeat(SafetyArbiter *arb) {
    arb->planner_watchdog = 0;
    arb->planner_timed_out = false;
}

Vector2D safety_arbiter_update(SafetyArbiter *arb,
                              const SafetyParams *params,
                              Vector2D v_plan,
                              Vector2D v_react,
                              float min_obstacle_dist,
                              float current_speed) {
    // 0. Моніторинг працездатності каналу зв'язку з планувальником
    arb->planner_watchdog++;
    if (arb->planner_watchdog > SAFETY_WATCHDOG_TICKS) {
        arb->planner_timed_out = true;
        // При втраті зв'язку обнуляємо плановий вектор (fail-safe)
        v_plan.x = 0.0f;
        v_plan.y = 0.0f;
    }

    // 1. Кінематичний розрахунок динамічних меж зон
    float safe_speed = (current_speed > 0.0f) ? current_speed : 0.0f;
    float d_brake = (safe_speed * safe_speed) / (2.0f * params->max_accel);
    float r_stop = d_brake + (safe_speed * params->reaction_time) + params->stop_margin;
    float r_warn = r_stop + (safe_speed * params->planner_period) + params->warn_buffer;

    // 2. Визначення миттєвої зони
    SafetyZone target_zone;
    if (min_obstacle_dist <= r_stop) {
        target_zone = ZONE_ESTOP;
    } else if (min_obstacle_dist <= r_warn) {
        target_zone = ZONE_WARNING;
    } else {
        target_zone = ZONE_OBSERVATION;
    }

    // 3. Автомат переходів із просторово-часовим гістерезисом
    if (target_zone > arb->current_zone) {
        // Ескалація: миттєвий перехід без затримок
        arb->current_zone = target_zone;
        arb->hold_counter = SAFETY_HOLD_TICKS;
    } else if (target_zone < arb->current_zone) {
        // Деескалація: вимагаємо просторовий запас та відлік таймера
        bool hyst_cleared = false;
        if (arb->current_zone == ZONE_ESTOP) {
            hyst_cleared = (min_obstacle_dist > (r_stop + SAFETY_HYST_DIST_M));
        } else if (arb->current_zone == ZONE_WARNING) {
            hyst_cleared = (min_obstacle_dist > (r_warn + SAFETY_HYST_DIST_M));
        }

        if (hyst_cleared) {
            if (arb->hold_counter > 0) {
                arb->hold_counter--;
            } else {
                arb->current_zone = target_zone;
                arb->hold_counter = SAFETY_HOLD_TICKS;
            }
        } else {
            arb->hold_counter = SAFETY_HOLD_TICKS;
        }
    } else {
        arb->hold_counter = SAFETY_HOLD_TICKS;
    }

    // 4. Формування вихідного вектора швидкості
    Vector2D cmd_out = { 0.0f, 0.0f };

    switch (arb->current_zone) {
        case ZONE_ESTOP:
            arb->override_active = true;
            cmd_out.x = 0.0f;
            cmd_out.y = 0.0f;
            break;

        case ZONE_WARNING: {
            arb->override_active = false;
            float span = r_warn - r_stop;
            float alpha = (span > 0.01f) ? ((r_warn - min_obstacle_dist) / span) : 1.0f;
            if (alpha < 0.0f) alpha = 0.0f;
            if (alpha > 1.0f) alpha = 1.0f;

            // Змішування: v_cmd = (1 - alpha)*v_plan + alpha*v_react
            Vector2D part_plan = vec2d_scale(v_plan, 1.0f - alpha);
            Vector2D part_react = vec2d_scale(v_react, alpha);
            cmd_out = vec2d_add(part_plan, part_react);

            // Динамічне обмеження швидкості за профілем гальмування
            float dist_to_stop = min_obstacle_dist - r_stop;
            if (dist_to_stop > 0.0f) {
                float v_safe = sqrtf(2.0f * params->max_accel * dist_to_stop);
                float cmd_len = vec2d_len(cmd_out);
                if (cmd_len > v_safe && cmd_len > 0.001f) {
                    cmd_out = vec2d_scale(cmd_out, v_safe / cmd_len);
                }
            } else {
                cmd_out.x = 0.0f;
                cmd_out.y = 0.0f;
            }
            break;
        }

        case ZONE_OBSERVATION:
        default:
            arb->override_active = false;
            cmd_out = v_plan;
            break;
    }

    arb->last_cmd_vel = cmd_out;
    return cmd_out;
}
