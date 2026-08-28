#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SOURCE_FAILSAFE    0
#define SOURCE_RC_PILOT    1
#define SOURCE_OFFBOARD    2
#define SOURCE_GCS_MISSION 3
#define SOURCE_COUNT       4
#define SOURCE_NONE        255

typedef struct {
    uint64_t timestamp_us;
    float channels[4]; /* [0]=Roll, [1]=Pitch, [2]=Yaw, [3]=Thrust [0..1] */
    bool valid;
} setpoint_t;

typedef struct {
    uint32_t timeout_us;
    float stick_deadband;
    float max_slew_rate[4]; /* Максимальна швидкість зміни (од/с) */
    bool allow_stick_override;
} source_cfg_t;

typedef struct {
    setpoint_t raw_sp;
    uint64_t last_heartbeat_us;
    source_cfg_t cfg;
    bool is_active;
    bool is_timed_out;
} source_slot_t;

typedef struct {
    source_slot_t slots[SOURCE_COUNT];
    uint8_t active_source;
    uint8_t previous_source;
    setpoint_t output_sp;
    uint64_t last_eval_us;
    uint32_t switch_count;
} arbiter_t;

static float clampf(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

void arbiter_init(arbiter_t *arb) {
    arb->active_source = SOURCE_NONE;
    arb->previous_source = SOURCE_NONE;
    arb->last_eval_us = 0;
    arb->switch_count = 0;
    
    for (int i = 0; i < 4; ++i) {
        arb->output_sp.channels[i] = 0.0f;
    }
    arb->output_sp.valid = false;
    arb->output_sp.timestamp_us = 0;

    for (int i = 0; i < SOURCE_COUNT; ++i) {
        arb->slots[i].raw_sp.valid = false;
        arb->slots[i].last_heartbeat_us = 0;
        arb->slots[i].is_active = false;
        arb->slots[i].is_timed_out = true;
        
        arb->slots[i].cfg.timeout_us = 500000;      /* 500 мс таймаут за замовчуванням */
        arb->slots[i].cfg.stick_deadband = 0.08f;   /* 8% мертва смуга */
        arb->slots[i].cfg.allow_stick_override = true;
        arb->slots[i].cfg.max_slew_rate[0] = 6.0f;  /* Roll: 6.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[1] = 6.0f;  /* Pitch: 6.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[2] = 10.0f; /* Yaw: 10.0 рад/с² */
        arb->slots[i].cfg.max_slew_rate[3] = 3.0f;  /* Thrust: 3.0 (100% за 330 мс) */
    }
}

void arbiter_submit_setpoint(arbiter_t *arb, uint8_t src_id, const setpoint_t *sp, uint64_t now_us) {
    if (src_id >= SOURCE_COUNT || !sp) return;
    arb->slots[src_id].raw_sp = *sp;
    arb->slots[src_id].last_heartbeat_us = now_us;
    arb->slots[src_id].is_active = true;
    arb->slots[src_id].is_timed_out = false;
}

static bool check_stick_deflection(const source_slot_t *slot) {
    if (!slot->is_active || slot->is_timed_out || !slot->raw_sp.valid) return false;
    
    float r = fabsf(slot->raw_sp.channels[0]);
    float p = fabsf(slot->raw_sp.channels[1]);
    float y = fabsf(slot->raw_sp.channels[2]);
    float db = slot->cfg.stick_deadband;
    
    return (r > db) || (p > db) || (y > db);
}

uint8_t arbiter_evaluate(arbiter_t *arb, uint64_t now_us, setpoint_t *out_sp) {
    /* 1. Оновлення таймаутів */
    for (int i = 0; i < SOURCE_COUNT; ++i) {
        source_slot_t *slot = &arb->slots[i];
        if (slot->is_active) {
            uint64_t elapsed = now_us - slot->last_heartbeat_us;
            if (elapsed > slot->cfg.timeout_us) {
                slot->is_timed_out = true;
                slot->is_active = false;
            }
        }
    }

    /* 2. Пріоритетний вибір джерела */
    uint8_t selected = SOURCE_NONE;

    if (arb->slots[SOURCE_FAILSAFE].is_active && !arb->slots[SOURCE_FAILSAFE].is_timed_out) {
        selected = SOURCE_FAILSAFE;
    } else if (arb->slots[SOURCE_RC_PILOT].is_active && !arb->slots[SOURCE_RC_PILOT].is_timed_out) {
        bool sticks_moved = check_stick_deflection(&arb->slots[SOURCE_RC_PILOT]);
        if (sticks_moved) {
            selected = SOURCE_RC_PILOT;
        } else if (arb->slots[SOURCE_OFFBOARD].is_timed_out && arb->slots[SOURCE_GCS_MISSION].is_timed_out) {
            selected = SOURCE_RC_PILOT;
        }
    }

    if (selected == SOURCE_NONE) {
        if (arb->slots[SOURCE_OFFBOARD].is_active && !arb->slots[SOURCE_OFFBOARD].is_timed_out) {
            selected = SOURCE_OFFBOARD;
        }
    }

    if (selected == SOURCE_NONE) {
        if (arb->slots[SOURCE_GCS_MISSION].is_active && !arb->slots[SOURCE_GCS_MISSION].is_timed_out) {
            selected = SOURCE_GCS_MISSION;
        }
    }

    if (selected != arb->active_source) {
        arb->previous_source = arb->active_source;
        arb->active_source = selected;
        arb->switch_count++;
    }

    /* 3. Безударна фільтрація швидкості зміни (Slew Rate) */
    float dt = 0.0025f; /* 400 Гц за замовчуванням */
    if (arb->last_eval_us > 0 && now_us > arb->last_eval_us) {
        dt = (float)(now_us - arb->last_eval_us) * 1e-6f;
        if (dt > 0.1f) dt = 0.1f;
    }
    arb->last_eval_us = now_us;

    if (selected != SOURCE_NONE && arb->slots[selected].raw_sp.valid) {
        const setpoint_t *target = &arb->slots[selected].raw_sp;
        for (int i = 0; i < 4; ++i) {
            float target_val = target->channels[i];
            float current_val = arb->output_sp.channels[i];
            float max_rate = arb->slots[selected].cfg.max_slew_rate[i];
            float max_delta = max_rate * dt;

            float delta = target_val - current_val;
            float clamped_delta = clampf(delta, -max_delta, max_delta);
            arb->output_sp.channels[i] = current_val + clamped_delta;
        }
        arb->output_sp.valid = true;
    } else {
        for (int i = 0; i < 3; ++i) {
            arb->output_sp.channels[i] = 0.0f;
        }
        arb->output_sp.channels[3] = 0.0f;
        arb->output_sp.valid = false;
    }

    arb->output_sp.timestamp_us = now_us;
    if (out_sp) {
        *out_sp = arb->output_sp;
    }

    return selected;
}

int main(void) {
    arbiter_t arb;
    arbiter_init(&arb);
    uint64_t now = 1000000; /* 1.0 c */

    printf("=== СИМУЛЯЦІЯ ДИСПЕТЧЕРА ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n");

    /* 1. Автономний режим: комп'ютер Offboard подає крен 20° (0.35 рад) */
    setpoint_t offboard_sp = {
        .timestamp_us = now,
        .channels = {0.35f, 0.0f, 0.0f, 0.55f},
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_OFFBOARD, &offboard_sp, now);

    setpoint_t out;
    uint8_t src = arbiter_evaluate(&arb, now, &out);
    printf("[1.00s] Стан: Автономія Offboard | Джерело: %u (Offboard=2) | Roll: %.3f rad, Thrust: %.2f\n", 
           src, out.channels[0], out.channels[3]);

    /* 2. Пілот бачить перешкоду й різко штовхає тангаж на 45° (0.78 рад) */
    now += 50000; /* +50 мс */
    setpoint_t rc_sp = {
        .timestamp_us = now,
        .channels = {0.0f, 0.78f, 0.0f, 0.70f},
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_RC_PILOT, &rc_sp, now);
    src = arbiter_evaluate(&arb, now, &out);
    printf("[1.05s] Пілот штовхнув стік! Джерело: %u (RC_PILOT=1) | Pitch out: %.3f (початок згладжування)\n", 
           src, out.channels[1]);

    /* Кроки роботи лімітера Slew-Rate */
    for (int step = 0; step < 4; ++step) {
        now += 25000; /* +25 мс */
        arbiter_submit_setpoint(&arb, SOURCE_RC_PILOT, &rc_sp, now);
        arbiter_evaluate(&arb, now, &out);
        printf("  [+25ms] Slew-rate динаміка | Pitch out: %.3f rad (ціль: 0.780)\n", out.channels[1]);
    }

    /* 3. Спрацьовує аварійний автомат Failsafe (критичний розряд батареї) */
    now += 10000;
    setpoint_t fs_sp = {
        .timestamp_us = now,
        .channels = {0.0f, 0.0f, 0.0f, 0.30f}, /* Горизонт 0°, спуск */
        .valid = true
    };
    arbiter_submit_setpoint(&arb, SOURCE_FAILSAFE, &fs_sp, now);
    src = arbiter_evaluate(&arb, now, &out);
    printf("\n[1.16s] ТРИВОГА FAILSAFE! Джерело: %u (FAILSAFE=0) | Витіснено всі інші канали!\n", src);

    return 0;
}
