/* platform_stm32.c — реалізація контракту плати на STM32 з HAL від ST.
 *
 * Розведення відповідає правилам статті: мікросхема АЦП стоїть на межі зон,
 * її аналогові виводи дивляться в аналоговий сектор, а SPI і DRDY йдуть у
 * цифровий бік і ніде не перетинають аналогової частини полігону.
 */
#include "platform.h"

#include "stm32f4xx_hal.h"

/* Ці об'єкти й функції породжує CubeMX у власних main.c та msp.c —
 * ми ними тільки користуємося. */
extern SPI_HandleTypeDef hspi1;
extern UART_HandleTypeDef huart2;

void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_SPI1_Init(void);
void MX_USART2_UART_Init(void);

/* SPI1: PA5 SCK, PA6 MISO, PA7 MOSI. Режим 1 (CPOL = 0, CPHA = 1),
 * швидкість не вище 4 МГц — довші фронти на шині дають менший di/dt,
 * а отже й менший індуктивний шум на землі. */
#define ADC_CS_PORT   GPIOA
#define ADC_CS_PIN    GPIO_PIN_4
#define ADC_DRDY_PORT GPIOA
#define ADC_DRDY_PIN  GPIO_PIN_3

#define SPI_TIMEOUT_MS  50u
#define UART_TIMEOUT_MS 100u

void board_init(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_USART2_UART_Init();

    /* CS відпускаємо явно: після скидання вивід міг лишитися в нулі,
     * і перша ж команда пішла б чипові в незрозумілому стані. */
    board_spi_release();
}

void board_spi_select(void)
{
    HAL_GPIO_WritePin(ADC_CS_PORT, ADC_CS_PIN, GPIO_PIN_RESET);
}

void board_spi_release(void)
{
    HAL_GPIO_WritePin(ADC_CS_PORT, ADC_CS_PIN, GPIO_PIN_SET);
}

bool board_spi_transfer(const uint8_t *tx, uint8_t *rx, size_t len)
{
    if (tx == NULL || rx == NULL || len == 0u || len > UINT16_MAX) {
        return false;
    }

    /* HAL приймає буфер передавання без const — приводимо явно, вміст
     * лишається недоторканим. */
    HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(&hspi1,
                                                   (uint8_t *)tx,
                                                   rx,
                                                   (uint16_t)len,
                                                   SPI_TIMEOUT_MS);
    return st == HAL_OK;
}

bool board_adc_data_ready(void)
{
    return HAL_GPIO_ReadPin(ADC_DRDY_PORT, ADC_DRDY_PIN) == GPIO_PIN_RESET;
}

uint32_t board_millis(void)
{
    return HAL_GetTick();
}

void board_delay_ms(uint32_t ms)
{
    HAL_Delay(ms);
}

/* Перенаправлення printf у UART: newlib для виведення кличе саме _write. */
int _write(int fd, char *data, int len)
{
    (void)fd;

    if (len <= 0) {
        return 0;
    }
    if (HAL_UART_Transmit(&huart2, (uint8_t *)data, (uint16_t)len, UART_TIMEOUT_MS) != HAL_OK) {
        return -1;
    }
    return len;
}
