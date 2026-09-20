#ifndef ROTARY_DIP_DRIVER_H
#define ROTARY_DIP_DRIVER_H

#include "rotary_dip_types.h"

/**
 * @brief Симуляційна/Апаратна функція зчитування стану фізичної ніжки GPIO.
 * 
 * @param port_id Ідентифікатор порту.
 * @param pin_index Номер ніжки.
 * @return uint8_t Логічний рівень (0 або 1).
 */
uint8_t hal_gpio_read_pin(uint8_t port_id, uint8_t pin_index);

/**
 * @brief Запис значення ніжки в симуляторі GPIO.
 */
void hal_gpio_write_pin(uint8_t port_id, uint8_t pin_index, uint8_t level);

/**
 * @brief Ініціалізація драйвера ротаційного DIP-перемикача.
 * 
 * @param handle Вказівник на структуру контексту драйвера.
 * @param config Вказівник на конфігураційні параметри.
 * @return true у разі успішного налаштування, false якщо вказівники невалідні.
 */
bool rotary_dip_init(rotary_dip_t *handle, const rotary_dip_config_t *config);

/**
 * @brief Опитування стану ліній, фільтрація брязкоту та декодування значення.
 * 
 * @param handle Вказівник на контекст драйвера.
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @return true якщо відчитано стабільне та валідне значення, false у разі помилки або дребезгу.
 */
bool rotary_dip_read(rotary_dip_t *handle, uint32_t current_time_ms);

/**
 * @brief Декодування 4-бітного коду Ґрея (Gray Code) у стандартний двійковий формат.
 * 
 * @param gray_val Вхідний код Ґрея (0x00..0x0F).
 * @return uint8_t Двійковий результат.
 */
uint8_t rotary_dip_gray_to_binary(uint8_t gray_val);

/**
 * @brief Обчислення мережевої адреси Modbus/CAN на основі значення ротора.
 * 
 * @param handle Вказівник на контекст драйвера.
 * @param base_address Базова мережева адреса (offset).
 * @return uint8_t Підсумкова мережева адреса.
 */
uint8_t rotary_dip_get_modbus_address(const rotary_dip_t *handle, uint8_t base_address);

/**
 * @brief Визначення швидкості обміну (Baudrate) за позицією ротора.
 * 
 * @param handle Вказівник на контекст драйвера.
 * @return uint32_t Швидкість у бодах.
 */
uint32_t rotary_dip_get_baudrate(const rotary_dip_t *handle);

#endif /* ROTARY_DIP_DRIVER_H */
