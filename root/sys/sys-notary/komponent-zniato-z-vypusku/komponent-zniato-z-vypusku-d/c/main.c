#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Коди помилок підсистеми збору даних */
typedef enum {
    ADC_STATUS_OK               = 0,
    ADC_STATUS_ERR_NULL_PTR     = -1,
    ADC_STATUS_ERR_COMM_TIMEOUT = -2,
    ADC_STATUS_ERR_CALIBRATION  = -3,
    ADC_STATUS_ERR_OUT_OF_BOUNDS= -4,
    ADC_STATUS_ERR_HW_REV       = -5
} adc_status_t;

/* Тип встановленого чіпа: оригінал або сумісна заміна */
typedef enum {
    ADC_CHIP_LEGACY_REV_A = 0x01,  /* Оригінал: 12 біт, повільне калібрування */
    ADC_CHIP_REPLACEMENT_B = 0x02  /* Заміна: 16 біт, швидкий конвеєр, інша карта регістрів */
} adc_chip_type_t;

/* Структура конфігурації вимірювального каналу */
typedef struct {
    uint8_t  channel_id;
    float    reference_voltage_v;
    float    gain_multiplier;
    float    offset_mv;
} adc_channel_config_t;

/* Покажчики на апаратні низькорівневі функції SPI/I2C */
typedef struct {
    adc_status_t (*spi_transfer)(uint8_t dev_id, const uint8_t *tx, uint8_t *rx, size_t len);
    void         (*delay_us)(uint32_t us);
    void         (*log_event)(const char *msg, int32_t code);
} adc_bus_ops_t;

/* Контекст драйвера АЦП */
typedef struct {
    uint8_t               device_id;
    adc_chip_type_t       chip_type;
    uint8_t               raw_resolution_bits;
    float                 lsb_voltage_step_v;
    const adc_bus_ops_t  *bus_ops;
    adc_channel_config_t  channels[8];
    uint8_t               channel_count;
    bool                  is_initialized;
} adc_device_t;

/* Ініціалізація та автодетекція ревізії змонтованого чіпа */
adc_status_t adc_init(adc_device_t *dev, uint8_t dev_id, const adc_bus_ops_t *ops) {
    if (!dev || !ops || !ops->spi_transfer || !ops->delay_us) {
        return ADC_STATUS_ERR_NULL_PTR;
    }

    memset(dev, 0, sizeof(adc_device_t));
    dev->device_id = dev_id;
    dev->bus_ops = ops;

    /* Читання регістра ідентифікації Device ID (адреса 0x00) */
    uint8_t tx_cmd[2] = {0x80, 0x00}; /* Читання регістру 0x00 */
    uint8_t rx_buf[2] = {0};

    adc_status_t st = ops->spi_transfer(dev_id, tx_cmd, rx_buf, 2);
    if (st != ADC_STATUS_OK) {
        return ADC_STATUS_ERR_COMM_TIMEOUT;
    }

    uint8_t silicon_id = rx_buf[1];

    /* Конфігурація параметрів залежно від виявленого кристала */
    if (silicon_id == 0xA1) {
        /* Оригінальний застарілий компонент: 12 біт */
        dev->chip_type = ADC_CHIP_LEGACY_REV_A;
        dev->raw_resolution_bits = 12;
        dev->lsb_voltage_step_v = 3.3f / 4096.0f;
        /* Оригінал потребує 250 мкс на прогрів внутрішнього ІОН */
        ops->delay_us(250);
    } else if (silicon_id == 0xB4) {
        /* Сумісна заміна іншого вендора: 16 біт */
        dev->chip_type = ADC_CHIP_REPLACEMENT_B;
        dev->raw_resolution_bits = 16;
        dev->lsb_voltage_step_v = 3.3f / 65536.0f;
        /* Новий чіп вимагає запису біта конфігурації у регістр 0x04 для 3.3V діапазону */
        uint8_t cfg_cmd[2] = {0x04, 0x12};
        st = ops->spi_transfer(dev_id, cfg_cmd, rx_buf, 2);
        if (st != ADC_STATUS_OK) return st;
        ops->delay_us(50);
    } else {
        if (ops->log_event) {
            ops->log_event("Невідомий кремнієвий ID АЦП", silicon_id);
        }
        return ADC_STATUS_ERR_HW_REV;
    }

    dev->is_initialized = true;
    return ADC_STATUS_OK;
}

/* Зчитування напруги каналу з автоматичним нормуванням розрядності */
adc_status_t adc_read_voltage(adc_device_t *dev, uint8_t channel_idx, float *voltage_out) {
    if (!dev || !voltage_out) return ADC_STATUS_ERR_NULL_PTR;
    if (!dev->is_initialized) return ADC_STATUS_ERR_CALIBRATION;
    if (channel_idx >= dev->channel_count) return ADC_STATUS_ERR_OUT_OF_BOUNDS;

    uint8_t tx_buf[3] = {0};
    uint8_t rx_buf[3] = {0};
    uint32_t raw_code = 0;

    if (dev->chip_type == ADC_CHIP_LEGACY_REV_A) {
        /* Оригінал: команда 0x10 + канал, відповідь 2 байти MSB-first */
        tx_buf[0] = 0x10 | (channel_idx & 0x07);
        adc_status_t st = dev->bus_ops->spi_transfer(dev->device_id, tx_buf, rx_buf, 3);
        if (st != ADC_STATUS_OK) return st;

        raw_code = ((uint32_t)(rx_buf[1] & 0x0F) << 8) | rx_buf[2];
    } else {
        /* Заміна: команда 0x30 + канал, відповідь 16 біт безпосередньо */
        tx_buf[0] = 0x30 | (channel_idx & 0x07);
        adc_status_t st = dev->bus_ops->spi_transfer(dev->device_id, tx_buf, rx_buf, 3);
        if (st != ADC_STATUS_OK) return st;

        raw_code = ((uint32_t)rx_buf[1] << 8) | rx_buf[2];
    }

    /* Нормалізація в абсолютні вольти за єдиною математичною шкалою */
    float raw_voltage = (float)raw_code * dev->lsb_voltage_step_v;
    const adc_channel_config_t *cfg = &dev->channels[channel_idx];
    
    *voltage_out = (raw_voltage * cfg->gain_multiplier) + (cfg->offset_mv / 1000.0f);
    return ADC_STATUS_OK;
}
