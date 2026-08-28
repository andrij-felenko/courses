#include "stm32f1xx.h"          /* CMSIS-заголовок конкретного чипа */

#define ADC_BUF_LEN  1024u

/* Статичний (не на стеку), 16-бітний (сам вирівняний), volatile — бо цю пам'ять
   змінює не ядро, і компілятор про це не здогадається. */
static volatile uint16_t adc_buf[ADC_BUF_LEN];

static volatile int8_t   ready_half = -1;   /* 0 — готова перша половина, 1 — друга */
static volatile uint32_t missed, errors;

void process(const volatile uint16_t *p, unsigned n);   /* корисна робота ядра */

/* ── Периферія: підняти АЦП і відкалібрувати (ще без жодного слова про DMA) ── */
static void adc1_bringup(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN | RCC_APB2ENR_IOPAEN;
    RCC->CFGR    &= ~RCC_CFGR_ADCPRE;
    RCC->CFGR    |= RCC_CFGR_ADCPRE_DIV6;        /* 72/6 = 12 МГц */

    GPIOA->CRL &= ~(GPIO_CRL_MODE0 | GPIO_CRL_CNF0);   /* PA0 — аналоговий вхід */

    ADC1->SMPR2 = ADC_SMPR2_SMP0_2;   /* 41.5 такту вибірки на каналі 0 */
    ADC1->SQR1  = 0;                  /* L = 0 → у послідовності один вимір */
    ADC1->SQR3  = 0;                  /* і це канал 0 */

    ADC1->CR2 |= ADC_CR2_ADON;                    /* вивести з режиму спокою */
    for (volatile int i = 0; i < 1000; i++) { }   /* дати стабілізуватися */
    ADC1->CR2 |= ADC_CR2_RSTCAL; while (ADC1->CR2 & ADC_CR2_RSTCAL) { }
    ADC1->CR2 |= ADC_CR2_CAL;    while (ADC1->CR2 & ADC_CR2_CAL)    { }
}

/* ── Канал DMA: анкета й ЗАМОК 1 ── */
static void dma1_ch1_setup(void)
{
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;            /* ① без такту блок не відповідає */

    DMA_Channel_TypeDef *ch = DMA1_Channel1;     /* ② АЦП1 просить лише сюди */

    ch->CCR &= ~DMA_CCR_EN;                      /* ③ відімкнути перед описом */
    while (ch->CCR & DMA_CCR_EN) { }             /*    дочекатися, поки справді ляже */
    DMA1->IFCR = DMA_IFCR_CGIF1;                 /* ④ стерти прапорці минулого прогону */

    ch->CPAR  = (uint32_t)&ADC1->DR;             /* ⑤ АДРЕСА регістра, не його вміст */
    ch->CMAR  = (uint32_t)adc_buf;               /* ⑥ адреса буфера */
    ch->CNDTR = ADC_BUF_LEN;                     /* ⑦ ЕЛЕМЕНТІВ, не байтів */

    ch->CCR = DMA_CCR_MINC                       /* ⑧ адреса в ОЗП росте (PINC = 0 → регістр стоїть) */
            | DMA_CCR_PSIZE_0                    /*    ширина з боку периферії — 16 біт */
            | DMA_CCR_MSIZE_0                    /*    ширина з боку пам'яті — теж 16 біт */
            | DMA_CCR_CIRC                       /*    кільце: з кінця — на початок */
            | DMA_CCR_PL_1                       /*    високий пріоритет каналу */
            | DMA_CCR_HTIE                       /*    IRQ на половині буфера */
            | DMA_CCR_TCIE                       /*    IRQ у кінці буфера */
            | DMA_CCR_TEIE;                      /*    IRQ на помилці доступу */
    /* DIR = 0 → джерело периферія; писати CCR присвоєнням, щоб не лишити хвостів */

    NVIC_SetPriority(DMA1_Channel1_IRQn, 5);     /* ⑨ дозвіл у контролері переривань */
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);

    ch->CCR |= DMA_CCR_EN;                       /* ⑩ ЗАМОК 1: канал зведено */
}

/* ── Периферія: ЗАМОК 2 і пуск ── */
static void adc1_start_stream(void)
{
    ADC1->CR2 |= ADC_CR2_CONT       /* міряти безперервно, а не по одному разу */
              |  ADC_CR2_DMA;       /* ЗАМОК 2: дозвіл піднімати запит до DMA */
    ADC1->CR2 |= ADC_CR2_EXTSEL;    /* EXTSEL = 111 → джерело пуску «SWSTART» */
    ADC1->CR2 |= ADC_CR2_EXTTRIG;   /* без цього біта тригер просто не слухають */
    ADC1->CR2 |= ADC_CR2_SWSTART;   /* пуск */
}

void DMA1_Channel1_IRQHandler(void)
{
    uint32_t isr = DMA1->ISR;

    if (isr & DMA_ISR_HTIF1) {              /* заповнена перша половина */
        DMA1->IFCR = DMA_IFCR_CHTIF1;       /* гасити прапорець ПЕРШИМ ДІЛОМ */
        if (ready_half >= 0) missed++;      /* ядро не забрало попередню — дедлайн зірвано */
        ready_half = 0;
    }
    if (isr & DMA_ISR_TCIF1) {              /* заповнена друга, кільце пішло на новий оберт */
        DMA1->IFCR = DMA_IFCR_CTCIF1;
        if (ready_half >= 0) missed++;
        ready_half = 1;
    }
    if (isr & DMA_ISR_TEIF1) {              /* помилка доступу: адреса нікуди не веде */
        DMA1->IFCR = DMA_IFCR_CTEIF1;
        errors++;                           /* канал при цьому вимкнувся сам */
    }
    __DSB();     /* запис гасіння мусить дійти до периферії ДО виходу з обробника */
}

int main(void)
{
    adc1_bringup();
    dma1_ch1_setup();       /* спершу канал… */
    adc1_start_stream();    /* …і лише потім дозвіл просити */

    for (;;) {
        int8_t h = ready_half;
        if (h >= 0) {
            ready_half = -1;                  /* заявку взято */
            __DMB();                          /* спершу прапорець, потім дані */
            process(&adc_buf[h * (ADC_BUF_LEN / 2)], ADC_BUF_LEN / 2);
        }
    }
}
