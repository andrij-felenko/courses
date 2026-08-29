/* gimbal_controller.h — чиста математика контуру одноосьового підвісу.
 *
 * Модуль свідомо не знає ні про I2C, ні про таймери: у нього входять числа
 * з давача, виходить тривалість імпульсу для сервоприводу. Саме тому його
 * можна прогнати на настільному комп'ютері записом із стенда. */

#ifndef GIMBAL_CONTROLLER_H
#define GIMBAL_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

#define GIMBAL_DT_SEC        0.005f   /* Крок такту 200 Гц */
#define GIMBAL_SERVO_MIN_US  1000.0f  /* Край ходу «мінус» */
#define GIMBAL_SERVO_MID_US  1500.0f  /* Нейтраль, 0° */
#define GIMBAL_SERVO_MAX_US  2000.0f  /* Край ходу «плюс» */
#define GIMBAL_MAX_ANGLE_DEG 45.0f    /* Механічна межа шарніра ±45° */

/* Поріг дисперсії вибірки спокою, (°/с)². Вище — давач рухався. */
#define GIMBAL_MAX_BIAS_VAR  0.25f

/* Стан комплементарного фільтра. */
typedef struct {
    float angle_deg;  /* Поточна оцінка кута нахилу */
    float alpha;      /* Довіра до гіроскопа, ≈0.98 */
} CompFilter;

/* Стан і налаштування ПІД-регулятора. */
typedef struct {
    float kp, ki, kd;

    float out_min, out_max;   /* Межі керування = межі ходу шарніра */
    float deadband_deg;       /* Мертва зона похибки проти дребезгу */

    float integrator;
    float d_lpf_state;        /* Згладжена похідна (за виміром) */
    float d_lpf_alpha;        /* Коефіцієнт ФНЧ похідної */
} GimbalPID;

/* Накопичувач калібрування нуля гіроскопа.
 *
 * Масиву на 500 вибірок тут немає навмисно: 500 float це 2000 байтів, а в
 * ATmega328P усього 2048 байтів SRAM. Середнє й дисперсію рахуємо потоково
 * за Велфордом — три числа замість двох кілобайтів. */
typedef struct {
    uint16_t n;
    float    mean;
    float    m2;   /* Сума квадратів відхилень від поточного середнього */
} GyroCal;

/* Налаштування підвісу в одному місці. */
typedef struct {
    float alpha;         /* Вага гіроскопа в комплементарному фільтрі */
    float kp, ki, kd;
    float d_cutoff_hz;   /* Зріз ФНЧ похідної, 20…30 Гц */
    float deadband_deg;  /* Мертва зона, ≈0.3° */
} GimbalConfig;

typedef struct {
    CompFilter filter;
    GimbalPID  pid;
    float      gyro_bias_dps;
    bool       is_calibrated;
} SingleAxisGimbal;

/* Що контур порахував на такті — для телеметрії й для приводу. */
typedef struct {
    float    angle_deg;      /* Оцінка кута після фільтра */
    float    rate_dps;       /* Кутова швидкість без зсуву */
    float    correction_deg; /* Вихід ПІД після обмеження */
    float    integrator;     /* Стан інтегратора, за ним стежить тест дрейфу */
    uint16_t pulse_us;       /* Тривалість імпульсу для серво */
} GimbalOutput;

void  gimbal_init(SingleAxisGimbal *g, const GimbalConfig *cfg);

/* Скидання лише керувального стану: інтегратор і фільтр похідної.
 * Калібрування й оцінку кута не чіпає — після збою шини вони чинні. */
void  gimbal_reset_control(SingleAxisGimbal *g);

void  gyro_cal_reset(GyroCal *cal);
void  gyro_cal_push(GyroCal *cal, float gyro_dps);

/* Завершення калібрування: перевіряє кількість вибірок і дисперсію.
 * Повертає false, якщо давач рухався — тоді зсув НЕ застосовується. */
bool  gyro_cal_finish(const GyroCal *cal, uint16_t need_samples, float *bias_out);

void  gimbal_set_bias(SingleAxisGimbal *g, float bias_dps);

/* Початкове наведення фільтра на акселерометр, щоб контур не стартував
 * із нуля, коли стенд стоїть під нахилом. */
void  gimbal_seed_angle(SingleAxisGimbal *g, float ay, float az);

float comp_filter_update(CompFilter *f, float raw_gyro_dps, float gyro_bias_dps,
                         float ay, float az, float dt);

float pid_update(GimbalPID *pid, float setpoint_deg, float current_angle_deg,
                 float measured_rate_dps, float dt);

uint16_t servo_output_map(float correction_deg);

void  gimbal_step(SingleAxisGimbal *g, float raw_gyro_dps, float ay, float az,
                  GimbalOutput *out);

#endif /* GIMBAL_CONTROLLER_H */
