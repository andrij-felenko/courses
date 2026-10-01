/**
 * @file main.c
 * @brief Головний модуль програми для демонстрації подієво-орієнтованої роботи драйвера ADXL345.
 * @details Виконує ініціалізацію системних годинників, периферійних модулів SPI1, DMA2 та EXTI GPIO,
 *          налаштовує акселерометр на ODR 100Гц і FIFO watermark 16 відліків, обробляє події та
 *          переводить ядро мікроконтролера у режим сну між пакетами вимірювань.
 */

#include "stm32f4xx_hal.h"
#include "adxl345_dma.h"
#include <stdio.h>

/* Глобальні об'єкти периферії HAL */
SPI_HandleTypeDef hspi1;
DMA_HandleTypeDef hdma_spi1_rx;
DMA_HandleTypeDef hdma_spi1_tx;

/* Глобальний хендл драйвера ADXL345 */
adxl345_handle_t g_adxl_dev;

/* Прапорець обробки отриманого пакета даних */
volatile uint8_t g_data_batch_ready = 0;

/* Прототипи функцій ініціалізації периферії */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_SPI1_Init(void);

/**
 * @brief Зворотний виклик готовності пакету даних акселерометра.
 * @details Викликається у контексті переривання SPI DMA.
 */
static void OnAdxlDataReady(adxl345_handle_t *hdev, uint8_t sample_count)
{
    (void)hdev;
    (void)sample_count;
    g_data_batch_ready = 1;
}

/**
 * @brief Зворотний виклик HAL при завершенні обміну SPI DMA (Tx/Rx complete).
 */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        ADXL345_OnSpiTxRxCplt(&g_adxl_dev);
    }
}

/**
 * @brief Зворотний виклик HAL при виникненні зовнішнього переривання EXTI.
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == g_adxl_dev.config.int1_pin) {
        ADXL345_OnGpioExti(&g_adxl_dev, GPIO_Pin);
    }
}

/**
 * @brief Головна функція програми.
 */
int main(void)
{
    /* Ініціалізація підсистеми HAL */
    HAL_Init();

    /* Налаштування системного тактування */
    SystemClock_Config();

    /* Ініціалізація периферії: GPIO, DMA, SPI1 */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_SPI1_Init();

    /* Конфігурація драйвера ADXL345 */
    adxl345_config_t adxl_cfg;
    adxl_cfg.hspi = &hspi1;
    adxl_cfg.cs_port = GPIOA;
    adxl_cfg.cs_pin = GPIO_PIN_4;
    adxl_cfg.int1_port = GPIOB;
    adxl_cfg.int1_pin = GPIO_PIN_0;
    adxl_cfg.odr = ADXL345_ODR_100HZ;
    adxl_cfg.range = ADXL345_RANGE_4G;
    adxl_cfg.watermark_samples = 16;
    adxl_cfg.data_ready_cb = OnAdxlDataReady;

    /* Ініціалізація акселерометра */
    if (ADXL345_Init(&g_adxl_dev, &adxl_cfg) != ADXL345_OK) {
        /* Помилка ініціалізації датчика */
        while (1) {
            HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
            HAL_Delay(100);
        }
    }

    /* Головний подієвий цикл з переведенням ядра в режим Sleep між перериваннями */
    while (1) {
        if (g_data_batch_ready) {
            g_data_batch_ready = 0;

            /* Обробка пакету відліків у фоновому режимі (наприклад, аналіз 0-го відліку) */
            float x_acc = g_adxl_dev.samples[0].x_g;
            float y_acc = g_adxl_dev.samples[0].y_g;
            float z_acc = g_adxl_dev.samples[0].z_g;
            (void)x_acc;
            (void)y_acc;
            (void)z_acc;
        }

        /* Переведення ядра в енергозберігаючий режим Sleep до наступного переривання */
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    }
}

/**
 * @brief Конфігурація системного тактування (System Clock).
 */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM = 16;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5);
}

/**
 * @brief Ініціалізація модуля SPI1 у режимі SPI Mode 3.
 */
static void MX_SPI1_Init(void)
{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_HIGH; /* CPOL = 1 */
    hspi1.Init.CLKPhase = SPI_PHASE_2EDGE;     /* CPHA = 1 (Mode 3) */
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 10;
    HAL_SPI_Init(&hspi1);
}

/**
 * @brief Ініціалізація контролера DMA для шини SPI1.
 */
static void MX_DMA_Init(void)
{
    __HAL_RCC_DMA2_CLK_ENABLE();

    /* Конфігурація DMA RX (SPI1_RX) */
    hdma_spi1_rx.Instance = DMA2_Stream0;
    hdma_spi1_rx.Init.Channel = DMA_CHANNEL_3;
    hdma_spi1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_spi1_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_spi1_rx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_spi1_rx.Init.Mode = DMA_NORMAL;
    hdma_spi1_rx.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_spi1_rx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_spi1_rx);
    __HAL_LINKDMA(&hspi1, hdmarx, hdma_spi1_rx);

    /* Конфігурація DMA TX (SPI1_TX) */
    hdma_spi1_tx.Instance = DMA2_Stream3;
    hdma_spi1_tx.Init.Channel = DMA_CHANNEL_3;
    hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_spi1_tx.Init.Mode = DMA_NORMAL;
    hdma_spi1_tx.Init.Priority = DMA_PRIORITY_LOW;
    hdma_spi1_tx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_spi1_tx);
    __HAL_LINKDMA(&hspi1, hdmatx, hdma_spi1_tx);

    /* Налаштування переривань DMA */
    HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
    HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);
}

/**
 * @brief Ініціалізація портів GPIO (CS pin та INT1 EXTI pin).
 */
static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* Налаштування виводу CS (GPIOA Pin 4) */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
    GPIO_InitStruct.Pin = GPIO_PIN_4;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* Налаштування виводу INT1 (GPIOB Pin 0) як джерела EXTI переривання */
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    /* Налаштування переривання EXTI для лінії INT1 */
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}
