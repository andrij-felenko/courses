#ifndef JVS_STANDARD_H
#define JVS_STANDARD_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Фундаментальні константи
#define JOSEPHSON_CONSTANT_KJ 483597.8484e9 // Гц / В

// Коди помилок метрологічного комплексу
typedef enum {
    JVS_SUCCESS = 0,
    JVS_ERR_RF_UNLOCKED = 1,     // Втрата фазової синхронізації НВЧ генератора
    JVS_ERR_STEP_TRIPPED = 2,    // Зрив зі сходинки Шапіро (струмове виходження)
    JVS_ERR_TEMP_EXCEEDED = 3,   // Перевищення критичної температури (> 4.2 K)
    JVS_ERR_INVALID_VOLTAGE = 4, // Запитана напруга поза діапазоном чипа
    JVS_ERR_COMM_TIMEOUT = 5     // Таймаут шини керування GPIB/Ethernet
} JvsStatus;

// Конфігурація сегмента масиву
typedef struct {
    uint32_t junction_count;
    int8_t current_state; // -1: зворотний струм, 0: вимкнено, +1: прямий струм
} PjvsSegment;

// Повний стан квантового еталона
typedef struct {
    double target_voltage_volts;
    double actual_rf_frequency_hz;
    double measured_cryo_temp_k;
    double bias_current_amperes;
    uint32_t total_active_junctions;
    bool is_locked_on_step;
} JvsSystemState;

// Функції публічного контракту
JvsStatus Jvs_Initialize(const char* device_resource_name);
JvsStatus Jvs_SetRfFrequency(double frequency_hz);
JvsStatus Jvs_SetTargetVoltage(double target_volts, JvsSystemState* out_state);
JvsStatus Jvs_ReadActualVoltage(double* out_voltage_volts, double* out_uncertainty_volts);
JvsStatus Jvs_Shutdown(void);

#ifdef __cplusplus
}
#endif

#endif // JVS_STANDARD_H
