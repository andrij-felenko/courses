// драйвер давача залежить від інтерфейсу шини (заголовок i2c.h):
//   int i2c_write_reg(uint8_t dev, uint8_t reg);   // обрати регістр
//   int i2c_read_byte(uint8_t dev, uint8_t *out);  // прочитати байт

#include "unity.h"
#include "mock_i2c.h"      // CMock згенерував це з i2c.h
#include "sensor.h"

#define DEV  0x40
#define REG_TEMP 0x07

void test_read_temp_writes_register_then_reads(void) {
    uint8_t fake = 25;

    // 1) очікуємо: спершу драйвер ОБЕРЕ регістр температури і дістане OK
    i2c_write_reg_ExpectAndReturn(DEV, REG_TEMP, 0);

    // 2) ПОТІМ прочитає байт; підсунемо 25 у вихідний параметр
    i2c_read_byte_ExpectAndReturn(DEV, NULL, 0);
    i2c_read_byte_IgnoreArg_out();          // адресу буфера наперед не знаємо
    i2c_read_byte_ReturnThruPtr_out(&fake); // у *out мок покладе 25

    // дія під тестом:
    int t = sensor_read_temp(DEV);

    // CMock уже перевірив, що обидва виклики були, з тими аргументами,
    // і саме в цьому порядку. Лишилось звірити результат логіки:
    TEST_ASSERT_EQUAL_INT(25, t);
}
