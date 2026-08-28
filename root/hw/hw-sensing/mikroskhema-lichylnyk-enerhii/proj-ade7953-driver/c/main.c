#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Адреси регістрів ADE7953 */
#define ADE7953_REG_CONFIG2      0x00FE  /* 8-bit: SPI lock register */
#define ADE7953_REG_PGA_IA       0x0080  /* 8-bit: PGA IA gain */
#define ADE7953_REG_PGA_IB       0x0081  /* 8-bit: PGA IB gain */
#define ADE7953_REG_PGA_V        0x0082  /* 8-bit: PGA Voltage gain */
#define ADE7953_REG_CONFIG       0x0102  /* 16-bit: System config */
#define ADE7953_REG_ACCMODE      0x0103  /* 16-bit: Accumulation & Tamper mode */
#define ADE7953_REG_CF1DEN       0x0105  /* 16-bit: CF1 pulse denominator */
#define ADE7953_REG_APHCAL       0x0108  /* 10-bit: Channel A phase calibration */
#define ADE7953_REG_PFA          0x010A  /* 16-bit: Power factor IA */
#define ADE7953_REG_AWATT        0x0212  /* 24-bit: Active power IA */
#define ADE7953_REG_AVAR         0x0214  /* 24-bit: Reactive power IA */
#define ADE7953_REG_AVA          0x0216  /* 24-bit: Apparent power IA */
#define ADE7953_REG_ISUMLVL      0x0218  /* 24-bit: Tamper current threshold */
#define ADE7953_REG_AIRMS        0x021A  /* 24-bit: RMS Current IA */
#define ADE7953_REG_BIRMS        0x0219  /* 24-bit: RMS Current IB */
#define ADE7953_REG_VRMS         0x021B  /* 24-bit: RMS Voltage */
#define ADE7953_REG_AIGAIN       0x021C  /* 24-bit: Current Gain IA */
#define ADE7953_REG_AVGAIN       0x021E  /* 24-bit: Voltage Gain */
#define ADE7953_REG_AIRMSOS      0x0223  /* 24-bit: RMS Current Offset IA */
#define ADE7953_REG_AVRMSOS      0x0225  /* 24-bit: RMS Voltage Offset */
#define ADE7953_REG_IRQENA       0x022C  /* 24-bit: Interrupt enable A */
#define ADE7953_REG_IRQSTATA     0x022D  /* 24-bit: Interrupt status A */
#define ADE7953_REG_RSTIRQSTATA  0x032D  /* 24-bit: Read with reset status A */
#define ADE7953_REG_AENERGYA     0x031E  /* 32-bit: Active energy IA */
#define ADE7953_REG_AENERGYB     0x031F  /* 32-bit: Active energy IB */

/* Біти переривань */
#define ADE7953_IRQ_MISMTCH      (1UL << 14)
#define ADE7953_IRQ_ZX           (1UL << 3)

/* Структура конфігурації та калібрувальних коефіцієнтів */
typedef struct {
    uint8_t pga_ia;         /* 0=1x, 1=2x, 2=4x, 3=8x, 4=16x, 5=22x */
    uint8_t pga_ib;
    uint8_t pga_v;
    int32_t aigain;         /* 24-bit підсилення струму */
    int32_t avgain;         /* 24-bit підсилення напруги */
    int32_t airmsos;        /* 24-bit зріз шуму RMS */
    int16_t aphcal;         /* 10-bit калібрування фази */
    uint16_t cf1den;        /* Дільник імпульсів CF1 */
    float v_scale;          /* Коефіцієнт перерахунку LSB -> Вольт */
    float i_scale;          /* Коефіцієнт перерахунку LSB -> Ампер */
    float p_scale;          /* Коефіцієнт перерахунку LSB -> Ват */
} ade7953_calib_t;

/* Структура виміряних метрик мережі */
typedef struct {
    float voltage_rms;      /* Напруга, В */
    float current_a_rms;    /* Струм фази, А */
    float current_b_rms;    /* Струм нейтралі, А */
    float active_power;     /* Активна потужність, Вт */
    float reactive_power;   /* Реактивна потужність, вар */
    float apparent_power;   /* Повна потужність, ВА */
    float power_factor;     /* Коефіцієнт потужності cos phi */
    int32_t energy_a_raw;   /* Сире значення активної енергії фази */
    bool tamper_detected;   /* Прапорець виявлення розкрадання */
} ade7953_metrics_t;

/* Платформозалежний інтерфейс SPI (надається користувачем) */
typedef struct {
    void (*cs_low)(void);
    void (*cs_high)(void);
    void (*spi_transfer)(const uint8_t *tx, uint8_t *rx, uint16_t len);
    void (*delay_ms)(uint32_t ms);
} ade7953_hal_t;

/* Контекст драйвера */
typedef struct {
    ade7953_hal_t hal;
    ade7953_calib_t calib;
} ade7953_dev_t;

/* Низькорівневий запис регістрів різної розрядності */
static void ade7953_write_reg(ade7953_dev_t *dev, uint16_t reg, uint32_t val, uint8_t bytes) {
    uint8_t tx[7];
    tx[0] = (uint8_t)(reg >> 8);
    tx[1] = (uint8_t)(reg & 0xFF);
    tx[2] = 0x00; /* Команда запису */

    for (int i = 0; i < bytes; i++) {
        tx[3 + i] = (uint8_t)(val >> ((bytes - 1 - i) * 8));
    }

    dev->hal.cs_low();
    dev->hal.spi_transfer(tx, NULL, 3 + bytes);
    dev->hal.cs_high();
}

/* Низькорівневе читання регістрів */
static uint32_t ade7953_read_reg(ade7953_dev_t *dev, uint16_t reg, uint8_t bytes) {
    uint8_t tx[7] = {0};
    uint8_t rx[7] = {0};
    tx[0] = (uint8_t)(reg >> 8);
    tx[1] = (uint8_t)(reg & 0xFF);
    tx[2] = 0x80; /* Команда читання */

    dev->hal.cs_low();
    dev->hal.spi_transfer(tx, rx, 3 + bytes);
    dev->hal.cs_high();

    uint32_t result = 0;
    for (int i = 0; i < bytes; i++) {
        result = (result << 8) | rx[3 + i];
    }
    return result;
}

/* Читання регістра зі знаком (двійковий додатковий код) */
static int32_t ade7953_read_signed(ade7953_dev_t *dev, uint16_t reg, uint8_t bytes) {
    uint32_t raw = ade7953_read_reg(dev, reg, bytes);
    if (bytes == 3) {
        if (raw & 0x800000) raw |= 0xFF000000; /* Розширення знакового біта 24 -> 32 */
    } else if (bytes == 2) {
        if (raw & 0x8000) raw |= 0xFFFF0000;
    }
    return (int32_t)raw;
}

/* Ініціалізація та блокування SPI */
bool ade7953_init(ade7953_dev_t *dev, const ade7953_hal_t *hal, const ade7953_calib_t *calib) {
    dev->hal = *hal;
    dev->calib = *calib;

    /* Програмне скидання */
    ade7953_write_reg(dev, ADE7953_REG_CONFIG, 0x0080, 2);
    dev->hal.delay_ms(15);

    /* Фіксація режиму SPI: запис 0xAD у регістр 0x00FE */
    ade7953_write_reg(dev, ADE7953_REG_CONFIG2, 0xAD, 1);

    /* Налаштування вхідних підсилювачів PGA */
    ade7953_write_reg(dev, ADE7953_REG_PGA_IA, dev->calib.pga_ia, 1);
    ade7953_write_reg(dev, ADE7953_REG_PGA_IB, dev->calib.pga_ib, 1);
    ade7953_write_reg(dev, ADE7953_REG_PGA_V, dev->calib.pga_v, 1);

    /* Завантаження калібрувальних коефіцієнтів */
    ade7953_write_reg(dev, ADE7953_REG_AIGAIN, (uint32_t)dev->calib.aigain, 3);
    ade7953_write_reg(dev, ADE7953_REG_AVGAIN, (uint32_t)dev->calib.avgain, 3);
    ade7953_write_reg(dev, ADE7953_REG_AIRMSOS, (uint32_t)dev->calib.airmsos, 3);
    ade7953_write_reg(dev, ADE7953_REG_APHCAL, (uint32_t)dev->calib.aphcal, 2);
    ade7953_write_reg(dev, ADE7953_REG_CF1DEN, dev->calib.cf1den, 2);

    /* Увімкнення режиму автоматичного обліку Anti-Tamper (біти в ACCMODE) */
    ade7953_write_reg(dev, ADE7953_REG_ACCMODE, 0x0008, 2);

    /* Дозвіл переривання виявлення дисбалансу струмів */
    ade7953_write_reg(dev, ADE7953_REG_IRQENA, ADE7953_IRQ_MISMTCH, 3);

    return true;
}

/* Зчитування поточних метрологічних параметрів */
void ade7953_read_metrics(ade7953_dev_t *dev, ade7953_metrics_t *metrics) {
    uint32_t v_raw = ade7953_read_reg(dev, ADE7953_REG_VRMS, 3);
    uint32_t ia_raw = ade7953_read_reg(dev, ADE7953_REG_AIRMS, 3);
    uint32_t ib_raw = ade7953_read_reg(dev, ADE7953_REG_BIRMS, 3);
    int32_t p_raw = ade7953_read_signed(dev, ADE7953_REG_AWATT, 3);
    int32_t q_raw = ade7953_read_signed(dev, ADE7953_REG_AVAR, 3);
    int32_t s_raw = ade7953_read_signed(dev, ADE7953_REG_AVA, 3);
    int16_t pf_raw = (int16_t)ade7953_read_reg(dev, ADE7953_REG_PFA, 2);
    int32_t energy_raw = (int32_t)ade7953_read_reg(dev, ADE7953_REG_AENERGYA, 4);

    uint32_t irq_stat = ade7953_read_reg(dev, ADE7953_REG_RSTIRQSTATA, 3);

    metrics->voltage_rms = (float)v_raw * dev->calib.v_scale;
    metrics->current_a_rms = (float)ia_raw * dev->calib.i_scale;
    metrics->current_b_rms = (float)ib_raw * dev->calib.i_scale;
    metrics->active_power = (float)p_raw * dev->calib.p_scale;
    metrics->reactive_power = (float)q_raw * dev->calib.p_scale;
    metrics->apparent_power = (float)s_raw * dev->calib.p_scale;
    metrics->power_factor = (float)pf_raw / 32768.0f;
    metrics->energy_a_raw = energy_raw;
    metrics->tamper_detected = (irq_stat & ADE7953_IRQ_MISMTCH) != 0;
}
