#ifndef WATER_PUMP_H
#define WATER_PUMP_H

#include <stdint.h>
#include <stdbool.h>

/* Стан помпи */
typedef enum {
    PUMP_STATE_IDLE,
    PUMP_STATE_STARTING,
    PUMP_STATE_RUNNING
} WaterPumpState_t;

/* Конфігурація помпи */
typedef struct {
    uint32_t soft_start_duration_ms; /* Тривалість плавного пуску, мс */
    uint32_t max_run_time_ms;        /* Максимальний час безперервної роботи (захист), мс */
    uint8_t target_duty_cycle;       /* Цільовий рівень ШІМ (0-100) */
} WaterPumpConfig_t;

/* Контекст помпи */
typedef struct {
    WaterPumpState_t state;
    WaterPumpConfig_t config;
    
    uint32_t start_time_ms;          /* Час початку роботи (для захисного таймера) */
    uint32_t soft_start_start_ms;    /* Час початку фази soft-start */
    
    uint8_t current_duty;            /* Поточне значення ШІМ */
    
    /* Функція зворотного виклику для встановлення ШІМ */
    void (*set_pwm_cb)(uint8_t duty_cycle);
    /* Функція зворотного виклику для отримання системного часу */
    uint32_t (*get_time_ms_cb)(void);
} WaterPump_t;

/* Ініціалізація помпи */
void WaterPump_Init(WaterPump_t *pump, 
                    WaterPumpConfig_t *config, 
                    void (*set_pwm)(uint8_t), 
                    uint32_t (*get_time_ms)(void));

/* Запуск помпи (вмикає плавний пуск) */
void WaterPump_Start(WaterPump_t *pump);

/* Зупинка помпи */
void WaterPump_Stop(WaterPump_t *pump);

/* Періодичне оновлення стану (має викликатись у головному циклі) */
void WaterPump_Update(WaterPump_t *pump);

#endif // WATER_PUMP_H
