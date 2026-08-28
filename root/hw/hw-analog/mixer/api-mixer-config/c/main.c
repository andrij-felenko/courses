#include <stdint.h>
#include <stdbool.h>

/* Адреси регістрів змішувача */
#define MIXER_REG_POWER   0x00
#define MIXER_REG_GAIN    0x01
#define MIXER_REG_BIAS    0x02
#define MIXER_REG_LO_BUFF 0x03

/* Прототип зовнішньої функції запису SPI */
extern void spi_write_register(uint8_t reg_addr, uint16_t reg_val);
extern void delay_us(uint32_t microseconds);

/* Структура конфігурації змішувача */
typedef struct {
    uint8_t  if_gain_db;    /* 0..18 dB */
    bool     rf_atten_en;   /* true = enable -10dB RF attenuation */
    uint8_t  iip3_mode;     /* 0 = Low Power, 1 = Normal, 2 = High Linearity */
    uint8_t  lo_divider;    /* 1, 2, 4, 8 */
} rf_mixer_config_t;

/* Процедура ініціалізації та конфігурації ВЧ-змішувача */
int rf_mixer_configure(const rf_mixer_config_t *cfg) {
    uint16_t reg_val = 0;

    /* 1. Подача живлення аналогового ядра та буфера LO */
    spi_write_register(MIXER_REG_POWER, 0x0003); // Power Up + LO Buffer EN
    delay_us(20); // Чекаємо стабілізації внутрішнього Bandgap (15 мкс)

    /* 2. Налаштування підсилення IF та атенюатора RF */
    reg_val = (cfg->if_gain_db & 0x1F);
    if (cfg->rf_atten_en) {
        reg_val |= (1 << 5);
    }
    spi_write_register(MIXER_REG_GAIN, reg_val);

    /* 3. Налаштування струму спокою для оптимізації IIP3 */
    switch (cfg->iip3_mode) {
        case 0: reg_val = 0x0000; break; // Low-power (+2 dBm)
        case 1: reg_val = 0x0003; break; // Normal (+10 dBm)
        case 2: reg_val = 0x0007; break; // High-Linearity (+18 dBm)
        default: return -1;
    }
    spi_write_register(MIXER_REG_BIAS, reg_val);

    /* 4. Налаштування дільника та підсилювача LO */
    reg_val = (cfg->lo_divider & 0x07);
    spi_write_register(MIXER_REG_LO_BUFF, reg_val);

    return 0; // Успішно
}
