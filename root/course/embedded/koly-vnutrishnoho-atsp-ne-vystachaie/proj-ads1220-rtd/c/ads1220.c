#include "ads1220.h"

#include <string.h>

/* Команди мікросхеми */
#define CMD_RESET       0x06u
#define CMD_START       0x08u
#define CMD_RDATA       0x10u
#define CMD_RREG(r, n)  ((uint8_t)(0x20u | ((r) << 2) | ((n) - 1u)))
#define CMD_WREG(r, n)  ((uint8_t)(0x40u | ((r) << 2) | ((n) - 1u)))

/* Робоча конфігурація для 3-провідного PT100 — розібрана в статті */
#define REG0_MEASURE    0x38u  /* вхід AIN1-AIN2, підсилення 16, PGA увімкнено */
#define REG0_OFFSET     0xE8u  /* входи закорочені на (AVDD+AVSS)/2, підсилення 16 */
#define REG1_WORK       0x00u  /* 20 вибірок/с, звичайний режим, одиничне перетворення */
#define REG2_WORK       0x76u  /* зовнішня опора REFP0/REFN0, фільтр 50/60 Гц, IDAC 500 мкА */
#define REG3_WORK       0x60u  /* IDAC1 на AIN0, IDAC2 на AIN1, окремий вивід DRDY */

#define SPI_TIMEOUT_MS      10u
#define CONV_TIMEOUT_MS     100u  /* 20 вибірок/с дають ~50 мс, решта — запас */
#define OFFSET_AVG_COUNT    8

#define CODE_POS_FULL_SCALE   0x7FFFFF
#define CODE_NEG_FULL_SCALE  (-0x800000)
#define CODE_RAIL_MARGIN      16       /* наскільки близько до шкали вже вважаємо збоєм */

/* Один обмін по SPI під притиснутим CS. Мікросхема відповідає на кожен
   переданий байт, тому читання завжди йде тим самим викликом, що й запис. */
static ads1220_status_t spi_xfer(ads1220_t *dev, const uint8_t *tx, uint8_t *rx, uint16_t len)
{
    uint8_t scratch[8];

    if (len > (uint16_t)sizeof scratch) {
        return ADS1220_ERR_ARG;
    }
    uint8_t *dst = (rx != NULL) ? rx : scratch;

    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef hal = HAL_SPI_TransmitReceive(dev->spi, (uint8_t *)tx, dst,
                                                    len, SPI_TIMEOUT_MS);
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);

    return (hal == HAL_OK) ? ADS1220_OK : ADS1220_ERR_SPI;
}

/* Перезапис лише нульового регістра — ним перемикають мультиплексор входу */
static ads1220_status_t write_reg0(ads1220_t *dev, uint8_t value)
{
    const uint8_t frame[2] = { CMD_WREG(0, 1), value };
    return spi_xfer(dev, frame, NULL, sizeof frame);
}

/* Запуск перетворення й очікування апаратного DRDY.
   Одиничне перетворення означає, що струми збудження течуть крізь
   датчик лише ці ~50 мс — саме тому саморозігрів лишається мізерним. */
static ads1220_status_t convert_once(ads1220_t *dev, int32_t *code)
{
    dev->drdy = 0;

    const uint8_t start = CMD_START;
    ads1220_status_t st = spi_xfer(dev, &start, NULL, 1);
    if (st != ADS1220_OK) {
        return st;
    }

    const uint32_t started = HAL_GetTick();
    while (dev->drdy == 0u) {
        if ((HAL_GetTick() - started) > CONV_TIMEOUT_MS) {
            return ADS1220_ERR_TIMEOUT;
        }
        __WFI(); /* спимо до наступного переривання: DRDY або системний тик */
    }

    const uint8_t frame[4] = { CMD_RDATA, 0x00, 0x00, 0x00 };
    uint8_t rx[4] = { 0 };
    st = spi_xfer(dev, frame, rx, sizeof frame);
    if (st != ADS1220_OK) {
        return st;
    }

    int32_t value = ((int32_t)rx[1] << 16) | ((int32_t)rx[2] << 8) | (int32_t)rx[3];
    if (value & 0x00800000) {
        value -= 0x01000000; /* доповнення знакового розряду до 32 біт */
    }
    *code = value;
    return ADS1220_OK;
}

ads1220_status_t ads1220_init(ads1220_t *dev)
{
    if (dev == NULL || dev->spi == NULL || dev->cs_port == NULL) {
        return ADS1220_ERR_ARG;
    }
    if (dev->r_ref <= 0.0f || dev->gain <= 0.0f) {
        return ADS1220_ERR_ARG;
    }

    dev->offset_code = 0;
    dev->drdy = 0;

    const uint8_t reset = CMD_RESET;
    ads1220_status_t st = spi_xfer(dev, &reset, NULL, 1);
    if (st != ADS1220_OK) {
        return st;
    }
    HAL_Delay(1); /* після скидання мікросхемі треба ~50 мкс плюс 32 такти */

    const uint8_t cfg[5] = {
        CMD_WREG(0, 4), REG0_MEASURE, REG1_WORK, REG2_WORK, REG3_WORK
    };
    st = spi_xfer(dev, cfg, NULL, sizeof cfg);
    if (st != ADS1220_OK) {
        return st;
    }

    /* Перечитуємо записане. Обірваний MISO, переплутаний CS чи неправильний
       режим SPI інакше виявляться аж на дивних показах температури, коли
       шукати причину вже вчетверо дорожче. */
    const uint8_t rreg[5] = { CMD_RREG(0, 4), 0x00, 0x00, 0x00, 0x00 };
    uint8_t back[5] = { 0 };
    st = spi_xfer(dev, rreg, back, sizeof rreg);
    if (st != ADS1220_OK) {
        return st;
    }
    if (memcmp(&back[1], &cfg[1], 4) != 0) {
        return ADS1220_ERR_CONFIG;
    }

    return ADS1220_OK;
}

ads1220_status_t ads1220_calibrate_offset(ads1220_t *dev)
{
    if (dev == NULL) {
        return ADS1220_ERR_ARG;
    }

    ads1220_status_t st = write_reg0(dev, REG0_OFFSET);
    if (st != ADS1220_OK) {
        return st;
    }

    int32_t code = 0;
    int64_t sum = 0;

    /* Перший відлік після перемикання мультиплексора беремо й викидаємо:
       вхідний ланцюг цифрового фільтра ще пам'ятає попередній сигнал. */
    st = convert_once(dev, &code);
    for (int i = 0; st == ADS1220_OK && i < OFFSET_AVG_COUNT; i++) {
        st = convert_once(dev, &code);
        if (st == ADS1220_OK) {
            sum += code;
        }
    }

    /* Робочу конфігурацію входу повертаємо навіть після невдачі:
       інакше наступний вимір мовчки читав би закорочені входи. */
    ads1220_status_t restore = write_reg0(dev, REG0_MEASURE);
    if (st != ADS1220_OK) {
        return st;
    }
    if (restore != ADS1220_OK) {
        return restore;
    }

    dev->offset_code = (int32_t)(sum / OFFSET_AVG_COUNT);
    return ADS1220_OK;
}

ads1220_status_t ads1220_read_resistance(ads1220_t *dev, float *r_ohms)
{
    if (dev == NULL || r_ohms == NULL) {
        return ADS1220_ERR_ARG;
    }

    int32_t code = 0;
    ads1220_status_t st = convert_once(dev, &code);
    if (st != ADS1220_OK) {
        return st;
    }

    /* Код, упертий у край шкали, — це не гаряча пічка, а обірваний дріт
       або закорочений датчик: рахувати з нього температуру нема сенсу. */
    if (code >= (CODE_POS_FULL_SCALE - CODE_RAIL_MARGIN) ||
        code <= (CODE_NEG_FULL_SCALE + CODE_RAIL_MARGIN)) {
        return ADS1220_ERR_RANGE;
    }

    code -= dev->offset_code;

    /* Логометричний перерахунок: струм збудження скорочується, лишається
       відношення опору датчика до еталонного резистора. */
    *r_ohms = ((float)code * 2.0f * dev->r_ref) / (8388608.0f * dev->gain);
    return ADS1220_OK;
}

void ads1220_drdy_isr(ads1220_t *dev)
{
    dev->drdy = 1;
}

const char *ads1220_strerror(ads1220_status_t status)
{
    switch (status) {
    case ADS1220_OK:           return "ok";
    case ADS1220_ERR_ARG:      return "хибний аргумент";
    case ADS1220_ERR_SPI:      return "збій обміну по SPI";
    case ADS1220_ERR_CONFIG:   return "регістри не підтвердилися";
    case ADS1220_ERR_TIMEOUT:  return "DRDY не відгукнувся";
    case ADS1220_ERR_RANGE:    return "датчик обірваний або закорочений";
    default:                   return "невідома помилка";
    }
}
