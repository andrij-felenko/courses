#include "ad2s1210.h"
#include <math.h>
#include <string.h>

/* Внутрішня карта регістрів AD2S1210 (у конфігураційному режимі A0=1, A1=1) */
#define AD2S1210_REG_POSITION_MSB   0x80
#define AD2S1210_REG_POSITION_LSB   0x81
#define AD2S1210_REG_VELOCITY_MSB   0x82
#define AD2S1210_REG_VELOCITY_LSB   0x83
#define AD2S1210_REG_EXCITATION_FREQ 0x91
#define AD2S1210_REG_CONTROL        0x92
#define AD2S1210_REG_SOFT_RESET     0xE0
#define AD2S1210_REG_FAULT          0xFF

/* Таймінги затримки сигналів за специфікацією AD2S1210 (у мікросекундах) */
#define AD2S1210_T_SAMPLE_US        1
#define AD2S1210_T_SETTLE_US        1
#define AD2S1210_T_RESET_US         10

/* Допоміжні функції для роботи з HAL */
static inline void hal_gpio_write(ad2s1210_dev_t *dev, ad2s1210_pin_t pin, ad2s1210_pin_state_t state) {
    if (dev->config.gpio_write) {
        dev->config.gpio_write(dev->config.user_ctx, pin, state);
    }
}

static inline ad2s1210_pin_state_t hal_gpio_read(ad2s1210_dev_t *dev, ad2s1210_pin_t pin) {
    if (dev->config.gpio_read) {
        return dev->config.gpio_read(dev->config.user_ctx, pin);
    }
    return AD2S1210_PIN_HIGH;
}

static inline void hal_delay_us(ad2s1210_dev_t *dev, uint32_t us) {
    if (dev->config.delay_us) {
        dev->config.delay_us(us);
    }
}

static inline bool hal_spi_transfer(ad2s1210_dev_t *dev, const uint8_t *tx, uint8_t *rx, size_t len) {
    if (dev->config.spi_transfer) {
        return dev->config.spi_transfer(dev->config.user_ctx, tx, rx, len);
    }
    return false;
}

/**
 * @brief Розрахунок максимальної кутової швидкості (RPS) для поточної роздільної здатності та тактування.
 */
static float get_max_velocity_rps(ad2s1210_resolution_t res, uint32_t clk_hz) {
    float clk_factor = (float)clk_hz / 8192000.0f;
    switch (res) {
        case AD2S1210_RES_10BIT: return 2500.0f * clk_factor;
        case AD2S1210_RES_12BIT: return 1000.0f * clk_factor;
        case AD2S1210_RES_14BIT: return 500.0f  * clk_factor;
        case AD2S1210_RES_16BIT:
        default:                 return 125.0f  * clk_factor;
    }
}

/**
 * @brief Запис регістра в конфігураційному режимі AD2S1210.
 */
static ad2s1210_status_t write_register(ad2s1210_dev_t *dev, uint8_t reg_addr, uint8_t val) {
    ad2s1210_status_t status = ad2s1210_set_mode(dev, AD2S1210_MODE_CONFIG);
    if (status != AD2S1210_OK) return status;

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_LOW);

    /* Операція запису регістра складається з двох байтів: адреса та дані */
    uint8_t tx[2] = { reg_addr, val };
    uint8_t rx[2] = { 0 };

    bool ok = hal_spi_transfer(dev, tx, rx, 2);

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_HIGH);

    return ok ? AD2S1210_OK : AD2S1210_ERR_SPI_FAIL;
}

ad2s1210_status_t ad2s1210_init(ad2s1210_dev_t *dev, const ad2s1210_config_t *config) {
    if (!dev || !config) {
        return AD2S1210_ERR_INVALID_ARG;
    }

    if (!config->gpio_write || !config->gpio_read || !config->delay_us || !config->spi_transfer) {
        return AD2S1210_ERR_HAL_NULL;
    }

    memset(dev, 0, sizeof(ad2s1210_dev_t));
    dev->config = *config;

    /* Встановлення дефолтних апаратних сигналів */
    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_HIGH);
    hal_gpio_write(dev, AD2S1210_PIN_SAMPLE, AD2S1210_PIN_HIGH);
    hal_gpio_write(dev, AD2S1210_PIN_RESET, AD2S1210_PIN_HIGH);

    /* Апаратне скидання мікросхеми */
    ad2s1210_status_t status = ad2s1210_hardware_reset(dev);
    if (status != AD2S1210_OK) {
        return status;
    }

    /* Налаштування частоти збудження первинної обмотки */
    status = ad2s1210_set_excitation_frequency(dev, config->excitation_freq_hz);
    if (status != AD2S1210_OK) {
        return status;
    }

    /* Налаштування контрольного регістра 0x92 (роздільна здатність, гістерезис, виходи) */
    status = ad2s1210_set_resolution(dev, config->resolution);
    if (status != AD2S1210_OK) {
        return status;
    }

    /* Повернення у стандартний режим зчитування кута */
    status = ad2s1210_set_mode(dev, AD2S1210_MODE_POSITION);
    if (status != AD2S1210_OK) {
        return status;
    }

    dev->is_initialized = true;
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_hardware_reset(ad2s1210_dev_t *dev) {
    hal_gpio_write(dev, AD2S1210_PIN_RESET, AD2S1210_PIN_LOW);
    hal_delay_us(dev, AD2S1210_T_RESET_US);
    hal_gpio_write(dev, AD2S1210_PIN_RESET, AD2S1210_PIN_HIGH);
    hal_delay_us(dev, AD2S1210_T_RESET_US);
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_set_mode(ad2s1210_dev_t *dev, ad2s1210_mode_t mode) {
    if (mode > AD2S1210_MODE_CONFIG) {
        return AD2S1210_ERR_INVALID_ARG;
    }

    ad2s1210_pin_state_t a0_state = (mode & 0x01) ? AD2S1210_PIN_HIGH : AD2S1210_PIN_LOW;
    ad2s1210_pin_state_t a1_state = (mode & 0x02) ? AD2S1210_PIN_HIGH : AD2S1210_PIN_LOW;

    hal_gpio_write(dev, AD2S1210_PIN_A0, a0_state);
    hal_gpio_write(dev, AD2S1210_PIN_A1, a1_state);
    hal_delay_us(dev, AD2S1210_T_SETTLE_US);

    dev->current_mode = mode;
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_trigger_sample(ad2s1210_dev_t *dev) {
    /* Імпульс SAMPLE спадає в 0 для фіксації кута та швидкості в регістрах вибірки */
    hal_gpio_write(dev, AD2S1210_PIN_SAMPLE, AD2S1210_PIN_LOW);
    hal_delay_us(dev, AD2S1210_T_SAMPLE_US);
    hal_gpio_write(dev, AD2S1210_PIN_SAMPLE, AD2S1210_PIN_HIGH);
    hal_delay_us(dev, AD2S1210_T_SETTLE_US);
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_read_position_raw(ad2s1210_dev_t *dev, uint16_t *raw_pos) {
    if (!dev || !raw_pos) return AD2S1210_ERR_INVALID_ARG;

    ad2s1210_status_t status = ad2s1210_set_mode(dev, AD2S1210_MODE_POSITION);
    if (status != AD2S1210_OK) return status;

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_LOW);

    uint8_t tx[2] = { 0x00, 0x00 };
    uint8_t rx[2] = { 0x00, 0x00 };

    bool ok = hal_spi_transfer(dev, tx, rx, 2);

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_HIGH);

    if (!ok) return AD2S1210_ERR_SPI_FAIL;

    *raw_pos = ((uint16_t)rx[0] << 8) | rx[1];
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_read_velocity_raw(ad2s1210_dev_t *dev, int16_t *raw_vel) {
    if (!dev || !raw_vel) return AD2S1210_ERR_INVALID_ARG;

    ad2s1210_status_t status = ad2s1210_set_mode(dev, AD2S1210_MODE_VELOCITY);
    if (status != AD2S1210_OK) return status;

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_LOW);

    uint8_t tx[2] = { 0x00, 0x00 };
    uint8_t rx[2] = { 0x00, 0x00 };

    bool ok = hal_spi_transfer(dev, tx, rx, 2);

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_HIGH);

    if (!ok) return AD2S1210_ERR_SPI_FAIL;

    *raw_vel = (int16_t)(((uint16_t)rx[0] << 8) | rx[1]);
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_read_all(ad2s1210_dev_t *dev, ad2s1210_data_t *data) {
    if (!dev || !data) return AD2S1210_ERR_INVALID_ARG;
    if (!dev->is_initialized) return AD2S1210_ERR_NOT_INITIALIZED;

    memset(data, 0, sizeof(ad2s1210_data_t));

    /* 1. Стробування вибірки сигналом SAMPLE */
    ad2s1210_status_t status = ad2s1210_trigger_sample(dev);
    if (status != AD2S1210_OK) return status;

    /* 2. Зчитання апаратних виводів помилок (LOT і DOS є активними низькими) */
    data->lot_pin_active = (hal_gpio_read(dev, AD2S1210_PIN_LOT) == AD2S1210_PIN_LOW);
    data->dos_pin_active = (hal_gpio_read(dev, AD2S1210_PIN_DOS) == AD2S1210_PIN_LOW);

    /* 3. Опитування сирого коду кута */
    status = ad2s1210_read_position_raw(dev, &data->raw_position);
    if (status != AD2S1210_OK) return status;

    /* 4. Опитування сирого коду швидкості */
    status = ad2s1210_read_velocity_raw(dev, &data->raw_velocity);
    if (status != AD2S1210_OK) return status;

    /* 5. Якщо виявлено апаратні збої, зчитуємо детальний регістр помилок 0xFF */
    if (data->lot_pin_active || data->dos_pin_active) {
        ad2s1210_read_fault_register(dev, &data->fault_flags);
    }

    /* 6. Перетворення кодів у фізичні величини */
    uint8_t res_bits = (uint8_t)dev->config.resolution;
    uint16_t pos_mask = (res_bits == 16) ? 0xFFFF : ((1U << res_bits) - 1U);
    uint16_t pos_code = (data->raw_position >> (16 - res_bits)) & pos_mask;

    float max_counts = (float)(1U << res_bits);
    data->angle_degrees = ((float)pos_code * 360.0f) / max_counts;
    data->angle_radians = ((float)pos_code * 2.0f * M_PI) / max_counts;

    /* Обчислення швидкості з урахуванням роздільної здатності */
    float max_rps = get_max_velocity_rps(dev->config.resolution, dev->config.clk_in_hz);
    data->velocity_rps  = ((float)data->raw_velocity / 32768.0f) * max_rps;
    data->velocity_rpm  = data->velocity_rps * 60.0f;
    data->velocity_rads = data->velocity_rps * 2.0f * M_PI;

    return (data->lot_pin_active || data->dos_pin_active) ? AD2S1210_ERR_HARDWARE_FAULT : AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_read_fault_register(ad2s1210_dev_t *dev, ad2s1210_fault_flags_t *flags) {
    if (!dev || !flags) return AD2S1210_ERR_INVALID_ARG;

    ad2s1210_mode_t prev_mode = dev->current_mode;

    ad2s1210_status_t status = ad2s1210_set_mode(dev, AD2S1210_MODE_CONFIG);
    if (status != AD2S1210_OK) return status;

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_LOW);

    uint8_t tx[1] = { AD2S1210_REG_FAULT };
    uint8_t rx[1] = { 0xFF };

    bool ok = hal_spi_transfer(dev, tx, rx, 1);

    hal_gpio_write(dev, AD2S1210_PIN_CS, AD2S1210_PIN_HIGH);

    ad2s1210_set_mode(dev, prev_mode);

    if (!ok) return AD2S1210_ERR_SPI_FAIL;

    /* Біти у регістрі 0xFF є активними низькими (0 = помилка). Нормалізуємо інверсією. */
    uint8_t raw = rx[0];
    flags->bits.parity_error     = ((raw & (1 << 0)) == 0) ? 1 : 0;
    flags->bits.config_change    = ((raw & (1 << 1)) == 0) ? 1 : 0;
    flags->bits.los_lot_combined = ((raw & (1 << 2)) == 0) ? 1 : 0;
    flags->bits.dos_phase_err    = ((raw & (1 << 3)) == 0) ? 1 : 0;
    flags->bits.dos_mismatch     = ((raw & (1 << 4)) == 0) ? 1 : 0;
    flags->bits.lot_fault        = ((raw & (1 << 5)) == 0) ? 1 : 0;
    flags->bits.dos_los_fault    = ((raw & (1 << 6)) == 0) ? 1 : 0;
    flags->bits.dos_clipping     = ((raw & (1 << 7)) == 0) ? 1 : 0;

    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_clear_faults(ad2s1210_dev_t *dev) {
    if (!dev) return AD2S1210_ERR_INVALID_ARG;

    /* Очищення прапорців у AD2S1210 виконується стробуванням SAMPLE у конфігураційному режимі */
    ad2s1210_mode_t prev_mode = dev->current_mode;
    ad2s1210_set_mode(dev, AD2S1210_MODE_CONFIG);

    ad2s1210_trigger_sample(dev);

    ad2s1210_set_mode(dev, prev_mode);
    return AD2S1210_OK;
}

ad2s1210_status_t ad2s1210_set_resolution(ad2s1210_dev_t *dev, ad2s1210_resolution_t res) {
    if (!dev) return AD2S1210_ERR_INVALID_ARG;

    uint8_t res_bits = 0;
    switch (res) {
        case AD2S1210_RES_10BIT: res_bits = 0x00; break;
        case AD2S1210_RES_12BIT: res_bits = 0x01; break;
        case AD2S1210_RES_14BIT: res_bits = 0x02; break;
        case AD2S1210_RES_16BIT: res_bits = 0x03; break;
        default: return AD2S1210_ERR_INVALID_ARG;
    }

    /* Регістр Control (0x92): [7:Addr/Data=1][6..5:RES1..RES0][4:SOE][3:ENCLK][2:FREQ][1:PHASE][0:DISABLE] */
    uint8_t ctrl_byte = (1 << 7) | (res_bits << 5);
    if (dev->config.enable_hysteresis) {
        ctrl_byte |= (1 << 4);
    }
    if (dev->config.enable_encoder_outputs) {
        ctrl_byte |= (1 << 3);
    }

    ad2s1210_status_t status = write_register(dev, AD2S1210_REG_CONTROL, ctrl_byte);
    if (status == AD2S1210_OK) {
        dev->config.resolution = res;
        dev->control_reg_shadow = ctrl_byte;
    }
    return status;
}

ad2s1210_status_t ad2s1210_set_excitation_frequency(ad2s1210_dev_t *dev, uint32_t freq_hz) {
    if (!dev || freq_hz < 2000 || freq_hz > 20000) {
        return AD2S1210_ERR_INVALID_ARG;
    }

    /* Формула розрахунку FCW (Frequency Control Word) з datasheet: FCW = (freq_hz * 32768) / clk_in_hz */
    uint32_t fcw = (uint32_t)lroundf(((float)freq_hz * 32768.0f) / (float)dev->config.clk_in_hz);
    if (fcw < 0x04 || fcw > 0x3C) {
        return AD2S1210_ERR_INVALID_ARG;
    }

    return write_register(dev, AD2S1210_REG_EXCITATION_FREQ, (uint8_t)fcw);
}

const char* ad2s1210_status_to_string(ad2s1210_status_t status) {
    switch (status) {
        case AD2S1210_OK:                 return "OK: Операція успішна";
        case AD2S1210_ERR_INVALID_ARG:    return "Помилка: Некоректні аргументи";
        case AD2S1210_ERR_HAL_NULL:       return "Помилка: Не ініціалізовано функції HAL";
        case AD2S1210_ERR_SPI_FAIL:       return "Помилка: Збій передачі даних SPI";
        case AD2S1210_ERR_HARDWARE_FAULT: return "Помилка: Апаратний збій резольвера (LOT/DOS)";
        case AD2S1210_ERR_TIMEOUT:        return "Помилка: Перевищено час очікування";
        case AD2S1210_ERR_NOT_INITIALIZED:return "Помилка: Драйвер не ініціалізований";
        default:                          return "Невідома помилка";
    }
}
