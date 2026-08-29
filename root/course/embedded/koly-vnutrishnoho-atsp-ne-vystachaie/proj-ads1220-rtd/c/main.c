/* Вимір температури PT100 через ADS1220: 3-провідне підключення,
   логометрична опора на R_ref = 3.3 кОм, одиничні перетворення по 20 SPS
   і готовність результату за апаратним перериванням DRDY.

   Виводи (STM32G0): SPI1 на PA5/PA6/PA7, CS на PA4, DRDY на PB0.
   Тактування ядра лишається таким, як його налаштував стартовий код. */

#include <stdio.h>
#include <string.h>

#include "stm32g0xx_hal.h"

#include "ads1220.h"
#include "pt100.h"

#define CS_PORT     GPIOA
#define CS_PIN      GPIO_PIN_4
#define DRDY_PORT   GPIOB
#define DRDY_PIN    GPIO_PIN_0

static SPI_HandleTypeDef  hspi1;
static UART_HandleTypeDef huart2;
static ads1220_t          rtd;

static void report(const char *text)
{
    HAL_UART_Transmit(&huart2, (uint8_t *)text, (uint16_t)strlen(text), 100);
}

static void gpio_init(void)
{
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* CS тримаємо високим у спокої, інакше мікросхема з'їсть перший байт */
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);

    GPIO_InitTypeDef cs = {
        .Pin   = CS_PIN,
        .Mode  = GPIO_MODE_OUTPUT_PP,
        .Pull  = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_HIGH,
    };
    HAL_GPIO_Init(CS_PORT, &cs);

    /* DRDY — вихід із відкритим стоком, який АЦП притискає до нуля,
       коли результат готовий. Звідси підтяжка вгору й спадний фронт. */
    GPIO_InitTypeDef drdy = {
        .Pin  = DRDY_PIN,
        .Mode = GPIO_MODE_IT_FALLING,
        .Pull = GPIO_PULLUP,
    };
    HAL_GPIO_Init(DRDY_PORT, &drdy);

    HAL_NVIC_SetPriority(EXTI0_1_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_1_IRQn);
}

static HAL_StatusTypeDef spi_init(void)
{
    __HAL_RCC_SPI1_CLK_ENABLE();

    hspi1.Instance               = SPI1;
    hspi1.Init.Mode              = SPI_MODE_MASTER;
    hspi1.Init.Direction         = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize          = SPI_DATASIZE_8BIT;
    /* Режим 1: тактовий сигнал у спокої низький, дані знімаються
       по другому фронту — саме такий обмін чекає ADS1220. */
    hspi1.Init.CLKPolarity       = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase          = SPI_PHASE_2EDGE;
    hspi1.Init.NSS               = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_32; /* ~2 МГц */
    hspi1.Init.FirstBit          = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode            = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation    = SPI_CRCCALCULATION_DISABLE;

    return HAL_SPI_Init(&hspi1);
}

static HAL_StatusTypeDef uart_init(void)
{
    __HAL_RCC_USART2_CLK_ENABLE();

    huart2.Instance        = USART2;
    huart2.Init.BaudRate   = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits   = UART_STOPBITS_1;
    huart2.Init.Parity     = UART_PARITY_NONE;
    huart2.Init.Mode       = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl  = UART_HWCONTROL_NONE;

    return HAL_UART_Init(&huart2);
}

/* Обробник спаду DRDY. Тут не читають результат по SPI: обмін довгий,
   а переривання має лише позначити, що чекати вже нема чого. */
void HAL_GPIO_EXTI_Falling_Callback(uint16_t pin)
{
    if (pin == DRDY_PIN) {
        ads1220_drdy_isr(&rtd);
    }
}

int main(void)
{
    HAL_Init();
    gpio_init();

    if (uart_init() != HAL_OK || spi_init() != HAL_OK) {
        /* Без шини говорити нема ні з ким і нема чим */
        for (;;) { }
    }

    rtd.spi     = &hspi1;
    rtd.cs_port = CS_PORT;
    rtd.cs_pin  = CS_PIN;
    rtd.r_ref   = 3300.0f;  /* еталон 0.01 %, 5 ppm/°C */
    rtd.gain    = 16.0f;

    ads1220_status_t st = ads1220_init(&rtd);
    if (st != ADS1220_OK) {
        char line[96];
        snprintf(line, sizeof line, "ADS1220 не піднявся: %s\r\n", ads1220_strerror(st));
        report(line);
        for (;;) { }
    }

    /* Зміщення нуля міряємо один раз при старті, на прогрітій платі.
       Воно дрібне, але при 1.9 мкВ на сотку градуса дрібне вже видно. */
    st = ads1220_calibrate_offset(&rtd);
    if (st != ADS1220_OK) {
        char line[96];
        snprintf(line, sizeof line, "калібрування нуля не вдалося: %s\r\n",
                 ads1220_strerror(st));
        report(line);
    }

    for (;;) {
        char line[96];
        float r_ohms = 0.0f;

        st = ads1220_read_resistance(&rtd, &r_ohms);
        if (st != ADS1220_OK) {
            snprintf(line, sizeof line, "вимір зірвано: %s\r\n", ads1220_strerror(st));
            report(line);
            HAL_Delay(1000);
            continue;
        }

        float t_celsius = 0.0f;
        if (pt100_celsius_at(r_ohms, &t_celsius) != PT100_OK) {
            snprintf(line, sizeof line, "опір %.3f Ом поза діапазоном PT100\r\n",
                     (double)r_ohms);
            report(line);
            HAL_Delay(1000);
            continue;
        }

        snprintf(line, sizeof line, "R = %.4f Ом   T = %.3f C\r\n",
                 (double)r_ohms, (double)t_celsius);
        report(line);

        /* Пауза між вимірами — це ще й час, коли струми збудження вимкнені
           й датчик остигає від власного розігріву. */
        HAL_Delay(1000);
    }
}
