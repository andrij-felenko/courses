#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Команди ADS1220 */
#define ADS1220_CMD_RESET    0x06
#define ADS1220_CMD_START    0x08
#define ADS1220_CMD_RDATA    0x10
#define ADS1220_CMD_RREG     0x20
#define ADS1220_CMD_WREG     0x40

/* Конфігураційні константи */
#define PT100_R0             100.0f
#define PT100_A              3.9083e-3f
#define PT100_B              -5.7750e-7f
#define PT100_C              -4.1830e-12f
#define R_REF_NOMINAL        3300.0f
#define PGA_GAIN             16.0f

typedef struct {
    void (*spi_cs_low)(void);
    void (*spi_cs_high)(void);
    void (*spi_transfer)(const uint8_t *tx, uint8_t *rx, uint16_t len);
    bool (*wait_drdy_low)(uint32_t timeout_ms);
} ads1220_hal_t;

typedef struct {
    ads1220_hal_t hal;
    float r_ref;
    float gain;
    int32_t offset_code;
} ads1220_t;

/* Ініціалізація та налаштування регістрів ADS1220 для 3-провідного PT100 */
bool ads1220_init(ads1220_t *dev, const ads1220_hal_t *hal) {
    if (!dev || !hal) return false;
    dev->hal = *hal;
    dev->r_ref = R_REF_NOMINAL;
    dev->gain = PGA_GAIN;
    dev->offset_code = 0;

    /* Скидання мікросхеми */
    uint8_t cmd_reset = ADS1220_CMD_RESET;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_reset, NULL, 1);
    dev->hal.spi_cs_high();

    /* Запис 4 конфігураційних регістрів */
    uint8_t config[5];
    config[0] = ADS1220_CMD_WREG | 0x03; /* Запис 4 байтів починаючи з регістру 0 */
    config[1] = 0x38; /* AIN1-AIN2, Gain=16, PGA on */
    config[2] = 0x00; /* 20 SPS, Normal mode, Single-shot */
    config[3] = 0x76; /* Зовнішня опора REFP0/REFN0, фільтр 50/60 Гц, IDAC=500 мкА */
    config[4] = 0x60; /* IDAC1 -> AIN0, IDAC2 -> AIN1 */

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(config, NULL, 5);
    dev->hal.spi_cs_high();

    return true;
}

/* Калібрування внутрішнього зсуву нуля АЦП через тестове замикання входів */
bool ads1220_calibrate_offset(ads1220_t *dev) {
    if (!dev) return false;

    /* Вмикання режиму (AVDD + AVSS)/2 на обох входах для виміру зміщення */
    uint8_t reg0_cal = 0xE8; /* MUX = (AVDD-AVSS)/2, Gain=16 */
    uint8_t cmd[2] = { (uint8_t)(ADS1220_CMD_WREG | 0x00), reg0_cal };
    
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(cmd, NULL, 2);
    dev->hal.spi_cs_high();

    /* Запуск та читання тестового відліку */
    uint8_t cmd_start = ADS1220_CMD_START;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_start, NULL, 1);
    dev->hal.spi_cs_high();

    if (!dev->hal.wait_drdy_low(60)) return false;

    uint8_t tx_buf[4] = { ADS1220_CMD_RDATA, 0x00, 0x00, 0x00 };
    uint8_t rx_buf[4] = { 0 };

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(tx_buf, rx_buf, 4);
    dev->hal.spi_cs_high();

    int32_t offset = ((int32_t)rx_buf[1] << 16) |
                     ((int32_t)rx_buf[2] << 8)  |
                     ((int32_t)rx_buf[3]);
    if (offset & 0x00800000) offset |= 0xFF000000;
    dev->offset_code = offset;

    /* Відновлення робочої конфігурації входу */
    cmd[1] = 0x38;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(cmd, NULL, 2);
    dev->hal.spi_cs_high();

    return true;
}

/* Запуск вимірювання та зчитування 24-бітного результату */
bool ads1220_read_raw(ads1220_t *dev, int32_t *raw_code) {
    if (!dev || !raw_code) return false;

    uint8_t cmd_start = ADS1220_CMD_START;
    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(&cmd_start, NULL, 1);
    dev->hal.spi_cs_high();

    /* Очікування сигналу DRDY за апаратним перериванням або тайм-аутом */
    if (!dev->hal.wait_drdy_low(60)) {
        return false;
    }

    uint8_t tx_buf[4] = { ADS1220_CMD_RDATA, 0x00, 0x00, 0x00 };
    uint8_t rx_buf[4] = { 0 };

    dev->hal.spi_cs_low();
    dev->hal.spi_transfer(tx_buf, rx_buf, 4);
    dev->hal.spi_cs_high();

    /* Збирання 24-бітного числа зі знаком */
    int32_t code = ((int32_t)rx_buf[1] << 16) |
                   ((int32_t)rx_buf[2] << 8)  |
                   ((int32_t)rx_buf[3]);

    /* Доповнення знакового розряду для 24-бітного значення */
    if (code & 0x00800000) {
        code |= 0xFF000000;
    }

    /* Компенсація каліброваного апаратного зміщення */
    *raw_code = code - dev->offset_code;
    return true;
}

/* Перерахунок коду в опір та температуру за рівнянням Каллендара-Ван Дюзена */
bool ads1220_read_temperature(ads1220_t *dev, float *temp_celsius) {
    int32_t raw_code = 0;
    if (!ads1220_read_raw(dev, &raw_code)) return false;

    /* Логометричний розрахунок опору RTD */
    float r_pt100 = ((float)raw_code * 2.0f * dev->r_ref) / (8388608.0f * dev->gain);

    /* Розрахунок температури для T >= 0 °C */
    float z = 1.0f - (r_pt100 / PT100_R0);
    float discriminant = (PT100_A * PT100_A) - (4.0f * PT100_B * z);

    if (discriminant < 0.0f) {
        return false; /* Неприпустиме значення опору */
    }

    float t = (-PT100_A + sqrtf(discriminant)) / (2.0f * PT100_B);

    /* Ітеративне уточнення для діапазону від'ємних температур T < 0 °C */
    if (t < 0.0f) {
        for (int i = 0; i < 3; i++) {
            float t2 = t * t;
            float t3 = t2 * t;
            float r_calc = PT100_R0 * (1.0f + PT100_A * t + PT100_B * t2 + PT100_C * (t - 100.0f) * t3);
            float r_diff = PT100_R0 * (PT100_A + 2.0f * PT100_B * t - 300.0f * PT100_C * t2 + 4.0f * PT100_C * t3);
            t = t - (r_calc - r_pt100) / r_diff;
        }
    }

    *temp_celsius = t;
    return true;
}
