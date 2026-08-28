#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <math.h>

#define CONTROL_FREQ_HZ       1000.0f
#define CONTROL_DT            (1.0f / CONTROL_FREQ_HZ)
#define MAX_ACCEL             5.0f    // м/с^2
#define MAX_DECEL_EMERGENCY   15.0f   // м/с^2 (екстрене рефлекторне гальмування)
#define SAFE_DISTANCE_M       0.30f   // Поріг реактивного спрацювання (30 см)

typedef enum {
    STATE_IDLE,
    STATE_FOLLOWING_PLAN,
    STATE_REACTIVE_OVERRIDE,
    STATE_BLENDING_RECOVERY
} controller_mode_t;

typedef struct {
    float position;
    float velocity;
    float acceleration;
} trajectory_point_t;

typedef struct {
    trajectory_point_t points[2];
    atomic_int active_idx;
} double_buffer_t;

typedef struct {
    // Фізичний стан осі
    float current_position;
    float current_velocity;
    float proximity_distance;
    
    // Стан арбітра
    controller_mode_t mode;
    double_buffer_t plan_buffer;
    
    // Стан рефлекторного гальмування
    float reflex_target_pos;
    
    // Параметри для безударного переходу (Bumpless Transfer)
    float blend_start_pos;
    float blend_start_vel;
    float blend_progress;
    float blend_duration;
    
    // Прапорець для сповіщення планувальника про необхідність репланування
    atomic_bool replan_required;
} hybrid_controller_t;

void hybrid_controller_init(hybrid_controller_t *ctrl) {
    ctrl->current_position = 0.0f;
    ctrl->current_velocity = 0.0f;
    ctrl->proximity_distance = 10.0f;
    ctrl->mode = STATE_IDLE;
    atomic_init(&ctrl->plan_buffer.active_idx, 0);
    atomic_init(&ctrl->replan_required, false);
    ctrl->blend_progress = 0.0f;
    ctrl->blend_duration = 0.20f; // 200 мс інтервал злиття
}

// ── Повільний шар: запис нової уставки фоновим планувальником (10–50 Гц) ─────
void planner_submit_setpoint(hybrid_controller_t *ctrl, const trajectory_point_t *pt) {
    int current_active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_relaxed);
    int next_write = 1 - current_active;
    
    ctrl->plan_buffer.points[next_write] = *pt;
    atomic_store_explicit(&ctrl->plan_buffer.active_idx, next_write, memory_order_release);
}

// ── Швидкий шар: 1 кГц цикл детерміністичного арбітражу та актуації ─────────
float fast_path_control_step(hybrid_controller_t *ctrl, float sensor_proximity) {
    ctrl->proximity_distance = sensor_proximity;
    
    // 1. Миттєва перевірка рефлекторного порогу (Fast Path)
    bool hazard = (ctrl->proximity_distance < SAFE_DISTANCE_M);
    
    if (hazard) {
        if (ctrl->mode != STATE_REACTIVE_OVERRIDE) {
            // Перехоплення керування: придушення плану (Subsumption)
            ctrl->mode = STATE_REACTIVE_OVERRIDE;
            ctrl->reflex_target_pos = ctrl->current_position;
            atomic_store_explicit(&ctrl->replan_required, true, memory_order_release);
        }
    }
    
    // 2. Арбітраж і формування керуючого сигналу
    float cmd_velocity = 0.0f;
    
    switch (ctrl->mode) {
        case STATE_REACTIVE_OVERRIDE: {
            // Рефлекторне екстрене гальмування із заданим темпом сповільнення
            if (ctrl->current_velocity > 0.0f) {
                ctrl->current_velocity -= MAX_DECEL_EMERGENCY * CONTROL_DT;
                if (ctrl->current_velocity < 0.0f) ctrl->current_velocity = 0.0f;
            } else if (ctrl->current_velocity < 0.0f) {
                ctrl->current_velocity += MAX_DECEL_EMERGENCY * CONTROL_DT;
                if (ctrl->current_velocity > 0.0f) ctrl->current_velocity = 0.0f;
            }
            
            ctrl->current_position += ctrl->current_velocity * CONTROL_DT;
            cmd_velocity = ctrl->current_velocity;
            
            // Якщо перешкоду усунуто і привід зупинився — переходимо до злиття
            if (!hazard && fabsf(ctrl->current_velocity) < 0.01f) {
                ctrl->mode = STATE_BLENDING_RECOVERY;
                ctrl->blend_start_pos = ctrl->current_position;
                ctrl->blend_start_vel = ctrl->current_velocity;
                ctrl->blend_progress = 0.0f;
            }
            break;
        }
        
        case STATE_BLENDING_RECOVERY: {
            // Обчислення кубічного сплайна Ерміта для повернення на цільовий план
            ctrl->blend_progress += CONTROL_DT / ctrl->blend_duration;
            
            int active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_acquire);
            trajectory_point_t target = ctrl->plan_buffer.points[active];
            
            if (ctrl->blend_progress >= 1.0f) {
                // Злиття завершено — повний перехід на план
                ctrl->mode = STATE_FOLLOWING_PLAN;
                ctrl->current_position = target.position;
                ctrl->current_velocity = target.velocity;
                cmd_velocity = target.velocity;
            } else {
                float s = ctrl->blend_progress;
                float h00 = 2.0f * s * s * s - 3.0f * s * s + 1.0f;
                float h10 = s * s * s - 2.0f * s * s + s;
                float h01 = -2.0f * s * s * s + 3.0f * s * s;
                float h11 = s * s * s - s * s;
                
                float blended_pos = h00 * ctrl->blend_start_pos +
                                    h10 * ctrl->blend_start_vel * ctrl->blend_duration +
                                    h01 * target.position +
                                    h11 * target.velocity * ctrl->blend_duration;
                
                cmd_velocity = (blended_pos - ctrl->current_position) / CONTROL_DT;
                ctrl->current_position = blended_pos;
                ctrl->current_velocity = cmd_velocity;
            }
            break;
        }
        
        case STATE_FOLLOWING_PLAN:
        default: {
            // Стандартне відпрацювання уставки планувальника
            int active = atomic_load_explicit(&ctrl->plan_buffer.active_idx, memory_order_acquire);
            trajectory_point_t target = ctrl->plan_buffer.points[active];
            
            ctrl->current_position = target.position;
            ctrl->current_velocity = target.velocity;
            cmd_velocity = target.velocity;
            break;
        }
    }
    
    return cmd_velocity;
}
