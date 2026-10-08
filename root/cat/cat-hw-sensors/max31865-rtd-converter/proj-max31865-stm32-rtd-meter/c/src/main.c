#include "stm32f4xx_hal.h"
#include "sensor_app.h"

/**
 * @file main.c
 * @brief Головний модуль програмування STM32: ініціалізація периферії SPI, UART, GPIO/EXTI та запуск циклу.
 */

#define MAX31865_CS_PORT GPIOA
#define MAX31865_CS_PIN  GPIO_PIN_4
#define MAX31865_DRDY_PIN GPIO_PIN_0

SPI_HandleTypeDef hspi1;
UART_HandleTypeDef huart2;
max31865_app_t sensor_app;

/* --- Прототипи системних функцій ініціалізації --- */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
static void MX_USART2_UART_Init(void);

/**
 * @brief Обробник зовнішніх переривань HAL GPIO (EXTI).
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    sensor_app_on_drdy_interrupt(&sensor_app, GPIO_Pin, MAX31865_DRDY_PIN);
}

int main(void)
{
    /* Ініціалізація бібліотеки STM32 HAL та налаштування тактування */
    HAL_Init();
    SystemClock_Config();

    /* Ініціалізація периферійних модулів */
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_USART2_UART_Init();

    /* Налаштування та запуск застосунку вимірювання опору/температури */
    if (sensor_app_init(&sensor_app, &hspi1, MAX31865_CS_PORT, MAX31865_CS_PIN, &huart2) != MAX31865_OK) {
        /* При помилці ініціалізації драйвера зупиняємо виконання */
        while (1) {
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
            HAL_Delay(100);
        }
    }

    /* Головний суперцикл обробки вимірювальних подій */
    while (1) {
        sensor_app_process(&sensor_app);
        /* Пауза енергозбереження або виконання інших фонових задач */
        HAL_Delay(10);
    }
}

/* --- Конфігурація периферії STM32 HAL --- */

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
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

static void MX_SPI1_Init(void)
{
    __HAL_RCC_SPI1_CLK_ENABLE();

    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_2EDGE; /* SPI Mode 1 (CPOL=0, CPHA=1) для MAX31865 */
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_32;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 10;
    HAL_SPI_Init(&hspi1);
}

static void MX_USART2_UART_Init(void)
{
    __HAL_RCC_USART2_CLK_ENABLE();

    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart2);
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    /* Налаштування лінії CS (PA4) як цифрового виходу Push-Pull */
    HAL_GPIO_WritePin(MAX31865_CS_PORT, MAX31865_CS_PIN, GPIO_PIN_SET);
    GPIO_InitStruct.Pin = MAX31865_CS_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(MAX31865_CS_PORT, &GPIO_InitStruct);

    /* Налаштування входу переривання DRDY (PA0) як EXTI Falling Edge */
    GPIO_InitStruct.Pin = MAX31865_DRDY_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* Налаштування світлодіода індикації (PC13) */
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    /* Ввімкнення ліній переривання в контролері NVIC */
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}
