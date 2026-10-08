#include <stdint.h>
#include <stdbool.h>

// Структура налаштувань та стану дискретного PID-регулятора
typedef struct {
    float k_p;           // Пропорційний коефіцієнт
    float k_i;           // Інтегральний коефіцієнт
    float k_d;           // Диференціальний коефіцієнт
    float dt;            // Період дискретизації (секунди)
    float out_min;       // Мінімальне значення виходу (0.0%)
    float out_max;       // Максимальне значення виходу (100.0%)
    float alpha;         // Коефіцієнт фільтрації термопари (0.0 .. 1.0)
    
    float i_term;        // Накопичена інтегральна сума
    float prev_meas;     // Попереднє значення виміряної температури
    float filt_temp;     // Відфільтрована температура
    bool  is_first_run;  // Прапорець першого запуску
} pid_controller_t;

// Ініціалізація регулятора
void pid_init(pid_controller_t *pid, float kp, float ki, float kd, float dt, float out_min, float out_max, float alpha) {
    pid->k_p = kp;
    pid->k_i = ki;
    pid->k_d = kd;
    pid->dt = dt;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->alpha = alpha;
    pid->i_term = 0.0f;
    pid->prev_meas = 0.0f;
    pid->filt_temp = 0.0f;
    pid->is_first_run = true;
}

// Крок обчислення вихідної потужності нагрівача
float pid_step(pid_controller_t *pid, float target_temp, float raw_temp) {
    // 1. Цифрова експоненційна фільтрація сигналу термопари K-типу
    if (pid->is_first_run) {
        pid->filt_temp = raw_temp;
        pid->prev_meas = raw_temp;
        pid->is_first_run = false;
    } else {
        pid->filt_temp = pid->alpha * raw_temp + (1.0f - pid->alpha) * pid->filt_temp;
    }

    // 2. Обчислення похибки регулювання
    float error = target_temp - pid->filt_temp;

    // 3. Пропорційна складова P
    float p_term = pid->k_p * error;

    // 4. Тимчасовий розрахунок інтегральної складової I
    float next_i_term = pid->i_term + pid->k_i * error * pid->dt;

    // 5. Диференціальна складова D (за вимірюванням для запобігання сплескам)
    float d_term = -pid->k_d * (pid->filt_temp - pid->prev_meas) / pid->dt;
    pid->prev_meas = pid->filt_temp;

    // 6. Сумарний вихід до обмеження
    float raw_output = p_term + next_i_term + d_term;

    // 7. Обмеження виходу та захист від інтегрального насичення (Anti-Windup)
    float output = raw_output;
    if (output > pid->out_max) {
        output = pid->out_max;
    } else if (output < pid->out_min) {
        output = pid->out_min;
    } else {
        // Оновлюємо накопичувач інтеграла лише коли вихід не в насиченні
        pid->i_term = next_i_term;
    }

    return output;
}
