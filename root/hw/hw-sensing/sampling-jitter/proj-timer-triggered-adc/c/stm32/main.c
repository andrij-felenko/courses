/* 
 * Реалізація на мові C (STM32 HAL / Register Level)
 * Конфігурація TIM2 (генератор TRGO) + ADC1 (Hardware Trigger) + DMA2
 */

#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define BUFFER_SIZE     2048
#define HALF_BUFFER     (BUFFER_SIZE / 2)

/* Подвійний буфер відліків АЦП (вирівняний для DMA) */
static uint16_t adc_dma_buffer[BUFFER_SIZE] __attribute__((aligned(4)));

/* Прапорці готовності половин буфера для фонового обробника */
static volatile bool g_half_ready = false;
static volatile bool g_full_ready = false;

ADC_HandleTypeDef hadc1;
TIM_HandleTypeDef htim2;
DMA_HandleTypeDef hdma_adc1;

/**
 * @brief Налаштування таймера TIM2 як генератора тактових тригерів TRGO
 * @param sampling_freq Частота дискретизації в Герцах (наприклад, 100000 для 100 кГц)
 */
void Timer2_TRGO_Init(uint32_t sampling_freq) {
    __HAL_RCC_TIM2_CLK_ENABLE();

    /* Частота шини APB1 Timer Clock = 84 МГц */
    uint32_t timer_clock = 84000000;
    uint32_t period = (timer_clock / sampling_freq) - 1;

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 0;                     /* Без попереднього ділення */
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = period;                   /* Автоперезавантаження ARR */
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim2);

    /* Комутація події оновлення (Update Event) на вихідний тригер TRGO */
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig);
}

/**
 * @brief Налаштування АЦП ADC1 на апаратний запуск від TIM2 TRGO та роботу з DMA
 */
void ADC1_HardwareTrigger_DMA_Init(void) {
    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_DMA2_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* Налаштування аналогового входу PA0 (ADC1_IN0) */
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_ANALOG;
    gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* Налаштування DMA2 Stream 0 для ADC1 */
    hdma_adc1.Instance = DMA2_Stream0;
    hdma_adc1.Init.Channel = DMA_CHANNEL_0;
    hdma_adc1.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_adc1.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_adc1.Init.MemInc = DMA_MINC_ENABLE;
    hdma_adc1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD; /* 16 біт */
    hdma_adc1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;    /* 16 біт */
    hdma_adc1.Init.Mode = DMA_CIRCULAR;                           /* Кільцевий режим */
    hdma_adc1.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_adc1.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_adc1);

    __HAL_LINKDMA(&hadc1, DMA_Handle, hdma_adc1);

    /* Налаштування самого АЦП */
    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;         /* 21 МГц */
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;                      /* Суворо по тригеру! */
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
    hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIGCONV_T2_TRGO;   /* Апаратний запуск TIM2 TRGO */
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = ENABLE;                     /* Постійні запити DMA */
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    HAL_ADC_Init(&hadc1);

    /* Налаштування регулярного каналу: мінімальний час вибірки 3 цикли */
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    /* Увімкнення переривань DMA в контролері NVIC */
    HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

/**
 * @brief Колбек половини передачі DMA: заповнено першу половину adc_dma_buffer[0 ... 1023]
 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        g_half_ready = true;
    }
}

/**
 * @brief Колбек повної передачі DMA: заповнено другу половину adc_dma_buffer[1024 ... 2047]
 */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        g_full_ready = true;
    }
}

/**
 * @brief Запуск збору даних з нульовим програмним джиттером
 */
void Start_Acquisition(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_dma_buffer, BUFFER_SIZE);
    HAL_TIM_Base_Start(&htim2);
}
