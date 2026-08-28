/* servo_controller.h / servo_controller.c — Повний каскадний серворегулятор на C */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SERVO_PI 3.14159265358979323846f

typedef struct {
    /* Обмеження руху */
    float max_velocity;      /* рад/с */
    float max_acceleration;  /* рад/с² */
    float max_current;       /* Ампери */
    float max_voltage;       /* Вольти (напруга живлення моста) */

    /* Коефіцієнти контурів */
    float kp_pos;            /* Контур положення: 1/с */
    float kp_vel;            /* Контур швидкості: А/(рад/с) */
    float ki_vel;            /* Інтегратор швидкості: А/(рад) */
    float kp_curr;           /* Контур струму: В/А */
    float ki_curr;           /* Інтегратор струму: В/(А·с) */

    /* Фільтрація швидкості */
    float vel_filter_cutoff; /* Гц (частота зрізу фільтра швидкості) */

    /* Параметри прямого випередження (Feedforward) */
    float inertia_j;         /* кг·м² */
    float torque_const_kt;   /* Н·м/А */
    float friction_coulomb;  /* Н·м (кулонівське тертя) */
    float friction_viscous;  /* Н·м/(рад/с) */
    float friction_stiction; /* Н·м (додатковий зривний момент) */
    float gravity_mass_arm;  /* Н·м (m · g · L_cm) */

    /* Параметри мертвої зони та гістерезису */
    float deadband_enter;    /* рад (поріг захоплення в спокій) */
    float deadband_exit;     /* рад (поріг виходу з режиму спокою) */
    float still_velocity;    /* рад/с (поріг нульової швидкості) */
} ServoConfig;

typedef struct {
    /* Генератор профілю руху */
    float target_pos;        /* Кінцева ціль, рад */
    float profile_pos;       /* Поточне завдання положення θ*, рад */
    float profile_vel;       /* Поточне завдання швидкості ω*, рад/с */
    float profile_acc;       /* Поточне завдання прискорення α*, рад/с² */
    bool  profile_active;

    /* Стан фільтра та інтеграторів */
    float filtered_vel;      /* Відфільтрована швидкість, рад/с */
    float integral_vel;      /* Інтеграл швидкості, А */
    float integral_curr;     /* Інтеграл струму, В */
    float prev_meas_pos;     /* Для чисельного диференціювання швидкості */

    /* Стан зони нечутливості */
    bool in_position;

    /* Вихідні змінні для діагностики */
    float cmd_voltage;       /* Вихідна напруга на мотор, В */
    float cmd_current;       /* Цільовий струм, А */
    float cmd_velocity;      /* Цільова швидкість, рад/с */
} ServoState;

static inline float servo_clamp(float val, float min_v, float max_v) {
    if (val > max_v) return max_v;
    if (val < min_v) return min_v;
    return val;
}

static inline float servo_sgn(float val) {
    if (val > 1e-4f) return 1.0f;
    if (val < -1e-4f) return -1.0f;
    return 0.0f;
}

void servo_init(ServoState *state, float init_pos) {
    state->target_pos = init_pos;
    state->profile_pos = init_pos;
    state->profile_vel = 0.0f;
    state->profile_acc = 0.0f;
    state->profile_active = false;
    state->filtered_vel = 0.0f;
    state->integral_vel = 0.0f;
    state->integral_curr = 0.0f;
    state->prev_meas_pos = init_pos;
    state->in_position = true;
    state->cmd_voltage = 0.0f;
    state->cmd_current = 0.0f;
    state->cmd_velocity = 0.0f;
}

void servo_set_target(ServoState *state, float new_target) {
    state->target_pos = new_target;
    state->profile_active = true;
    state->in_position = false;
}

/* Оновлення траєкторії руху (Online Profile Step) */
static void servo_update_profile(const ServoConfig *cfg, ServoState *state, float dt) {
    if (!state->profile_active) {
        state->profile_vel = 0.0f;
        state->profile_acc = 0.0f;
        return;
    }

    float pos_error = state->target_pos - state->profile_pos;
    float dist = fabsf(pos_error);
    float dir = servo_sgn(pos_error);

    if (dist < 1e-5f && fabsf(state->profile_vel) < 1e-4f) {
        state->profile_pos = state->target_pos;
        state->profile_vel = 0.0f;
        state->profile_acc = 0.0f;
        state->profile_active = false;
        return;
    }

    /* Дистанція, необхідна для повної зупинки з поточної швидкості: s = v² / (2a) */
    float stop_dist = (state->profile_vel * state->profile_vel) / (2.0f * cfg->max_acceleration);

    if (dist <= stop_dist) {
        /* Фаза гальмування: максимальне сповільнення до цілі */
        state->profile_acc = -dir * cfg->max_acceleration;
    } else {
        /* Фаза розгону або руху на граничній швидкості */
        if (fabsf(state->profile_vel) < cfg->max_velocity) {
            state->profile_acc = dir * cfg->max_acceleration;
        } else {
            state->profile_acc = 0.0f;
        }
    }

    /* Чисельне інтегрування Ейлера для профілю */
    state->profile_vel += state->profile_acc * dt;
    state->profile_vel = servo_clamp(state->profile_vel, -cfg->max_velocity, cfg->max_velocity);
    state->profile_pos += state->profile_vel * dt;
}

/* Головний такт каскадного керування */
float servo_update(const ServoConfig *cfg, ServoState *state,
                   float meas_pos, float meas_curr, float dt) {
    /* 1. Оновлення профілю траєкторії */
    servo_update_profile(cfg, state, dt);

    /* 2. Обчислення швидкості за показами енкодера з IIR-фільтрацією */
    float raw_vel = (meas_pos - state->prev_meas_pos) / dt;
    state->prev_meas_pos = meas_pos;

    float tau_filter = 1.0f / (2.0f * SERVO_PI * cfg->vel_filter_cutoff);
    float alpha = dt / (tau_filter + dt);
    state->filtered_vel += alpha * (raw_vel - state->filtered_vel);
    float meas_vel = state->filtered_vel;

    /* 3. Перевірка логіки зони нечутливості та гістерезису */
    float target_err = state->target_pos - meas_pos;
    float abs_err = fabsf(target_err);
    float abs_vel = fabsf(meas_vel);

    if (!state->in_position) {
        if (!state->profile_active && abs_err <= cfg->deadband_enter && abs_vel <= cfg->still_velocity) {
            state->in_position = true;
        }
    } else {
        if (abs_err > cfg->deadband_exit) {
            state->in_position = false;
        }
    }

    /* 4. Зовнішній контур: Регулятор положення (P + Velocity Feedforward) */
    float vel_cmd = 0.0f;
    if (state->in_position) {
        /* У стані фіксації демпфуємо рух без накопичення похибки */
        vel_cmd = -0.1f * meas_vel;
    } else {
        float pos_err = state->profile_pos - meas_pos;
        vel_cmd = (cfg->kp_pos * pos_err) + state->profile_vel;
    }
    vel_cmd = servo_clamp(vel_cmd, -cfg->max_velocity, cfg->max_velocity);
    state->cmd_velocity = vel_cmd;

    /* 5. Середній контур: Регулятор швидкості (PI + Anti-Windup) */
    float vel_err = vel_cmd - meas_vel;
    float p_curr_cmd = cfg->kp_vel * vel_err;

    /* Інтегрування швидкості (лише коли не в зоні спокою) */
    if (!state->in_position) {
        state->integral_vel += (cfg->ki_vel * vel_err) * dt;
        /* Anti-windup clamping для інтеграла */
        state->integral_vel = servo_clamp(state->integral_vel, -cfg->max_current, cfg->max_current);
    }

    /* Пряме випередження інерції (J · α*) */
    float accel_ff_torque = cfg->inertia_j * state->profile_acc;
    float accel_ff_curr = accel_ff_torque / cfg->torque_const_kt;

    /* Пряме випередження тертя (Stiction + Coulomb + Viscous) */
    float fric_torque = (servo_sgn(vel_cmd) * cfg->friction_coulomb) + (cfg->friction_viscous * vel_cmd);
    if (fabsf(meas_vel) < cfg->still_velocity && fabsf(vel_cmd) > 1e-3f) {
        fric_torque += servo_sgn(vel_cmd) * cfg->friction_stiction;
    }
    float fric_ff_curr = fric_torque / cfg->torque_const_kt;

    /* Пряме випередження гравітаційного моменту: τ_grav = m·g·L·cos(θ) */
    float grav_torque = cfg->gravity_mass_arm * cosf(meas_pos);
    float grav_ff_curr = grav_torque / cfg->torque_const_kt;

    /* Сумарне завдання струму */
    float total_curr_cmd = p_curr_cmd + state->integral_vel + accel_ff_curr + fric_ff_curr + grav_ff_curr;
    total_curr_cmd = servo_clamp(total_curr_cmd, -cfg->max_current, cfg->max_current);
    state->cmd_current = total_curr_cmd;

    /* 6. Внутрішній контур: Регулятор струму (PI) */
    float curr_err = total_curr_cmd - meas_curr;
    float p_volt_cmd = cfg->kp_curr * curr_err;
    state->integral_curr += (cfg->ki_curr * curr_err) * dt;
    state->integral_curr = servo_clamp(state->integral_curr, -cfg->max_voltage, cfg->max_voltage);

    float total_volt_cmd = p_volt_cmd + state->integral_curr;
    total_volt_cmd = servo_clamp(total_volt_cmd, -cfg->max_voltage, cfg->max_voltage);
    state->cmd_voltage = total_volt_cmd;

    /* Повертаємо напругу керування ШІМ */
    return total_volt_cmd;
}
