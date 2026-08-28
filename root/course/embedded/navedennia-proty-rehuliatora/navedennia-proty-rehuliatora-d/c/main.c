/* ============================================================================
   Модуль розділення Наведення (Guidance) та Регулювання (Control)
   Мова: C (C99 / C11) для FreeRTOS / RTOS систем реального часу
   ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define RAD_TO_DEG(x) ((x) * 57.2957795f)
#define DEG_TO_RAD(x) ((x) * 0.0174532925f)
#define MAX_TILT_RAD   (0.610865f)    /* 35 градусів максимального нахилу */
#define SETPOINT_TIMEOUT_US (100000)  /* 100 мс таймаут застарівання */

/* Тривимірний вектор */
typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

/* Кватерніон просторової орієнтації */
typedef struct {
    float w, x, y, z;
} Quaternion;

/* Інтерфейсний пакет уставки від наведення до регулятора */
typedef struct {
    uint64_t timestamp_us;    /* Часова мітка генерації (мікросекунди) */
    Quaternion q_target;      /* Цільовий кватерніон орієнтації */
    Vector3f rate_feedforward;/* Кутові швидкості прямого зв'язку (рад/с) */
    float collective_thrust;  /* Нормалізована тяга [0.0 .. 1.0] */
    bool valid;               /* Прапорець валідності даних */
} SetpointPayload;

/* Стан безблокувального обміну між потоками (Seqlock Mailbox) */
typedef struct {
    SetpointPayload buffer[2];
    volatile uint32_t sequence;
} LockFreeMailbox;

static LockFreeMailbox g_mailbox = {0};

/* Запис уставки з задачі наведення (Guidance Task, 20–50 Гц) */
void mailbox_write(const SetpointPayload* sp) {
    uint32_t seq = g_mailbox.sequence;
    uint32_t next_idx = (seq & 1) ^ 1;
    
    g_mailbox.buffer[next_idx] = *sp;
    
    /* Збільшуємо послідовність атомарно (парне число = стабільні дані) */
    g_mailbox.sequence = seq + 1;
}

/* Читання уставки в задачі стабілізації (Control Task, 1000 Гц) */
bool mailbox_read(SetpointPayload* out_sp) {
    uint32_t seq = g_mailbox.sequence;
    uint32_t read_idx = seq & 1;
    
    *out_sp = g_mailbox.buffer[read_idx];
    
    /* Перевірка, чи не відбувся запис під час читання */
    return (g_mailbox.sequence == seq && out_sp->valid);
}

/* ----------------------------------------------------------------------------
   1. ШАР НАВЕДЕННЯ (GUIDANCE): Генерація уставки з бажаного прискорення
   ---------------------------------------------------------------------------- */
void guidance_generate_setpoint(const Vector3f* a_des, float yaw_target_rad, 
                                uint64_t now_us, SetpointPayload* sp) 
{
    /* Вектор питомої сили f = a_des - g (де g = [0, 0, -9.81] в NED) */
    Vector3f f_des;
    f_des.x = a_des->x;
    f_des.y = a_des->y;
    f_des.z = a_des->z - 9.81f;

    float f_norm = sqrtf(f_des.x * f_des.x + f_des.y * f_des.y + f_des.z * f_des.z);
    if (f_norm < 1e-4f) {
        f_norm = 9.81f;
        f_des.z = -9.81f;
    }

    /* Бажана вісь Z тіла: z_body = -f_des / ||f_des|| */
    Vector3f zb;
    zb.x = -f_des.x / f_norm;
    zb.y = -f_des.y / f_norm;
    zb.z = -f_des.z / f_norm;

    /* Обмеження кута нахилу (Tilt Limiter): zb.z відповідає cos(tilt) */
    if (zb.z < cosf(MAX_TILT_RAD)) {
        float xy_norm = sqrtf(zb.x * zb.x + zb.y * zb.y);
        if (xy_norm > 1e-4f) {
            float sin_max = sinf(MAX_TILT_RAD);
            zb.x = (zb.x / xy_norm) * sin_max;
            zb.y = (zb.y / xy_norm) * sin_max;
            zb.z = cosf(MAX_TILT_RAD);
        }
    }

    /* Побудова цільового кватерніона за віссю Z та кутом курсу */
    float cy = cosf(yaw_target_rad * 0.5f);
    float sy = sinf(yaw_target_rad * 0.5f);
    
    /* Спрощений розрахунок нахилу для малих та середніх кутів */
    float pitch_target = asinf(-zb.x);
    float roll_target  = atan2f(zb.y, zb.z);

    float cr = cosf(roll_target * 0.5f);
    float sr = sinf(roll_target * 0.5f);
    float cp = cosf(pitch_target * 0.5f);
    float sp_p = sinf(pitch_target * 0.5f);

    sp->q_target.w = cr * cp * cy + sr * sp_p * sy;
    sp->q_target.x = sr * cp * cy - cr * sp_p * sy;
    sp->q_target.y = cr * sp_p * cy + sr * cp * sy;
    sp->q_target.z = cr * cp * sy - sr * sp_p * cy;

    /* Нормалізація колективної тяги (номінал 9.81 м/с² = 0.5 тяги) */
    float thrust = f_norm / (2.0f * 9.81f);
    if (thrust > 1.0f) thrust = 1.0f;
    if (thrust < 0.05f) thrust = 0.05f;
    sp->collective_thrust = thrust;

    sp->rate_feedforward.x = 0.0f;
    sp->rate_feedforward.y = 0.0f;
    sp->rate_feedforward.z = 0.0f;

    sp->timestamp_us = now_us;
    sp->valid = true;
}

/* ----------------------------------------------------------------------------
   2. ШАР РЕГУЛЮВАННЯ (CONTROL): Відпрацювання уставки на частоті 1000 Гц
   ---------------------------------------------------------------------------- */
void control_step_1000hz(const Quaternion* q_est, const Vector3f* gyro_rad_s,
                         uint64_t now_us, Vector3f* motor_torques, float* final_thrust) 
{
    SetpointPayload sp;
    bool fresh_data = mailbox_read(&sp);

    /* Сторож застарівання уставки (Setpoint Watchdog) */
    if (!fresh_data || (now_us - sp.timestamp_us > SETPOINT_TIMEOUT_US)) {
        /* АВАРІЙНИЙ РЕЖИМ (Fallback): горизонтальне положення, плавний спуск */
        sp.q_target.w = 1.0f;
        sp.q_target.x = 0.0f;
        sp.q_target.y = 0.0f;
        sp.q_target.z = 0.0f;
        sp.collective_thrust = 0.40f; /* 40% газу для керованого зниження */
        sp.rate_feedforward.x = 0.0f;
        sp.rate_feedforward.y = 0.0f;
        sp.rate_feedforward.z = 0.0f;
    }

    /* 1. Похибка орієнтації: q_err = q_est_conj * q_target */
    Quaternion q_err;
    q_err.w =  q_est->w * sp.q_target.w + q_est->x * sp.q_target.x 
             + q_est->y * sp.q_target.y + q_est->z * sp.q_target.z;
    q_err.x =  q_est->w * sp.q_target.x - q_est->x * sp.q_target.w 
             - q_est->y * sp.q_target.z + q_est->z * sp.q_target.y;
    q_err.y =  q_est->w * sp.q_target.y + q_est->x * sp.q_target.z 
             - q_est->y * sp.q_target.w - q_est->z * sp.q_target.x;
    q_err.z =  q_est->w * sp.q_target.z - q_est->x * sp.q_target.y 
             + q_est->y * sp.q_target.x - q_est->z * sp.q_target.w;

    /* Якщо w < 0, обираємо найкоротший шлях повороту на 4-сфері */
    float sign = (q_err.w >= 0.0f) ? 1.0f : -1.0f;
    
    /* Пропорційний P-регулятор орієнтації (k_p = 6.5 рад/с на рад похибки) */
    const float KP_ATTITUDE = 6.5f;
    Vector3f rate_target;
    rate_target.x = 2.0f * sign * q_err.x * KP_ATTITUDE + sp.rate_feedforward.x;
    rate_target.y = 2.0f * sign * q_err.y * KP_ATTITUDE + sp.rate_feedforward.y;
    rate_target.z = 2.0f * sign * q_err.z * (KP_ATTITUDE * 0.6f);

    /* 2. Швидкий PID-регулятор кутових швидкостей (Rate Loop) */
    const float KP_RATE = 0.15f;
    const float KD_RATE = 0.003f;
    
    Vector3f rate_err;
    rate_err.x = rate_target.x - gyro_rad_s->x;
    rate_err.y = rate_target.y - gyro_rad_s->y;
    rate_err.z = rate_target.z - gyro_rad_s->z;

    /* Розрахунок керівних моментів */
    motor_torques->x = KP_RATE * rate_err.x;
    motor_torques->y = KP_RATE * rate_err.y;
    motor_torques->z = KP_RATE * rate_err.z * 1.5f;

    *final_thrust = sp.collective_thrust;
}
