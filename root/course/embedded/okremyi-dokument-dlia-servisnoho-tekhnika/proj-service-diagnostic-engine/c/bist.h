/* bist.h — самотестування вузлів плати (Built-In Self Test). */
#ifndef BIST_H
#define BIST_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool     bus_free;   /* обидві лінії I2C відпущені до початку тесту */
    bool     rtc_ok;     /* годинник реального часу відповів ACK */
    bool     eeprom_ok;  /* EEPROM відповіла ACK */
    uint16_t adc0_raw;   /* сирий код каналу 0 */
    uint16_t adc0_mv;    /* він же в мілівольтах, цілочисельно */
} bist_report_t;

/* Пробник одного адресата. ACK -> true; зайнята або прибита шина -> false
   не пізніше ніж за 5 мс. Зациклитись ця функція не може. */
bool hw_i2c_probe_device(uint8_t addr_7bit);

/* Повний прохід BIST. false — шину тримає інша задача, тест не робився. */
bool bist_run(bist_report_t *rep);

#endif /* BIST_H */
