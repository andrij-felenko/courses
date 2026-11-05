// Реалізація драйвера 64-бітного лічильника енкодера на мові C (ESP-IDF / Generic Driver)
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t accumulated_position; // 64-бітне абсолютне положення ротора
    uint16_t last_hardware_cnt;   // Попереднє значення 16-бітного регістру CNT
    float current_velocity_rpm;   // Обчислена кутова швидкість у RPM
} encoder_64bit_handle_t;

void encoder_64bit_init(encoder_64bit_handle_t *handle, uint16_t initial_cnt) {
    handle->accumulated_position = 0;
    handle->last_hardware_cnt = initial_cnt;
    handle->current_velocity_rpm = 0.0f;
}

// Функція періодичного опитування (викликається в таймері RTOS із частотою dt_seconds)
void encoder_64bit_update(encoder_64bit_handle_t *handle, uint16_t current_cnt, float dt_seconds, uint32_t cpr) {
    // Обчислення знакової різниці з автоматичною обробкою 16-бітного переповнення через int16_t!
    int16_t delta = (int16_t)(current_cnt - handle->last_hardware_cnt);
    
    // Оновлення 64-бітного накопичувального лічильника
    handle->accumulated_position += delta;
    handle->last_hardware_cnt = current_cnt;

    // Розрахунок кутової швидкості обертання вала (RPM)
    if (dt_seconds > 0.0f && cpr > 0) {
        float revs = (float)delta / (float)cpr;
        handle->current_velocity_rpm = (revs / dt_seconds) * 60.0f;
    }
}

int64_t encoder_64bit_get_position(const encoder_64bit_handle_t *handle) {
    return handle->accumulated_position;
}
