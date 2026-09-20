#ifndef ENCODER_TYPES_H
#define ENCODER_TYPES_H

#include <stdint.h>
#include <stdbool.h>

#define RVDT_DMA_BUFFER_SIZE 16

// Статуси системної верифікації каналів вимірювання
typedef enum {
    COMPARE_OK = 0,             // Канали узгоджені, дані достовірні
    COMPARE_WARNING_DISCREPANCY,// Фіксація тимчасової розбіжності в межах допустимого вікна
    COMPARE_ERROR_DISCREPANCY,  // Перевищено таймаут розбіжності між QEI та RVDT
    COMPARE_ERROR_HARDWARE      // Апаратний збій одного з давачів
} compare_status_t;

// Контекст квадратурного оптичного енкодера (QEI)
typedef struct {
    uint32_t ppr;               // Роздільна здатність (імпульсів на оберт)
    int32_t pulse_count;        // Поточне значення лічильника таймера QEI
    float current_angle_deg;    // Обчислений кут повороту у градусах
    bool index_found;           // Прапорець фіксації нульової мітки Index
} qei_encoder_t;

// Контекст індуктивного давача RVDT
typedef struct {
    uint16_t adc_dma_buffer[RVDT_DMA_BUFFER_SIZE]; // Буфер DMA зчитування АЦП
    float sensitivity_mv_per_deg;                  // Чутливість RVDT (мВ/град)
    float zero_offset_deg;                         // Спланований зсув нульової точки
    float current_angle_deg;                       // Обчислений кут у градусах
    bool signal_valid;                             // Стан амплітуди огинаючої RVDT
} rvdt_sensor_t;

// Контекст перехресного порівняння (Cross-Comparison)
typedef struct {
    float max_allowed_diff_deg;  // Максимально припустима розбіжність кутів (град)
    uint32_t discrepancy_timeout_ms; // Таймаут допустимого розходження каналів (мс)
    uint32_t discrepancy_start_ms;   // Початок відліку розходження
    bool in_discrepancy;             // Прапорець наявності розбіжності
    compare_status_t status;         // Поточний статус компаратора
} encoder_comparator_t;

// Головний агрегуючий контекст подвійного драйвера положення штурвала
typedef struct {
    qei_encoder_t qei;               // Оптичний канал QEI
    rvdt_sensor_t rvdt;             // Індуктивний канал RVDT
    encoder_comparator_t comparator;// Модуль порівняння та верифікації
    float valid_position_deg;       // Підсумкова узгоджена координата штурвала
    bool system_healthy;            // Підсумковий прапорець здоров'я системи
} yoke_position_system_t;

#endif // ENCODER_TYPES_H
