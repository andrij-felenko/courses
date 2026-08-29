#ifndef SHT3X_H
#define SHT3X_H

/* Драйвер цифрового термогігрометра Sensirion SHT3x (SHT30/31/35).
   Прив'язки до конкретного мікроконтролера в ньому немає: доступ до шини
   й затримку драйвер отримує покажчиками на функції в структурі sht3x_t. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* 7-бітна адреса задається виводом ADDR: до GND — 0x44, до VDD — 0x45.
   Зсув на біт ліворуч і біт напрямку робить драйвер шини, не ми. */
#define SHT3X_ADDR_GND 0x44u
#define SHT3X_ADDR_VDD 0x45u

typedef enum {
    SHT3X_OK = 0,
    SHT3X_ERR_PARAM,        /* хибний аргумент або недозаповнений хендл */
    SHT3X_ERR_NO_DEVICE,    /* чип не відгукується на адресу після POR */
    SHT3X_ERR_I2C_WRITE,    /* сенсор не підтвердив адресу або байт команди */
    SHT3X_ERR_I2C_READ,     /* сенсор не віддав кадр результату */
    SHT3X_ERR_CRC_TEMP,     /* спотворене слово температури */
    SHT3X_ERR_CRC_HUMI,     /* спотворене слово вологості */
    SHT3X_ERR_CRC_STATUS    /* спотворене слово регістра стану */
} sht3x_status_t;

/* Повторюваність вимірювання: що вища, то довше працює сигма-дельта
   модулятор і то менший шум результату. */
typedef enum {
    SHT3X_REP_HIGH = 0,     /* t_meas 12.5..15.0 мс */
    SHT3X_REP_MEDIUM,       /* t_meas  4.5.. 6.0 мс */
    SHT3X_REP_LOW           /* t_meas  2.5.. 4.0 мс */
} sht3x_rep_t;

/* Результат одного вимірювання. Фізичні величини — у цілих числах
   із фіксованою комою, щоб драйвер працював і без апаратного FPU. */
typedef struct {
    uint16_t raw_t;             /* сирий код АЦП температури */
    uint16_t raw_rh;            /* сирий код АЦП вологості */
    int32_t  temperature_mc;    /* міліградуси Цельсія: 23729 = +23.729 °C */
    uint32_t humidity_cpm;      /* соті частки відсотка: 4155 = 41.55 %RH */
} sht3x_meas_t;

/* Апаратний шар. Обидві функції обміну повертають true, якщо всі байти
   транзакції отримали ACK; ctx передається наскрізь (хендл периферії). */
typedef struct {
    bool (*i2c_write)(uint8_t addr7, const uint8_t *data, size_t len, void *ctx);
    bool (*i2c_read)(uint8_t addr7, uint8_t *data, size_t len, void *ctx);
    void (*delay_ms)(uint32_t ms, void *ctx);
    void    *ctx;
    uint8_t  addr7;
    uint32_t bus_errors;    /* скільки транзакцій зірвалося на шині */
    uint32_t crc_errors;    /* скільки кадрів відкинуто через CRC */
} sht3x_t;

/* Витримує паузу POR і переконується, що чип відповідає на свою адресу. */
sht3x_status_t sht3x_init(sht3x_t *dev);

/* Разове вимірювання: команда, пауза t_meas, зчитування 6 байтів, CRC. */
sht3x_status_t sht3x_measure(sht3x_t *dev, sht3x_rep_t rep, sht3x_meas_t *out);

/* Те саме з повторами через 30 мс: одиночна завада на лінії не має
   зупиняти прилад, але й підсовувати спотворене число нікому не можна. */
sht3x_status_t sht3x_measure_retry(sht3x_t *dev, sht3x_rep_t rep,
                                   sht3x_meas_t *out, uint8_t attempts);

/* Вбудований нагрівач (~33 мВт): десорбція конденсату й діагностика. */
sht3x_status_t sht3x_heater(sht3x_t *dev, bool on);

/* Регістр стану чипа (16 біт + CRC). */
sht3x_status_t sht3x_read_status(sht3x_t *dev, uint16_t *status);

/* Текст помилки для журналу. */
const char *sht3x_strerror(sht3x_status_t st);

/* Ті самі величини у float — для машин, де FPU є і економити нема на чому. */
static inline float sht3x_temperature_c(const sht3x_meas_t *m)
{
    return -45.0f + 175.0f * ((float)m->raw_t / 65535.0f);
}

static inline float sht3x_humidity_rh(const sht3x_meas_t *m)
{
    return 100.0f * ((float)m->raw_rh / 65535.0f);
}

#endif /* SHT3X_H */
