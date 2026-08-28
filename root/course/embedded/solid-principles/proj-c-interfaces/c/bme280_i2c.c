// bme280_i2c.c — реалізація baro_t поверх шини I2C. Поля приховані тут.
#include "baro.h"
#include "i2c.h"          // i2c_read_reg / i2c_write_reg — примітиви шини плати

#define BME280_REG_ID    0xD0   // регістр ідентифікації чипа
#define BME280_CHIP_ID   0x60   // BME280 відповідає саме цим значенням
#define BME280_REG_PRESS 0xF7   // перший із трьох байтів сирого тиску

typedef struct {
    baro_t   base;        // ПЕРШИМ полем — щоб (baro_t*)self працювало (крок 2)
    uint8_t  addr;        // 7-бітна адреса на шині: 0x76 (SDO→GND) або 0x77 (SDO→VDDIO)
    int32_t  t_fine;      // калібрувальний контекст компенсації (спрощено)
} bme280_i2c_t;

// Перетворити сирий 20-бітний відлік у паскалі. Реальна компенсація BME280 —
// довгий поліном на калібрувальних коефіцієнтах; тут лишаємо суть прикладу:
// драйвер ВІДДАЄ паскалі, політика НЕ знає про сирі відліки.
static uint32_t compensate(bme280_i2c_t *d, int32_t raw) {
    (void)d;                       // у повному драйвері тут ідуть dig_P1..P9, t_fine
    return 30000u + (uint32_t)(raw & 0x000FFFFF) / 16u;   // навмисно спрощено
}

static baro_status_t i2c_read(baro_t *self, uint32_t *out_pa) {
    bme280_i2c_t *d = (bme280_i2c_t *)self;   // відновлюємо повний тип із base
    uint8_t raw[3];
    if (i2c_read_reg(d->addr, BME280_REG_PRESS, raw, 3) != 0) {
        return BARO_ERR_BUS;       // немає ACK / таймаут — шина мовчить
    }
    int32_t v = ((int32_t)raw[0] << 12) | ((int32_t)raw[1] << 4) | (raw[2] >> 4);
    uint32_t pa = compensate(d, v);
    if (pa < 30000u || pa > 110000u) {
        return BARO_ERR_RANGE;     // фізично неможливий тиск — давач здурів
    }
    *out_pa = pa;                  // чіпаємо вихід ЛИШЕ на успіху (контракт)
    return BARO_OK;
}

static void i2c_close(baro_t *self) {
    free(self);                    // шину тут тримає плата; звільняємо лише пам'ять
}

// Єдина на цей файл таблиця методів — спільна для всіх екземплярів драйвера.
static const baro_vtable_t BME280_I2C_VT = { .read = i2c_read, .close = i2c_close };

// Фабрика: відкрити давач на шині I2C. Підпис СВІЙ — параметри саме для I2C.
// Повертає baro_t* (абстракцію) або NULL, якщо чипа немає / не той.
baro_t *bme280_i2c_open(uint8_t addr) {
    uint8_t id = 0;
    if (i2c_read_reg(addr, BME280_REG_ID, &id, 1) != 0) return NULL;  // шина мовчить
    if (id != BME280_CHIP_ID) return NULL;                            // не BME280

    bme280_i2c_t *d = malloc(sizeof *d);
    if (!d) return NULL;
    d->base.vt = &BME280_I2C_VT;   // підставляємо таблицю — тепер це чесний baro_t
    d->addr    = addr;
    d->t_fine  = 0;
    return &d->base;               // віддаємо адресу base == адреса структури
}
