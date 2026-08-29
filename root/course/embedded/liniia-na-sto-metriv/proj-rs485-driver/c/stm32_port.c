/* stm32_port.c — прив'язка драйвера до периферії STM32G4.
 *
 * USART1: PA9 (TX), PA10 (RX), PA12 (DE — він же USART1_RTS/DE в апаратному режимі).
 * DMA1_Channel4 — передавання, TIM7 — таймер пауз T1.5/T3.5/розвороту.
 *
 * RS485_HARDWARE_DE=1 передає керування DE самому UART (CR3_DEM): ядро більше
 * не смикає пін, а джиттер перемикання зникає.
 */
#include "rs485.h"

#include "stm32g4xx.h"

#ifndef RS485_HARDWARE_DE
#define RS485_HARDWARE_DE 0
#endif

#define USART_CLK_HZ 170000000u   /* тактова USART1 */
#define TIMER_CLK_HZ 170000000u   /* тактова TIM7 */

/* USART_CR1 */
#define CR1_UE       (1u << 0)
#define CR1_RE       (1u << 2)
#define CR1_TE       (1u << 3)
#define CR1_RXNEIE   (1u << 5)
#define CR1_TCIE     (1u << 6)
#define CR1_PEIE     (1u << 8)
#define CR1_DEDT_POS 16u          /* затримка зняття DE після стоп-біта */
#define CR1_DEAT_POS 21u          /* затримка старт-біта після підняття DE */
/* USART_CR3 */
#define CR3_EIE      (1u << 0)
#define CR3_DMAT     (1u << 7)
#define CR3_DEM      (1u << 14)
#define CR3_DEP      (1u << 15)
/* USART_ISR */
#define ISR_PE       (1u << 0)
#define ISR_FE       (1u << 1)
#define ISR_NE       (1u << 2)
#define ISR_ORE      (1u << 3)
#define ISR_RXNE     (1u << 5)
#define ISR_TC       (1u << 6)
/* USART_ICR */
#define ICR_PECF     (1u << 0)
#define ICR_FECF     (1u << 1)
#define ICR_NCF      (1u << 2)
#define ICR_ORECF    (1u << 3)
#define ICR_TCCF     (1u << 6)
/* DMA_CCR */
#define CCR_EN       (1u << 0)
#define CCR_TCIE     (1u << 1)
#define CCR_DIR_M2P  (1u << 4)
#define CCR_MINC     (1u << 7)
/* TIM_CR1 */
#define TIM_CR1_CEN_ (1u << 0)
#define TIM_CR1_URS_ (1u << 2)
#define TIM_CR1_OPM_ (1u << 3)

#define DMAMUX_REQ_USART1_TX 25u  /* номер запиту з таблиці DMAMUX (RM0440) */

static rs485_port_t g_bus;

static void de_write(bool on)
{
    GPIOA->BSRR = on ? (1u << 12) : (1u << (12 + 16));
}

static void dma_start(const uint8_t *buf, size_t len)
{
    DMA1_Channel4->CCR &= ~CCR_EN;
    DMA1->IFCR = 0xFu << 12;                       /* прапорці каналу 4 */
    DMA1_Channel4->CPAR = (uint32_t)(uintptr_t)&USART1->TDR;
    DMA1_Channel4->CMAR = (uint32_t)(uintptr_t)buf;
    DMA1_Channel4->CNDTR = (uint32_t)len;
    DMA1_Channel4->CCR = CCR_MINC | CCR_DIR_M2P | CCR_TCIE;

    USART1->ICR = ICR_TCCF;   /* прибрати TC від попереднього кадру */
    DMA1_Channel4->CCR |= CCR_EN;
}

static void dma_abort(void)
{
    DMA1_Channel4->CCR &= ~(CCR_EN | CCR_TCIE);
    DMA1->IFCR = 0xFu << 12;
}

static void tc_irq_enable(bool on)
{
    if (on) {
        USART1->ICR = ICR_TCCF;
        USART1->CR1 |= CR1_TCIE;
    } else {
        USART1->CR1 &= ~CR1_TCIE;
        USART1->ICR = ICR_TCCF;
    }
}

/* На класичному USART (F1/F4) ORE знімається читанням SR, а потім DR;
 * тут для цього є окремий регістр ICR. */
static void rx_error_clear(void)
{
    USART1->ICR = ICR_PECF | ICR_FECF | ICR_NCF | ICR_ORECF;
    (void)USART1->RDR;
}

static void timer_arm_us(uint32_t us)
{
    TIM7->CR1 = 0u;
    TIM7->PSC = (TIMER_CLK_HZ / 1000000u) - 1u;   /* тік — 1 мкс */
    TIM7->ARR = (us > 1u) ? (us - 1u) : 1u;
    TIM7->EGR = 1u;                                /* UG: перезавантажити PSC/ARR */
    TIM7->SR = 0u;                                 /* UG підняв UIF — прибираємо */
    TIM7->DIER = 1u;                               /* UIE */
    TIM7->CR1 = TIM_CR1_OPM_ | TIM_CR1_URS_ | TIM_CR1_CEN_;
}

static void timer_stop(void)
{
    TIM7->CR1 = 0u;
    TIM7->DIER = 0u;
    TIM7->SR = 0u;
}

static uint32_t irq_lock(void)
{
    const uint32_t saved = __get_PRIMASK();
    __disable_irq();
    return saved;
}

static void irq_unlock(uint32_t saved)
{
    if (saved == 0u) {
        __enable_irq();
    }
}

rs485_port_t *rs485_bus(void)
{
    return &g_bus;
}

void rs485_board_init(uint32_t baud)
{
    RCC->AHB2ENR |= (1u << 0);            /* GPIOA */
    RCC->AHB1ENR |= (1u << 0) | (1u << 2);/* DMA1, DMAMUX */
    RCC->APB2ENR |= (1u << 14);           /* USART1 */
    RCC->APB1ENR1 |= (1u << 5);           /* TIM7 */

    /* PA9/PA10 — альтернативна функція AF7 */
    GPIOA->MODER &= ~((3u << (9 * 2)) | (3u << (10 * 2)) | (3u << (12 * 2)));
    GPIOA->MODER |= (2u << (9 * 2)) | (2u << (10 * 2));
    GPIOA->AFR[1] &= ~((0xFu << ((9 - 8) * 4)) | (0xFu << ((10 - 8) * 4)) | (0xFu << ((12 - 8) * 4)));
    GPIOA->AFR[1] |= (7u << ((9 - 8) * 4)) | (7u << ((10 - 8) * 4));

#if RS485_HARDWARE_DE
    GPIOA->MODER |= (2u << (12 * 2));                 /* PA12 = USART1_DE */
    GPIOA->AFR[1] |= (7u << ((12 - 8) * 4));
#else
    GPIOA->MODER |= (1u << (12 * 2));                 /* PA12 — звичайний вихід */
    GPIOA->OSPEEDR |= (3u << (12 * 2));
    de_write(false);
#endif

    /* DMAMUX: канал 4 DMA1 = канал 3 мультиплексора */
    DMAMUX1_Channel3->CCR = DMAMUX_REQ_USART1_TX;

    USART1->CR1 = 0u;   /* DEAT/DEDT пишуться лише при UE = 0 */
    USART1->BRR = (USART_CLK_HZ + baud / 2u) / baud;
    USART1->CR3 = CR3_DMAT | CR3_EIE;
#if RS485_HARDWARE_DE
    USART1->CR3 |= CR3_DEM;                            /* DE веде периферія */
    USART1->CR1 |= (8u << CR1_DEAT_POS) | (8u << CR1_DEDT_POS);  /* по пів символу з боків */
#endif
    USART1->CR1 |= CR1_UE | CR1_TE | CR1_RE | CR1_RXNEIE | CR1_PEIE;

    static const rs485_hw_t hw = {
#if RS485_HARDWARE_DE
        .set_de = NULL,
#else
        .set_de = de_write,
#endif
        .tx_dma_start = dma_start,
        .tx_dma_abort = dma_abort,
        .tc_irq_enable = tc_irq_enable,
        .rx_error_clear = rx_error_clear,
        .timer_arm_us = timer_arm_us,
        .timer_stop = timer_stop,
        .irq_lock = irq_lock,
        .irq_unlock = irq_unlock,
    };
    rs485_init(&g_bus, &hw, baud);

    NVIC_SetPriority(USART1_IRQn, 1);
    NVIC_SetPriority(DMA1_Channel4_IRQn, 1);
    NVIC_SetPriority(TIM7_DAC_IRQn, 1);   /* ім'я вектора — за startup-файлом сімейства */
    NVIC_EnableIRQ(USART1_IRQn);
    NVIC_EnableIRQ(DMA1_Channel4_IRQn);
    NVIC_EnableIRQ(TIM7_DAC_IRQn);
}

void USART1_IRQHandler(void)
{
    const uint32_t isr = USART1->ISR;

    if ((isr & (ISR_ORE | ISR_FE | ISR_NE | ISR_PE)) != 0u) {
        uint32_t flags = 0u;
        if ((isr & ISR_ORE) != 0u) { flags |= RS485_RX_OVERRUN; }
        if ((isr & ISR_FE) != 0u)  { flags |= RS485_RX_FRAMING; }
        if ((isr & ISR_NE) != 0u)  { flags |= RS485_RX_NOISE; }
        rs485_isr_rx_error(&g_bus, flags);   /* усередині — rx_error_clear() */
        return;
    }

    if ((isr & ISR_RXNE) != 0u) {
        rs485_isr_rx(&g_bus, (uint8_t)USART1->RDR);
    }

    if ((isr & ISR_TC) != 0u && (USART1->CR1 & CR1_TCIE) != 0u) {
        USART1->ICR = ICR_TCCF;
        rs485_isr_uart_tc(&g_bus);
    }
}

void DMA1_Channel4_IRQHandler(void)
{
    if ((DMA1->ISR & (1u << 13)) != 0u) {   /* TCIF4 */
        DMA1->IFCR = 1u << 13;
        DMA1_Channel4->CCR &= ~CCR_EN;
        rs485_isr_dma_done(&g_bus);
    }
}

void TIM7_DAC_IRQHandler(void)
{
    if ((TIM7->SR & 1u) != 0u) {
        TIM7->SR = 0u;
        rs485_isr_timer(&g_bus);
    }
}
