/**
 * @file main.c
 * @brief Головний модуль запуску прошивки STM32: ініціалізація периферії та передача моменту.
 */

#include "stm32g4xx_hal.h"
#include "sea_controller.h"

SPI_HandleTypeDef hspi1;
TIM_HandleTypeDef htim1; /* ШІМ інвертора FOC 20 кГц */
TIM_HandleTypeDef htim6; /* Базовий таймер переривань 1 кГц */

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM6_Init(void);

int main(void) {
    /* 1. Ініціалізація низькорівневої бібліотеки HAL та тактування 170 МГц */
    HAL_Init();
    SystemClock_Config();

    /* 2. Налаштування апаратних портів введення-виведення та SPI */
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_TIM1_Init();
    MX_TIM6_Init();

    /* 3. Ініціалізація драйвера серійного пружного привода */
    Sea_Init(&hspi1, GPIOA, GPIO_PIN_4, GPIOA, GPIO_PIN_15);

    /* 4. Затримка для стабілізації живлення та калібрування нулів енкодерів */
    HAL_Delay(150);
    Sea_CalibrateZeros(200);

    /* 5. Запуск контуру FOC ШІМ на таймері TIM1 */
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);

    /* 6. Запуск таймера переривання контуру керування моментом (1 кГц) */
    HAL_TIM_Base_Start_IT(&htim6);

    /* 7. Встановлення початкового тестового крутного моменту */
    Sea_SetDesiredTorque(15.0f); /* 15 Н·м */

    while (1) {
        /* Фоновий цикл: моніторинг телеметрії та температурний захист */
        const SeaState_t *state = Sea_GetState();
        if (state->is_overloaded) {
            /* Аварійна зупинка інвертора при перевищенні порогу напружень */
            HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);
            HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_2);
            HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_3);
        }
        HAL_Delay(50);
    }
}

/**
 * @brief Обробник переривання таймера TIM6 (період 1 мс / 1 кГц)
 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM6) {
        Sea_Timer1kHz_ISR();
    }
}

static void MX_GPIO_Init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_4 | GPIO_PIN_15;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOA, &gpio);
}

static void MX_SPI1_Init(void) {
    __HAL_RCC_SPI1_CLK_ENABLE();
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_16BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_2EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    HAL_SPI_Init(&hspi1);
}

static void MX_TIM1_Init(void) {
    /* 20 кГц ШІМ для 3-фазного мосту FOC */
    __HAL_RCC_TIM1_CLK_ENABLE();
    htim1.Instance = TIM1;
    htim1.Init.Prescaler = 0;
    htim1.Init.CounterMode = TIM_COUNTERMODE_CENTERALIGNED1;
    htim1.Init.Period = 4250; /* 170 МГц / (2 * 4250) = 20 кГц */
    HAL_TIM_PWM_Init(&htim1);
}

static void MX_TIM6_Init(void) {
    /* 1 кГц таймер періодичного виклику ПІД */
    __HAL_RCC_TIM6_CLK_ENABLE();
    htim6.Instance = TIM6;
    htim6.Init.Prescaler = 169;
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = 999; /* 170 МГц / (170 * 1000) = 1 кГц */
    HAL_TIM_Base_Init(&htim6);
}

void SystemClock_Config(void) {
    /* Конфігурація тактування внутрішнього генератора до 170 МГц */
}
