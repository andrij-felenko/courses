#include <stdint.h>

/* Регістрові зміщення та маски для STM32G4 DMAMUX */
#define DMAMUX_REQ_GEN_EXTI0   1U
#define DMAMUX_REQ_ADC1_EOC    5U

typedef struct {
    volatile uint32_t CCR[16];   /* Канали конфігурації DMA (Channel Control Registers) */
    volatile uint32_t RGCR[4];   /* Регістри генераторів запитів (Request Generator) */
    volatile uint32_t RGSR;      /* Статус генераторів запитів */
    volatile uint32_t RGCFR;     /* Скидання прапорців генераторів */
} DMAMUX_Channel_Regs;

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t CCR1;
} TIM_TypeDef_Lite;

typedef struct {
    volatile uint32_t ISR;
    volatile uint32_t IER;
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t DR;
} ADC_TypeDef_Lite;

extern DMAMUX_Channel_Regs * const DMAMUX1_Regs;
extern TIM_TypeDef_Lite     * const TIM2_Regs;
extern ADC_TypeDef_Lite     * const ADC1_Regs;

void stm32_dmamux_pipeline_init(void) {
    /* 1. Налаштування TIM2 у режимі Master Mode (видача TRGO по збігу CCR1) */
    TIM2_Regs->PSC = 169;       /* 170 МГц / 170 = 1 МГц (1 мкс на тік) */
    TIM2_Regs->ARR = 1000;      /* Загальний період */
    TIM2_Regs->CCR1 = 10;       /* Імпульс через 10 мкс */
    
    /* CR2: MMS[2:0] = 0b100 (Compare Pulse - сигнал TRGO при збігу CC1IF) */
    TIM2_Regs->CR2 &= ~(0x7UL << 4);
    TIM2_Regs->CR2 |= (0x4UL << 4);

    /* SMCR: Slave Mode Selection - запуск по тригеру від EXTI (Trigger Mode) */
    TIM2_Regs->SMCR |= (0x6UL); /* SMS = 0b0110 (Trigger Mode) */

    /* 2. Налаштування ADC1: запуск від тригера TIM2_TRGO */
    /* CFGR: EXTEN = 0b01 (фронт), EXTSEL = 0b1011 (тригер від TIM2_TRGO) */
    ADC1_Regs->CFGR &= ~((0x3UL << 10) | (0x1FUL << 5));
    ADC1_Regs->CFGR |= (0x1UL << 10) | (0x0BUL << 5);
    ADC1_Regs->CFGR |= (1UL << 0); /* DMAEN: Дозвіл видачі DMA запитів */

    /* 3. Налаштування DMAMUX Channel 0 для маршрутизації сигналу ADC1 -> DMA1 Channel 1 */
    /* DMAMUX1 Channel 0 підключається до виходу запитів ADC1 (ідентифікатор 5) */
    DMAMUX1_Regs->CCR[0] = (DMAMUX_REQ_ADC1_EOC & 0x7FUL);

    /* 4. Запуск АЦП у режим очікування тригера */
    ADC1_Regs->CR |= (1UL << 2); /* ADSTART */
}
