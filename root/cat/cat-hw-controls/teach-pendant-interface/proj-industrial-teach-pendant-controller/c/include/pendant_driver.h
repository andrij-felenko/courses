#ifndef PENDANT_DRIVER_H
#define PENDANT_DRIVER_H

#include "pendant_types.h"

// Допустимий час неузгодженості каналів безпеки (у мілісекундах)
#define PENDANT_DISCREPANCY_TIMEOUT_MS 50U

// Центральна точка 12-бітного ADC (4096 / 2)
#define PENDANT_ADC_CENTER             2048U

/**
 * @brief Ініціалізація структур пульта налагодження робота.
 * @param safety Вказівник на контекст безпеки.
 * @param joy Вказівник на контекст джойстика.
 */
void pendant_init(pendant_safety_state_t *safety, pendant_joystick_t *joy);

/**
 * @brief Потактовий крос-моніторинг двоканальних ліній E-Stop та Enabling Switch.
 * @param safety Вказівник на контекст безпеки.
 * @param estop_1 Стан 1-го каналу E-Stop (1 - замкнено, 0 - розімкнено).
 * @param estop_2 Стан 2-го каналу E-Stop (1 - замкнено, 0 - розімкнено).
 * @param enable_1 Позиція 1-го каналу клавіша (0 - Released, 1 - Center, 2 - Panic).
 * @param enable_2 Позиція 2-го каналу клавіша (0 - Released, 1 - Center, 2 - Panic).
 * @param current_time_ms Поточний системний час у мілісекундах.
 */
void pendant_update_safety(pendant_safety_state_t *safety,
                          uint8_t estop_1, uint8_t estop_2,
                          uint8_t enable_1, uint8_t enable_2,
                          uint32_t current_time_ms);

/**
 * @brief Обробка значень 3D-джойстика з нечутливою зоною та масштабуванням.
 * @param joy Вказівник на контекст джойстика.
 * @param adc_x Сирий відлік ADC очі X.
 * @param adc_y Сирий відлік ADC очі Y.
 * @param adc_z Сирий відлік ADC очі Z.
 */
void pendant_update_joystick(pendant_joystick_t *joy,
                            uint16_t adc_x, uint16_t adc_y, uint16_t adc_z);

/**
 * @brief Обчислення контрольної суми CRC-16 (Modbus polynomial 0xA001).
 * @param data Вказівник на буфер даних.
 * @param length Довжина даних у байтах.
 * @return Обчислена 16-бітна контрольна сума.
 */
uint16_t pendant_calculate_crc16(const uint8_t *data, size_t length);

/**
 * @brief Упаковка поточних даних пульта в телеметричний кадр з CRC-16.
 * @param safety Вказівник на контекст безпеки.
 * @param joy Вказівник на контекст джойстика.
 * @param buffer Вихідний буфер для збереження кадру.
 * @param max_len Максимальний розмір вихідного буфера.
 * @return Кількість упакованих байтів кадру.
 */
size_t pendant_serialize_frame(const pendant_safety_state_t *safety,
                               const pendant_joystick_t *joy,
                               uint8_t *buffer, size_t max_len);

#endif // PENDANT_DRIVER_H
