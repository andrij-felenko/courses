#pragma once
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SPAD_OK = 0,
    SPAD_ERR_NOT_FOUND = -1,
    SPAD_ERR_HV_OUT_OF_RANGE = -2,
    SPAD_ERR_TEC_TIMEOUT = -3,
    SPAD_ERR_FIFO_OVERFLOW = -4,
    SPAD_ERR_INVALID_PARAM = -5,
    SPAD_ERR_COMMUNICATION = -6
} spad_status_t;

typedef struct {
    float bias_voltage_v;     // Напруга зміщення V_bias (V)
    float discriminator_mv;   // Поріг дискримінатора (mV)
    uint32_t dead_time_ns;    // Заданий мертвий час (ns)
    float target_temp_c;      // Цільова температура Пельтьє (°C)
    bool enable_gating;       // Прапорець зовнішнього стробування
    uint32_t coinc_window_ps; // Часове вікно совпадінь (ps)
} spad_config_t;

typedef struct {
    uint64_t total_counts_a;  // Накопичені відліки каналу A
    uint64_t total_counts_b;  // Накопичені відліки каналу B
    uint64_t coincidences;    // Кількість зафіксованих совпадінь
    float current_dcr_hz;     // Поточний темновий рахунок (Hz)
    float actual_temp_c;      // Поточна температура кристала (°C)
    bool high_voltage_active; // Стан високої напруги
} spad_metrics_t;

/**
 * @brief Ініціалізація та відкриття з'єднання з детектором SPAD / платою TCSPC
 * @param device_index Індекс пристрою в системі (0, 1...)
 * @param handle Повертає вказівник на хендл сесії
 */
spad_status_t spad_init(int device_index, void** handle);

/**
 * @brief Завантаження конфігурації (напруга, поріг, мертвий час)
 */
spad_status_t spad_configure(void* handle, const spad_config_t* config);

/**
 * @brief Ввімкнення/вимкнення джерела високої напруги HV_BIAS
 */
spad_status_t spad_enable_high_voltage(void* handle, bool enable);

/**
 * @brief Зчитування поточних метрологічних метрик детектора
 */
spad_status_t spad_read_metrics(void* handle, spad_metrics_t* metrics);

/**
 * @brief Зчитування масиву 64-бітних пікосекундних часових міток (Time-Tagging Mode)
 * @param handle Хендл пристрою
 * @param buffer Масив для запису міток
 * @param max_tags Максимальна кількість міток
 * @param actual_read Повертає кількість реально прочитаних міток
 */
spad_status_t spad_read_timetags(void* handle, uint64_t* buffer, uint32_t max_tags, uint32_t* actual_read);

/**
 * @brief Безпечне вимкнення високої напруги та закриття сесії
 */
spad_status_t spad_close(void* handle);

#ifdef __cplusplus
}
#endif
