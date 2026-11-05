#include "stm32f4xx.h"
#include <stdint.h>
#include <stdbool.h>

#define ADC_BUF_SAMPLES       16
#define ADC_HALF_BUF_SAMPLES  (ADC_BUF_SAMPLES / 2)
#define EWMA_SHIFT_VAL        3

#define THRESHOLD_WARN_RAW    3846U  /* ~3.1 В */
#define THRESHOLD_CRIT_RAW    3598U  /* ~2.9 В */

typedef enum {
    SYS_POWER_OK       = 0x00U,
    SYS_POWER_WARNING  = 0x01U,
    SYS_POWER_CRITICAL = 0x02U
} SysPowerStatus_t;

typedef struct {
    uint16_t dma_buffer[ADC_BUF_SAMPLES];
    volatile uint32_t filtered_raw;
    volatile SysPowerStatus_t status;
} PowerHardwareDriver_t;

static PowerHardwareDriver_t g_power_drv;

void PowerHW_InitRegisters(void) {
    /* 1. Вмикаємо тактування GPIOA, ADC1, DMA1, TIM3, PWR */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_DMA2EN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN | RCC_APB1ENR_PWREN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    /* 2. Конфігурація аналогового виводу PA0 (ADC1_IN0) */
    GPIOA->MODER |= (3U << (0 * 2)); /* Analog mode */
    GPIOA->PUPDR &= ~(3U << (0 * 2)); /* No pull-up/pull-down */

    /* 3. Конфігурація таймера TIM3 для генерації TRGO кожні 500 мкс (2 кГц) */
    TIM3->PSC = (SystemCoreClock / 1000000U) - 1U; /* Тактування 1 МГц */
    TIM3->ARR = 500U - 1U;                          /* Період 500 мкс */
    TIM3->CR2 &= ~TIM_CR2_MMS;
    TIM3->CR2 |= (2U << TIM_CR2_MMS_Pos);           /* Update event як TRGO */

    /* 4. Конфігурація DMA2 Stream0 Channel 0 (ADC1) */
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN);
    
    DMA2_Stream0->PAR = (uint32_t)&(ADC1->DR);
    DMA2_Stream0->M0AR = (uint32_t)g_power_drv.dma_buffer;
    DMA2_Stream0->NDTR = ADC_BUF_SAMPLES;
    DMA2_Stream0->CR = (0U << DMA_SxCR_CHSEL_Pos) |  /* Channel 0 */
                       (1U << DMA_SxCR_PL_Pos)    |  /* High priority */
                       (1U << DMA_SxCR_MSIZE_Pos) |  /* Memory 16-bit */
                       (1U << DMA_SxCR_PSIZE_Pos) |  /* Peripheral 16-bit */
                       DMA_SxCR_MINC              |  /* Memory increment */
                       DMA_SxCR_CIRC              |  /* Circular mode */
                       DMA_SxCR_HTIE              |  /* Half transfer IRQ */
                       DMA_SxCR_TCIE;                /* Transfer complete IRQ */

    /* 5. Конфігурація ADC1 */
    ADC1->CR1 = ADC_CR1_SCAN;
    ADC1->CR2 = ADC_CR2_DMA | ADC_CR2_DDS |
                (1U << ADC_CR2_EXTEN_Pos) |         /* Rising edge trigger */
                (8U << ADC_CR2_EXTSEL_Pos);         /* TIM3 TRGO event */
    ADC1->SQR1 = 0U;                                 /* 1 conversion */
    ADC1->SQR3 = 0U;                                 /* Channel 0 */
    ADC1->SMPR2 |= (4U << ADC_SMPR2_SMP0_Pos);      /* 84 cycles sampling */

    /* 6. Увімкнення переривання DMA у NVIC */
    NVIC_SetPriority(DMA2_Stream0_IRQn, 0);          /* Найвищий пріоритет */
    NVIC_EnableIRQ(DMA2_Stream0_IRQn);

    /* 7. Запуск периферійних модулів */
    DMA2_Stream0->CR |= DMA_SxCR_EN;
    ADC1->CR2 |= ADC_CR2_ADON;
    TIM3->CR1 |= TIM_CR1_CEN;
}

static inline void PowerHW_ProcessSampleChunk(const uint16_t *samples, size_t count) {
    uint32_t sum = 0;
    for (size_t i = 0; i < count; ++i) {
        sum += samples[i];
    }
    uint32_t avg = sum / count;

    if (g_power_drv.filtered_raw == 0) {
        g_power_drv.filtered_raw = avg;
    } else {
        g_power_drv.filtered_raw = ((g_power_drv.filtered_raw << EWMA_SHIFT_VAL) - 
                                     g_power_drv.filtered_raw + avg) >> EWMA_SHIFT_VAL;
    }

    if (g_power_drv.filtered_raw < THRESHOLD_CRIT_RAW) {
        g_power_drv.status = SYS_POWER_CRITICAL;
        
        /* Негайне аварійне блокування запису Flash та збереження стану */
        FLASH->CR &= ~FLASH_CR_PG;
        PWR->CR |= PWR_CR_DBP;
        RTC->BKP0R = 0xA5A5DEADU;
    } else if (g_power_drv.filtered_raw < THRESHOLD_WARN_RAW) {
        g_power_drv.status = SYS_POWER_WARNING;
    } else {
        g_power_drv.status = SYS_POWER_OK;
    }
}

void DMA2_Stream0_IRQHandler(void) {
    if (DMA2->LISR & DMA_LISR_HTIF0) {
        DMA2->LIFCR = DMA_LIFCR_CHTIF0;
        PowerHW_ProcessSampleChunk(&g_power_drv.dma_buffer[0], ADC_HALF_BUF_SAMPLES);
    }
    if (DMA2->LISR & DMA_LISR_TCIF0) {
        DMA2->LIFCR = DMA_LIFCR_CTCIF0;
        PowerHW_ProcessSampleChunk(&g_power_drv.dma_buffer[ADC_HALF_BUF_SAMPLES], ADC_HALF_BUF_SAMPLES);
    }
}
