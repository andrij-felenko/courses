#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AS5048_CMD_READ_ANGLE   0xFFFF
#define AS5048_CMD_CLEAR_ERR    0x4001
#define AS5048_CMD_READ_AGC     0x7FFD
#define AS5048_CPR              16384
#define M_TWOPI                 (2.0 * 3.14159265358979323846)

typedef struct {
    int16_t turns;
    uint16_t prev_raw_angle;
    bool initialized;
    
    // Калібрувальні гармонійні коефіцієнти
    float offset_rad;
    float a1, b1; // 1-ша гармоніка (ексцентриситет)
    float a2, b2; // 2-га гармоніка (нахил / неортогональність)
    
    // Змінні стану альфа-бета фільтра
    float est_pos_rad;
    float est_vel_rad_s;
    float alpha;
    float beta;
} magnetic_encoder_t;

// Обчислення біта парності (Even Parity)
static inline bool check_even_parity(uint16_t word) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if ((word >> i) & 1) count++;
    }
    return (count % 2) == 0;
}

// Ініціалізація структури енкодера
void encoder_init(magnetic_encoder_t *enc, float sample_time_s) {
    enc->turns = 0;
    enc->prev_raw_angle = 0;
    enc->initialized = false;
    enc->offset_rad = 0.0f;
    enc->a1 = 0.0f; enc->b1 = 0.0f;
    enc->a2 = 0.0f; enc->b2 = 0.0f;
    
    // Налаштування коефіцієнтів фільтра стеження для смуги 50 Гц
    float dt = sample_time_s;
    enc->alpha = 0.25f;
    enc->beta = 0.05f / dt;
    enc->est_pos_rad = 0.0f;
    enc->est_vel_rad_s = 0.0f;
}

// Запис гармонійних коефіцієнтів лінеаризації
void encoder_set_calibration(magnetic_encoder_t *enc, float offset, 
                             float a1, float b1, float a2, float b2) {
    enc->offset_rad = offset;
    enc->a1 = a1; enc->b1 = b1;
    enc->a2 = a2; enc->b2 = b2;
}

// Обробка сирого фрейму SPI
bool encoder_process_raw_frame(magnetic_encoder_t *enc, uint16_t rx_frame, 
                               float dt, float *out_pos_rad, float *out_vel_rad_s) {
    // 1. Перевірка парності
    if (!check_even_parity(rx_frame)) {
        return false; // Помилка лінії зв'язку
    }
    
    // 2. Перевірка прапорця помилки (Bit 14)
    if (rx_frame & 0x4000) {
        return false; // Помилка енкодера (Error Flag)
    }
    
    // 3. Вилучення 14-бітного значення кута (0..16383)
    uint16_t raw = rx_frame & 0x3FFF;
    
    if (!enc->initialized) {
        enc->prev_raw_angle = raw;
        enc->turns = 0;
        enc->initialized = true;
        enc->est_pos_rad = ((float)raw / (float)AS5048_CPR) * (float)M_TWOPI;
    }
    
    // 4. Багатооборотне розгортання кута (Unwrapping)
    int32_t delta = (int32_t)raw - (int32_t)enc->prev_raw_angle;
    if (delta > (AS5048_CPR / 2)) {
        enc->turns--;
    } else if (delta < -(AS5048_CPR / 2)) {
        enc->turns++;
    }
    enc->prev_raw_angle = raw;
    
    // 5. Неперервний розгорнутий кут в радіанах
    float total_counts = (float)enc->turns * (float)AS5048_CPR + (float)raw;
    float uncalibrated_rad = (total_counts / (float)AS5048_CPR) * (float)M_TWOPI;
    
    // 6. Гармонійна корекція за кутом одного оберту theta_single
    float theta_single = ((float)raw / (float)AS5048_CPR) * (float)M_TWOPI;
    float sin1 = sinf(theta_single), cos1 = cosf(theta_single);
    float sin2 = sinf(2.0f * theta_single), cos2 = cosf(2.0f * theta_single);
    
    float error_correction = enc->offset_rad 
                           + (enc->a1 * cos1 + enc->b1 * sin1)
                           + (enc->a2 * cos2 + enc->b2 * sin2);
    
    float calibrated_pos_rad = uncalibrated_rad - error_correction;
    
    // 7. Альфа-бета фільтрація кута та оцінка швидкості
    float pred_pos = enc->est_pos_rad + enc->est_vel_rad_s * dt;
    float residual = calibrated_pos_rad - pred_pos;
    
    enc->est_pos_rad = pred_pos + enc->alpha * residual;
    enc->est_vel_rad_s = enc->est_vel_rad_s + (enc->beta * dt) * residual;
    
    if (out_pos_rad) *out_pos_rad = enc->est_pos_rad;
    if (out_vel_rad_s) *out_vel_rad_s = enc->est_vel_rad_s;
    
    return true;
}
