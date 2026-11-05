#ifndef LVC_BUFFER_H
#define LVC_BUFFER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file lvc_buffer.h
 * @brief Драйвер шинного буфера з трьома станами 74LVC1G125 (/OE керування).
 */

/**
 * @brief Стани виходу буфера 74LVC1G125.
 */
typedef enum {
    LVC_BUFFER_STATE_HI_Z = 0,  /* Високоімпедансний стан (відключено від шини, /OE = HIGH) */
    LVC_BUFFER_STATE_ENABLED    /* Активний стан (передача даних на шину, /OE = LOW) */
} lvc_buffer_state_t;

/**
 * @brief Структура конфігурації піна GPIO для керування лінією /OE (Output Enable).
 */
typedef struct {
    void (*set_oe_pin)(bool high);  /* Функція встановлення рівня на піні /OE (true = HIGH, false = LOW) */
    uint32_t delay_us;              /* Час затримки break-before-make в мікросекундах */
} lvc_buffer_config_t;

/**
 * @brief Дескриптор буфера 74LVC1G125.
 */
typedef struct {
    lvc_buffer_config_t config;
    lvc_buffer_state_t current_state;
} lvc_buffer_t;

/**
 * @brief Ініціалізація дескриптора буфера 74LVC1G125.
 * @param buf Вказівник на дескриптор буфера.
 * @param config Конфігурація апаратного інтерфейсу.
 * @return true у разі успіху, false за нульових вказівників.
 */
bool lvc_buffer_init(lvc_buffer_t *buf, const lvc_buffer_config_t *config);

/**
 * @brief Увімкнення буфера (переведення /OE в LOW для передачі на шину).
 * @param buf Вказівник на дескриптор буфера.
 */
void lvc_buffer_enable(lvc_buffer_t *buf);

/**
 * @brief Вимкнення буфера (переведення /OE в HIGH у стан Hi-Z).
 * @param buf Вказівник на дескриптор буфера.
 */
void lvc_buffer_disable(lvc_buffer_t *buf);

/**
 * @brief Безпечне перемикання каналів (Break-Before-Make): вимикає один буфер, 
 *        витримує захисну затримку, потім вмикає інший для запобігання колізіям шини.
 * @param active_buf Буфер, який потрібно вимкнути (може бути NULL).
 * @param next_buf Буфер, який потрібно увімкнути (може бути NULL).
 */
void lvc_buffer_switch_channel(lvc_buffer_t *active_buf, lvc_buffer_t *next_buf);

#endif /* LVC_BUFFER_H */
