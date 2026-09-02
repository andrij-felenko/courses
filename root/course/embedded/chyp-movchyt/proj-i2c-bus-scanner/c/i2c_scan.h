/* Перебір адресного простору й читання його результату як діагнозу */
#ifndef I2C_SCAN_H
#define I2C_SCAN_H

#include <stdint.h>

#include "i2c_bitbang.h"

/* Робочий діапазон 7-бітних адрес: 0x00..0x07 і 0x78..0x7F стандарт
   віддав під General Call, CBUS, 10-бітний префікс і Device ID. */
#define I2C_FIRST_ADDR 0x08u
#define I2C_LAST_ADDR  0x77u
#define I2C_ADDR_SPACE 112u

typedef struct {
    uint8_t found[I2C_ADDR_SPACE];
    uint8_t found_count;
    uint16_t nack_count;   /* адреса відповіді не дала — це нормальний стан порожньої адреси */
    uint16_t error_count;  /* транзакція не відбулася взагалі — це вже дефект ліній */
    i2c_status_t last_error;
} i2c_scan_report_t;

typedef enum {
    VERDICT_DEVICE_AS_EXPECTED,
    VERDICT_ADDRESS_MISMATCH,
    VERDICT_PHANTOM_ALL_ACK,
    VERDICT_SILENT_BUT_HEALTHY,
    VERDICT_LINES_BROKEN
} i2c_verdict_t;

i2c_scan_report_t i2c_scan_range(void);
i2c_verdict_t i2c_classify(const i2c_scan_report_t *report, uint8_t expected_addr);
void i2c_print_report(const i2c_scan_report_t *report, uint8_t expected_addr, i2c_verdict_t verdict);

#endif /* I2C_SCAN_H */
