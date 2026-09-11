#include <stdint.h>

/* Структура калібрувальних параметрів сервопривода */
typedef struct {
    uint16_t t_cal_min_us;  /* Мінімальна безпечна тривалість імпульсу, мкс */
    uint16_t t_cal_max_us;  /* Максимальна безпечна тривалість імпульсу, мкс */
    float angle_min_deg;    /* Мінімальний робочий кут, градуси */
    float angle_max_deg;    /* Максимальний робочий кут, градуси */
    float k_cal;            /* Робочий коефіцієнт нахилу, мкс/градус */
} servo_calib_t;

/* Функція обмеження значення у вказаному діапазоні (clamping) */
static inline float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

static inline uint16_t clamp_u16(uint16_t val, uint16_t min, uint16_t max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

/* Ініціалізація структури та перерахунок коефіцієнта нахилу */
void servo_init_calibration(servo_calib_t *cal, 
                            uint16_t t_phys_min_us, 
                            uint16_t t_phys_max_us, 
                            uint16_t margin_us,
                            float angle_min, 
                            float angle_max) {
    cal->t_cal_min_us = t_phys_min_us + margin_us;
    cal->t_cal_max_us = t_phys_max_us - margin_us;
    cal->angle_min_deg = angle_min;
    cal->angle_max_deg = angle_max;
    
    /* Обчислення крутизни робочої характеристики k_cal */
    cal->k_cal = (float)(cal->t_cal_max_us - cal->t_cal_min_us) / 
                 (cal->angle_max_deg - cal->angle_min_deg);
}

/* Безпечне перетворення цільового кута в тривалість імпульсу */
uint16_t servo_angle_to_pulse_safe(const servo_calib_t *cal, float target_angle) {
    /* Рівень 1: кутовий клампінг для усунення некоректного завдання */
    float angle_clamped = clampf(target_angle, cal->angle_min_deg, cal->angle_max_deg);
    
    /* Лінійна інтерполяція за відкаліброваними параметрами */
    float pulse_raw = (float)cal->t_cal_min_us + 
                      cal->k_cal * (angle_clamped - cal->angle_min_deg);
    
    /* Рівень 2: апаратний клампінг тривалості імпульсу перед передачею в таймер */
    uint16_t pulse_final = clamp_u16((uint16_t)(pulse_raw + 0.5f), 
                                     cal->t_cal_min_us, 
                                     cal->t_cal_max_us);
    
    return pulse_final;
}
