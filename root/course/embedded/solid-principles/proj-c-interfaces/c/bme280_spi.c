// bme280_spi.c — та сама абстракція baro_t, але поверх SPI. Новий файл — OCP.
#include "baro.h"
#include "spi.h"          // spi_transfer / gpio_set — примітиви плати
#include "i2c.h"          // (не потрібен) — навмисно НЕ включаємо; SPI самодостатній

#define BME280_REG_ID    0xD0
#define BME280_CHIP_ID   0x60
#define BME280_REG_PRESS 0xF7
#define SPI_READ         0x00   // старший біт першого байта: 0 → читання
#define SPI_WRITE        0x80   // ... 1 → запис

typedef struct {
    baro_t  base;         // знову ПЕРШИМ полем
    uint8_t cs_pin;       // лінія вибору кристала саме цього давача
} bme280_spi_t;

// Прочитати n байтів із регістра по SPI: опустити CS, послати адресу, забрати дані.
static int spi_read_reg(uint8_t cs, uint8_t reg, uint8_t *buf, int n) {
    gpio_set(cs, 0);                       // вибрали кристал — обмін почався
    spi_transfer((reg & 0x7F) | SPI_READ); // адреса з бітом читання
    for (int i = 0; i < n; i++) {
        buf[i] = spi_transfer(0x00);       // висуваємо порожнє, забираємо корисне
    }
    gpio_set(cs, 1);                       // відпустили кристал
    return 0;                              // SPI не квитує — апаратного «немає ACK» нема
}

static uint32_t compensate(bme280_spi_t *d, int32_t raw) {
    (void)d;
    return 30000u + (uint32_t)(raw & 0x000FFFFF) / 16u;   // те саме спрощення, що в I2C
}

static baro_status_t spi_read(baro_t *self, uint32_t *out_pa) {
    bme280_spi_t *d = (bme280_spi_t *)self;
    uint8_t raw[3];
    spi_read_reg(d->cs_pin, BME280_REG_PRESS, raw, 3);     // SPI завжди «успіх» на рівні шини
    int32_t v = ((int32_t)raw[0] << 12) | ((int32_t)raw[1] << 4) | (raw[2] >> 4);
    uint32_t pa = compensate(d, v);
    if (pa < 30000u || pa > 110000u) {
        return BARO_ERR_RANGE;
    }
    *out_pa = pa;
    return BARO_OK;
}

static void spi_close(baro_t *self) { free(self); }

static const baro_vtable_t BME280_SPI_VT = { .read = spi_read, .close = spi_close };

// Фабрика SPI: підпис СВІЙ — їй потрібна ніжка CS, а не I2C-адреса.
baro_t *bme280_spi_open(uint8_t cs_pin) {
    uint8_t id = 0;
    spi_read_reg(cs_pin, BME280_REG_ID, &id, 1);
    if (id != BME280_CHIP_ID) return NULL;     // не той чип — не віддаємо калічний давач

    bme280_spi_t *d = malloc(sizeof *d);
    if (!d) return NULL;
    d->base.vt = &BME280_SPI_VT;
    d->cs_pin  = cs_pin;
    return &d->base;
}
