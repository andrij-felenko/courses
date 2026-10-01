/**
 * @file adxl345_dma.c
 * @brief Реалізація драйвера акселерометра ADXL345 для STM32 HAL.
 * @details Містить функції ініціалізації датчика у режимі SPI Mode 3, конфігурування
 *          буфера FIFO Stream та переривання watermark INT1, запуск безблокуючого
 *          burst-зчитання через DMA та розпарсинг 16-бітних даних у g.
 */

#include "adxl345_dma.h"
#include <string.h>

/**
 * @brief Допоміжна функція для запису значення у регістр ADXL345 через SPI (блокуюча).
 */
adxl345_status_t ADXL345_WriteRegister(adxl345_handle_t *hdev, uint8_t reg, uint8_t val)
{
    if (hdev == NULL || hdev->config.hspi == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t tx_data[2];
    tx_data[0] = reg & 0x3F;
    tx_data[1] = val;

    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(hdev->config.hspi, tx_data, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_SET);

    return (status == HAL_OK) ? ADXL345_OK : ADXL345_ERROR;
}

/**
 * @brief Допоміжна функція для зчитування значення з регістру ADXL345 через SPI (блокуюча).
 */
adxl345_status_t ADXL345_ReadRegister(adxl345_handle_t *hdev, uint8_t reg, uint8_t *val)
{
    if (hdev == NULL || hdev->config.hspi == NULL || val == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t tx_data[2];
    uint8_t rx_data[2];

    tx_data[0] = (reg & 0x3F) | ADXL345_SPI_READ;
    tx_data[1] = 0x00;

    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(hdev->config.hspi, tx_data, rx_data, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_SET);

    if (status == HAL_OK) {
        *val = rx_data[1];
        return ADXL345_OK;
    }
    return ADXL345_ERROR;
}

/**
 * @brief Ініціалізація та налаштування акселерометра ADXL345.
 */
adxl345_status_t ADXL345_Init(adxl345_handle_t *hdev, const adxl345_config_t *cfg)
{
    if (hdev == NULL || cfg == NULL || cfg->hspi == NULL) {
        return ADXL345_ERR_PARAM;
    }

    memset(hdev, 0, sizeof(adxl345_handle_t));
    hdev->config = *cfg;
    hdev->state = ADXL345_STATE_UNINIT;

    /* Встановлюємо лінію CS у високий рівень (пасивний стан) */
    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_SET);
    HAL_Delay(10);

    /* Перевірка ідентифікатора пристрою DEVID (має бути 0xE5) */
    uint8_t devid = 0;
    if (ADXL345_ReadRegister(hdev, ADXL345_REG_DEVID, &devid) != ADXL345_OK) {
        hdev->state = ADXL345_STATE_ERROR;
        return ADXL345_ERROR;
    }

    if (devid != ADXL345_DEVID_VAL) {
        hdev->state = ADXL345_STATE_ERROR;
        return ADXL345_ERR_DEVID;
    }

    /* Переведення у режим Standby для безпечного налаштування регістрів */
    ADXL345_WriteRegister(hdev, ADXL345_REG_POWER_CTL, ADXL345_POWER_CTL_STANDBY);

    /* Налаштування формату даних: режим високої роздільності FULL_RES (4 мг/LSB) та вибраний діапазон */
    uint8_t data_fmt = ADXL345_DATA_FORMAT_FULL_RES | (cfg->range & 0x03);
    ADXL345_WriteRegister(hdev, ADXL345_REG_DATA_FORMAT, data_fmt);

    /* Масштабний коефіцієнт у режимі FULL_RES дорівнює 3.9 мг/LSB = 0.00390625 g/LSB */
    hdev->scale_factor = 0.00390625f;

    /* Налаштування частоти вихідних даних (ODR) */
    ADXL345_WriteRegister(hdev, ADXL345_REG_BW_RATE, cfg->odr & 0x0F);

    /* Обмеження розміру watermark у межах від 1 до 32 відліків */
    uint8_t watermark = cfg->watermark_samples;
    if (watermark == 0) {
        watermark = 1;
    } else if (watermark > ADXL345_MAX_FIFO_SAMPLES) {
        watermark = ADXL345_MAX_FIFO_SAMPLES;
    }
    hdev->config.watermark_samples = watermark;

    /* Конфігурування FIFO у режим Stream з заданим порогом watermark */
    uint8_t fifo_ctl = ADXL345_FIFO_STREAM | (watermark & 0x1F);
    ADXL345_WriteRegister(hdev, ADXL345_REG_FIFO_CTL, fifo_ctl);

    /* Налаштування генерації переривання Watermark на виводі INT1 */
    ADXL345_WriteRegister(hdev, ADXL345_REG_INT_MAP, 0x00);
    ADXL345_WriteRegister(hdev, ADXL345_REG_INT_ENABLE, ADXL345_INT_WATERMARK);

    /* Переведення пристрою у режим вимірювання (Measurement Mode) */
    ADXL345_WriteRegister(hdev, ADXL345_REG_POWER_CTL, ADXL345_POWER_CTL_MEASURE);

    hdev->state = ADXL345_STATE_IDLE;
    return ADXL345_OK;
}

/**
 * @brief Запуск безблокуючого пакетного зчитування FIFO через SPI DMA.
 */
adxl345_status_t ADXL345_TriggerBurstReadDMA(adxl345_handle_t *hdev)
{
    if (hdev == NULL) {
        return ADXL345_ERR_PARAM;
    }

    if (hdev->state != ADXL345_STATE_IDLE) {
        return ADXL345_BUSY;
    }

    uint8_t watermark = hdev->config.watermark_samples;
    uint16_t transfer_len = 1 + (watermark * ADXL345_BYTES_PER_SAMPLE);

    /* Команда burst-зчитання з регістру DATAX0 (0x32) з бітами READ (0x80) та MB (0x40) */
    hdev->tx_buf[0] = ADXL345_REG_DATAX0 | ADXL345_SPI_READ | ADXL345_SPI_MB;
    memset(&hdev->tx_buf[1], 0x00, transfer_len - 1);

    hdev->state = ADXL345_STATE_BUSY_DMA;

    /* Активація лінії CS (Reset у LOW) */
    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_RESET);

    /* Запуск прийому та передачі через SPI DMA */
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive_DMA(hdev->config.hspi,
                                                          hdev->tx_buf,
                                                          hdev->rx_buf,
                                                          transfer_len);
    if (status != HAL_OK) {
        HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_SET);
        hdev->state = ADXL345_STATE_ERROR;
        return ADXL345_ERROR;
    }

    return ADXL345_OK;
}

/**
 * @brief Обробник завершення обміну SPI DMA. Викликається із HAL_SPI_TxRxCpltCallback.
 */
void ADXL345_OnSpiTxRxCplt(adxl345_handle_t *hdev)
{
    if (hdev == NULL || hdev->state != ADXL345_STATE_BUSY_DMA) {
        return;
    }

    /* Деактивація лінії CS (Set у HIGH) одразу після завершення передачі */
    HAL_GPIO_WritePin(hdev->config.cs_port, hdev->config.cs_pin, GPIO_PIN_SET);

    uint8_t watermark = hdev->config.watermark_samples;

    /* Парсинг сирих байт даних у відліки акселерометра */
    for (uint8_t i = 0; i < watermark; i++) {
        uint16_t idx = 1 + (i * ADXL345_BYTES_PER_SAMPLE);

        int16_t raw_x = (int16_t)((uint16_t)hdev->rx_buf[idx] | ((uint16_t)hdev->rx_buf[idx + 1] << 8));
        int16_t raw_y = (int16_t)((uint16_t)hdev->rx_buf[idx + 2] | ((uint16_t)hdev->rx_buf[idx + 3] << 8));
        int16_t raw_z = (int16_t)((uint16_t)hdev->rx_buf[idx + 4] | ((uint16_t)hdev->rx_buf[idx + 5] << 8));

        hdev->samples[i].x_raw = raw_x;
        hdev->samples[i].y_raw = raw_y;
        hdev->samples[i].z_raw = raw_z;

        hdev->samples[i].x_g = (float)raw_x * hdev->scale_factor;
        hdev->samples[i].y_g = (float)raw_y * hdev->scale_factor;
        hdev->samples[i].z_g = (float)raw_z * hdev->scale_factor;
    }

    hdev->samples_count = watermark;
    hdev->state = ADXL345_STATE_DATA_READY;

    /* Викликаємо зворотний виклик прикладного рівня, якщо він зареєстрований */
    if (hdev->config.data_ready_cb != NULL) {
        hdev->config.data_ready_cb(hdev, watermark);
    }

    hdev->state = ADXL345_STATE_IDLE;
}

/**
 * @brief Обробник зовнішнього переривання EXTI від лінії INT1. Викликається із HAL_GPIO_EXTI_Callback.
 */
void ADXL345_OnGpioExti(adxl345_handle_t *hdev, uint16_t GPIO_Pin)
{
    if (hdev == NULL) {
        return;
    }

    if (GPIO_Pin == hdev->config.int1_pin) {
        if (hdev->state == ADXL345_STATE_IDLE) {
            ADXL345_TriggerBurstReadDMA(hdev);
        }
    }
}
