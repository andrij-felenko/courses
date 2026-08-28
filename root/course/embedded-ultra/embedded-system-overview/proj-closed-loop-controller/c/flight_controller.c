/* ========================================================================== */
/* flight_controller.c — C-реалізація замкненого контуру керування 1 кГц      */
/* ========================================================================== */
#include <stdint.h>
#include <stdbool.h>

/* Фізичні та алгоритмічні константи */
#define LOOP_PERIOD_SEC    0.001f    /* Період квантування: 1 мс (1 кГц) */
#define FILTER_ALPHA       0.98f     /* Ваговий коефіцієнт гіроскопа */
#define MOTOR_MIN_PWM      1000      /* Мінімальна тривалість імпульсу ШІМ (мкс) */
#define MOTOR_MAX_PWM      2000      /* Максимальна тривалість імпульсу ШІМ (мкс) */
#define MOTOR_IDLE_PWM     1100      /* Шпаруватість холостого ходу */

/* Вектор 3D-величин (кутові швидкості, прискорення, кути) */
typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

/* Стан та коефіцієнти дискретного ПІД-регулятора */
typedef struct {
    float kp;             /* Пропорційний коефіцієнт */
    float ki;             /* Інтегральний коефіцієнт */
    float kd;             /* Диференціальний коефіцієнт */
    float integral;       /* Накопичена сума похибки */
    float prev_error;     /* Похибка на попередньому такті */
    float out_limit;      /* Межа насичення виходу */
    float int_limit;      /* Межа запобігання накопиченню (anti-windup) */
} PidController;

/* Структура стану безпілотного апарата */
typedef struct {
    Vector3f gyro_dps;        /* Кутові швидкості (°/с) */
    Vector3f accel_g;         /* Лінійні прискорення (g) */
    Vector3f attitude_deg;    /* Оцінка кутів орієнтації (крен, тангаж, курс) */
    Vector3f target_angle;    /* Задані пілотом кути */
    float target_throttle;    /* Задана базова тяга (0.0 .. 1.0) */
    uint16_t motor_pwm[4];    /* Значення ШІМ для моторів M1..M4 */
    bool armed;               /* Прапорець дозволу роботи моторів */
} FlightState;

/* Ініціалізація ПІД-регулятора */
void pid_init(PidController* pid, float kp, float ki, float kd, float out_limit, float int_limit) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->out_limit = out_limit;
    pid->int_limit = int_limit;
}

/* Обчислення керуючого впливу за один такт */
float pid_update(PidController* pid, float target, float current, float dt) {
    float error = target - current;

    /* Пропорційна складова */
    float p_term = pid->kp * error;

    /* Інтегральна складова із захистом від перенасичення (anti-windup) */
    pid->integral += error * dt;
    if (pid->integral > pid->int_limit) {
        pid->integral = pid->int_limit;
    } else if (pid->integral < -pid->int_limit) {
        pid->integral = -pid->int_limit;
    }
    float i_term = pid->ki * pid->integral;

    /* Диференціальна складова за зміною похибки */
    float d_term = 0.0f;
    if (dt > 0.0f) {
        d_term = pid->kd * ((error - pid->prev_error) / dt);
    }
    pid->prev_error = error;

    float output = p_term + i_term + d_term;

    /* Обмеження вихідного сигналу */
    if (output > pid->out_limit) {
        output = pid->out_limit;
    } else if (output < -pid->out_limit) {
        output = -pid->out_limit;
    }
    return output;
}

/* Комплементарний фільтр оцінки орієнтації */
void attitude_filter_update(Vector3f* att, const Vector3f* gyro, const Vector3f* accel, float dt) {
    /* 1. Наближена оцінка кутів крену та тангажу за акселерометром */
    /* За нульових кутів accel_g.z = 1.0g; спрощене лінійне наближення для малих кутів */
    float accel_roll = accel->y * 57.29578f;   /* Радіани в градуси: 180 / π */
    float accel_pitch = -accel->x * 57.29578f;

    /* 2. Інтегрування гіроскопа та злиття з даними акселерометра */
    att->x = FILTER_ALPHA * (att->x + gyro->x * dt) + (1.0f - FILTER_ALPHA) * accel_roll;
    att->y = FILTER_ALPHA * (att->y + gyro->y * dt) + (1.0f - FILTER_ALPHA) * accel_pitch;
    att->z += gyro->z * dt; /* Курс (yaw) розраховується прямим інтегруванням */
}

/* Матриця мікшування для квадрокоптера схеми Quad-X */
void motor_mixer(FlightState* state, float roll_corr, float pitch_corr, float yaw_corr) {
    if (!state->armed) {
        for (int i = 0; i < 4; ++i) {
            state->motor_pwm[i] = MOTOR_MIN_PWM;
        }
        return;
    }

    float base_throttle = (float)MOTOR_MIN_PWM + state->target_throttle * (float)(MOTOR_MAX_PWM - MOTOR_MIN_PWM);
    if (base_throttle < (float)MOTOR_IDLE_PWM) {
        base_throttle = (float)MOTOR_IDLE_PWM;
    }

    /* Мотори Quad-X:
       M1: передній правий (CCW)  = Base - Roll + Pitch + Yaw
       M2: задній правий   (CW)   = Base - Roll - Pitch - Yaw
       M3: задній лівий    (CCW)  = Base + Roll - Pitch + Yaw
       M4: передній лівий  (CW)   = Base + Roll + Pitch - Yaw */
    float m[4];
    m[0] = base_throttle - roll_corr + pitch_corr + yaw_corr;
    m[1] = base_throttle - roll_corr - pitch_corr - yaw_corr;
    m[2] = base_throttle + roll_corr - pitch_corr + yaw_corr;
    m[3] = base_throttle + roll_corr + pitch_corr - yaw_corr;

    for (int i = 0; i < 4; ++i) {
        if (m[i] < (float)MOTOR_IDLE_PWM) m[i] = (float)MOTOR_IDLE_PWM;
        if (m[i] > (float)MOTOR_MAX_PWM)  m[i] = (float)MOTOR_MAX_PWM;
        state->motor_pwm[i] = (uint16_t)m[i];
    }
}

/* Зовнішні прототипи драйверів низького рівня (HAL/Регістри) */
extern bool hardware_timer_wait_next_tick(void);
extern void sensor_read_imu(Vector3f* gyro, Vector3f* accel);
extern void radio_read_commands(Vector3f* target_angle, float* throttle, bool* armed);
extern void pwm_write_channels(const uint16_t pwm[4]);
extern void watchdog_feed(void);

/* Головна точка входу керуючого циклу */
void flight_controller_main_loop(void) {
    PidController pid_roll;
    PidController pid_pitch;
    PidController pid_yaw;

    pid_init(&pid_roll,  2.5f, 0.4f, 0.08f, 300.0f, 100.0f);
    pid_init(&pid_pitch, 2.5f, 0.4f, 0.08f, 300.0f, 100.0f);
    pid_init(&pid_yaw,   4.0f, 0.8f, 0.00f, 400.0f, 150.0f);

    FlightState state = {0};

    while (1) {
        /* 1. Блокування до настання періодичного переривання (1 кГц) */
        if (!hardware_timer_wait_next_tick()) {
            continue;
        }

        /* 2. Зчитування сенсорів */
        sensor_read_imu(&state.gyro_dps, &state.accel_g);

        /* 3. Оцінка орієнтації */
        attitude_filter_update(&state.attitude_deg, &state.gyro_dps, &state.accel_g, LOOP_PERIOD_SEC);

        /* 4. Отримання цілей від радіоприймача */
        radio_read_commands(&state.target_angle, &state.target_throttle, &state.armed);

        /* 5. Розрахунок впливів ПІД */
        float roll_u  = pid_update(&pid_roll,  state.target_angle.x, state.attitude_deg.x, LOOP_PERIOD_SEC);
        float pitch_u = pid_update(&pid_pitch, state.target_angle.y, state.attitude_deg.y, LOOP_PERIOD_SEC);
        float yaw_u   = pid_update(&pid_yaw,   state.target_angle.z, state.gyro_dps.z,     LOOP_PERIOD_SEC);

        /* 6. Мікшування та видача на ШІМ */
        motor_mixer(&state, roll_u, pitch_u, yaw_u);
        pwm_write_channels(state.motor_pwm);

        /* 7. Скидання сторожового таймера */
        watchdog_feed();
    }
}
