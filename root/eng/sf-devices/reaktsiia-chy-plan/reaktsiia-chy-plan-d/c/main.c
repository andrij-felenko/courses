#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <math.h>

#define CONTROL_DT            0.001f  // 1 мс крок швидкого контуру (1 кГц)
#define MAX_EMERGENCY_DECEL   12.0f   // м/с^2 максимальне аварійне гальмування
#define SAFE_PROXIMITY_M      0.25f   // Поріг реактивного спрацювання (25 см)
#define BLEND_TIME_S          0.15f   // 150 мс інтервал злиття (Bumpless Transfer)

typedef enum {
    MODE_FOLLOW_PLAN,
    MODE_REACTIVE_OVERRIDE,
    MODE_BLEND_RECOVERY
} arbiter_mode_t;

typedef struct {
    float pos;
    float vel;
} traj_point_t;

typedef struct {
    traj_point_t slots[2];
    atomic_int active_slot;
} double_buf_t;

typedef struct {
    float actual_pos;
    float actual_vel;
    arbiter_mode_t mode;
    double_buf_t plan_input;
    
    // Параметри для інтерполяції злиття
    float blend_start_p;
    float blend_start_v;
    float blend_t;
    
    atomic_bool replan_flag;
} hybrid_arbiter_t;

void arbiter_init(hybrid_arbiter_t *arb) {
    arb->actual_pos = 0.0f;
    arb->actual_vel = 0.0f;
    arb->mode = MODE_FOLLOW_PLAN;
    atomic_init(&arb->plan_input.active_slot, 0);
    atomic_init(&arb->replan_flag, false);
    arb->blend_t = 0.0f;
}

// ── Повільний шар: запис нової уставки планувальником (10–50 Гц) ──────────────
void arbiter_push_plan_point(hybrid_arbiter_t *arb, float target_pos, float target_vel) {
    int active = atomic_load_explicit(&arb->plan_input.active_slot, memory_order_relaxed);
    int next = 1 - active;
    
    arb->plan_input.slots[next].pos = target_pos;
    arb->plan_input.slots[next].vel = target_vel;
    atomic_store_explicit(&arb->plan_input.active_slot, next, memory_order_release);
}

// ── Швидкий шар: 1 кГц детерміністичний крок із ISR таймера ──────────────────
float arbiter_fast_step(hybrid_arbiter_t *arb, float distance_sensor_m) {
    bool obstacle_near = (distance_sensor_m < SAFE_PROXIMITY_M);
    
    // 1. Пріоритетне реактивне перехоплення (Subsumption)
    if (obstacle_near && arb->mode != MODE_REACTIVE_OVERRIDE) {
        arb->mode = MODE_REACTIVE_OVERRIDE;
        atomic_store_explicit(&arb->replan_flag, true, memory_order_release);
    }
    
    float cmd_vel = 0.0f;
    
    switch (arb->mode) {
        case MODE_REACTIVE_OVERRIDE: {
            // Екстрене гальмування рефлекторного шару
            if (arb->actual_vel > 0.0f) {
                arb->actual_vel -= MAX_EMERGENCY_DECEL * CONTROL_DT;
                if (arb->actual_vel < 0.0f) arb->actual_vel = 0.0f;
            } else if (arb->actual_vel < 0.0f) {
                arb->actual_vel += MAX_EMERGENCY_DECEL * CONTROL_DT;
                if (arb->actual_vel > 0.0f) arb->actual_vel = 0.0f;
            }
            
            arb->actual_pos += arb->actual_vel * CONTROL_DT;
            cmd_vel = arb->actual_vel;
            
            // Якщо загроза минула й вісь зупинилася — переходимо до згладжування
            if (!obstacle_near && fabsf(arb->actual_vel) < 0.01f) {
                arb->mode = MODE_BLEND_RECOVERY;
                arb->blend_start_p = arb->actual_pos;
                arb->blend_start_v = arb->actual_vel;
                arb->blend_t = 0.0f;
            }
            break;
        }
        
        case MODE_BLEND_RECOVERY: {
            // Кубічний сплайн Ерміта для безударного переходу
            arb->blend_t += CONTROL_DT / BLEND_TIME_S;
            int active = atomic_load_explicit(&arb->plan_input.active_slot, memory_order_acquire);
            traj_point_t target = arb->plan_input.slots[active];
            
            if (arb->blend_t >= 1.0f) {
                arb->mode = MODE_FOLLOW_PLAN;
                arb->actual_pos = target.pos;
                arb->actual_vel = target.vel;
                cmd_vel = target.vel;
            } else {
                float s = arb->blend_t;
                float h00 = 2.0f * s * s * s - 3.0f * s * s + 1.0f;
                float h10 = s * s * s - 2.0f * s * s + s;
                float h01 = -2.0f * s * s * s + 3.0f * s * s;
                float h11 = s * s * s - s * s;
                
                float p_blend = h00 * arb->blend_start_p +
                                h10 * arb->blend_start_v * BLEND_TIME_S +
                                h01 * target.pos +
                                h11 * target.vel * BLEND_TIME_S;
                
                cmd_vel = (p_blend - arb->actual_pos) / CONTROL_DT;
                arb->actual_pos = p_blend;
                arb->actual_vel = cmd_vel;
            }
            break;
        }
        
        case MODE_FOLLOW_PLAN:
        default: {
            int active = atomic_load_explicit(&arb->plan_input.active_slot, memory_order_acquire);
            traj_point_t target = arb->plan_input.slots[active];
            arb->actual_pos = target.pos;
            arb->actual_vel = target.vel;
            cmd_vel = target.vel;
            break;
        }
    }
    
    return cmd_vel; // Видача на PWM-генератор драйвера мотора
}
