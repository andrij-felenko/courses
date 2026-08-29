/* ports/host_mock/host_port.h — порт для комп'ютера розробника.
 * Той самий застосунок, ті самі драйвери, але замість шини I2C — імітація
 * мікросхем у пам'яті, а замість SysTick — віртуальний годинник, який
 * стрибає вперед миттєво. Прошивка добу роботи проживає за частку секунди,
 * і саме це робить збірку на кожен коміт можливою. */
#ifndef HOST_PORT_H
#define HOST_PORT_H

#include "hal/hal_gpio.h"
#include "hal/hal_i2c_ops.h"

/* --- Імітація шини --- */

const hal_i2c_bus_t *mock_i2c_bus(void);

/* Чи присутня мікросхема на адресі. Вимкнена відповідає HAL_I2C_ERR_NACK —
 * рівно так, як порожня колодка на платі. */
void mock_i2c_set_present(uint8_t dev_addr, bool present);

/* Наступні count звертань до цієї адреси зазнають невдачі із заданим
 * статусом. Так перевіряють гілки обробки помилок, які на живій платі
 * відтворити важко: обрив шлейфа посеред читання не замовиш. */
void mock_i2c_inject_error(uint8_t dev_addr, hal_i2c_status_t status, unsigned count);

/* Задає покази імітованих мікросхем у сирих кодах АЦП. */
void mock_bme280_set_raw(uint32_t adc_t, uint32_t adc_p, uint16_t adc_h);
void mock_adxl345_set_axes(int16_t x, int16_t y, int16_t z);

/* Скільки транзакцій пройшло шиною — дешева перевірка того, що драйвер
 * не опитує давач частіше, ніж обіцяв. */
unsigned mock_i2c_transaction_count(void);

/* --- Імітація виводів --- */

const hal_gpio_ops_t *mock_gpio_ops(void);
void                 *mock_gpio_port(void);
bool                  mock_gpio_level(uint8_t pin);
unsigned              mock_gpio_toggle_count(uint8_t pin);

/* --- Імітація кнопки --- */

/* Кладе подію натиску так само, як це зробив би обробник EXTI0. */
void mock_button_click(void);

#endif /* HOST_PORT_H */
