#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферійних блоків */
#define RCC_BASE        0x40021000UL
#define GPIOA_BASE      0x48000000UL
#define OPAMP_BASE      0x40007800UL
#define COMP_BASE       0x40010200UL
#define DAC1_BASE       0x40007400UL
#define TIM1_BASE       0x40012C00UL
#define ADC1_BASE       0x50000000UL

/* Зсуви регістрів OPAMP, COMP, DAC, TIM1, ADC */
#define OPAMP1_CSR      (*(volatile uint32_t *)(OPAMP_BASE + 0x00))
#define OPAMP1_OTR      (*(volatile uint32_t *)(OPAMP_BASE + 0x18))

#define COMP1_CSR       (*(volatile uint32_t *)(COMP_BASE + 0x00))

#define DAC1_CR         (*(volatile uint32_t *)(DAC1_BASE + 0x00))
#define DAC1_DHR12R1    (*(volatile uint32_t *)(DAC1_BASE + 0x08))

#define TIM1_CR1        (*(volatile uint32_t *)(TIM1_BASE + 0x00))
#define TIM1_BDTR       (*(volatile uint32_t *)(TIM1_BASE + 0x44))
#define TIM1_SR         (*(volatile uint32_t *)(TIM1_BASE + 0x10))
#define TIM1_DIER       (*(volatile uint32_t *)(TIM1_BASE + 0x0C))

#define ADC1_CR         (*(volatile uint32_t *)(ADC1_BASE + 0x08))
#define ADC1_CFGR       (*(volatile uint32_t *)(ADC1_BASE + 0x0C))
#define ADC1_TR1        (*(volatile uint32_t *)(ADC1_BASE + 0x20))
#define ADC1_IER        (*(volatile uint32_t *)(ADC1_BASE + 0x04))
#define ADC1_ISR        (*(volatile uint32_t *)(ADC1_BASE + 0x00))

/* Бітові маски OPAMP */
#define OPAMP_CSR_OPAMPINTEN    (1UL << 30) /* Внутрішнє підключення виходу до ADC/COMP */
#define OPAMP_CSR_PGA_GAIN_16X  (0x3UL << 14)/* Коефіцієнт підсилення 16x */
#define OPAMP_CSR_VM_SEL_PGA    (0x2UL << 5) /* Інверсний вхід на внутрішній дільник PGA */
#define OPAMP_CSR_VP_SEL_INP0   (0x0UL << 2) /* Неінверсний вхід з зовнішнього піна */
#define OPAMP_CSR_OPAMPxEN      (1UL << 0)  /* Увімкнення підсилювача */
#define OPAMP_CSR_CALON         (1UL << 11) /* Запуск калібрування */
#define OPAMP_CSR_CALOUT        (1UL << 12) /* Вихід компаратора калібрування */

/* Бітові маски COMP */
#define COMP_CSR_LOCK           (1UL << 31) /* Блокування конфігурації регістра до Reset */
#define COMP_CSR_HYST_20MV      (0x2UL << 16)/* Гістерезис 20 мВ */
#define COMP_CSR_INPSEL_OPAMP   (0x1UL << 7) /* Неінверсний вхід підключений до OPAMP1_OUT */
#define COMP_CSR_INMSEL_DAC1_CH1(0x4UL << 4) /* Інверсний вхід підключений до DAC1_OUT1 */
#define COMP_CSR_COMPxEN        (1UL << 0)  /* Увімкнення компаратора */

/* Бітові маски TIM1 */
#define TIM_BDTR_MOE            (1UL << 15) /* Main Output Enable */
#define TIM_BDTR_AOE            (1UL << 14) /* Automatic Output Enable */
#define TIM_BDTR_BKE            (1UL << 12) /* Увімкнення входу Break */
#define TIM_BDTR_BKP            (0UL << 13) /* Полярність Break: високий рівень = аварія */
#define TIM_DIER_BIE            (1UL << 7)  /* Дозвіл переривання Break */
#define TIM_SR_BIF              (1UL << 7)  /* Прапорець переривання Break */

/* Калібрування зсуву нуля OPAMP */
void opamp_calibrate_offset(void) {
    /* 1. Увімкнення режиму калібрування для диференційного каскаду */
    OPAMP1_CSR |= OPAMP_CSR_CALON;

    /* Підбір тримінгу для транзисторів p-типу (TRIMOFFSETP) */
    uint32_t trim_p = 0;
    for (uint32_t i = 0; i < 32; ++i) {
        OPAMP1_OTR = (OPAMP1_OTR & ~0x1FUL) | (i & 0x1FUL);
        for (volatile int d = 0; d < 200; ++d); /* Затримка встановлення */
        if (OPAMP1_CSR & OPAMP_CSR_CALOUT) {
            trim_p = i;
            break;
        }
    }

    /* Підбір тримінгу для транзисторів n-типу (TRIMOFFSETN) */
    uint32_t trim_n = 0;
    for (uint32_t i = 0; i < 32; ++i) {
        OPAMP1_OTR = (OPAMP1_OTR & ~(0x1FUL << 8)) | ((i & 0x1FUL) << 8);
        for (volatile int d = 0; d < 200; ++d);
        if (OPAMP1_CSR & OPAMP_CSR_CALOUT) {
            trim_n = i;
            break;
        }
    }

    /* Завершення калібрування */
    OPAMP1_CSR &= ~OPAMP_CSR_CALON;
}

/* Ініціалізація вбудованого ОП у режимі PGA 16x */
void opamp_init_pga(void) {
    opamp_calibrate_offset();

    /* Налаштування: вхід INP0, зворотний зв'язок PGA 16x, вихід внутрішній */
    OPAMP1_CSR = OPAMP_CSR_OPAMPINTEN   |
                 OPAMP_CSR_PGA_GAIN_16X |
                 OPAMP_CSR_VM_SEL_PGA   |
                 OPAMP_CSR_VP_SEL_INP0  |
                 OPAMP_CSR_OPAMPxEN;
}

/* Ініціалізація опорного ЦАП для порогу струму (поріг 25 А) */
void dac_init_threshold(void) {
    /* 25 А * 5 мОм = 125 мВ. Підсилення 16x -> 2.0 В.
       Код ЦАП (12 біт, Vref = 3.3 В): (2.0 / 3.3) * 4095 = 2482 */
    DAC1_DHR12R1 = 2482;
    DAC1_CR |= (1UL << 0); /* Увімкнення каналу 1 ЦАП */
}

/* Ініціалізація компаратора COMP1 з прямим зв'язком до TIM1 Break */
void comp_init_protection(void) {
    COMP1_CSR = COMP_CSR_HYST_20MV       |
                COMP_CSR_INPSEL_OPAMP    |
                COMP_CSR_INMSEL_DAC1_CH1 |
                COMP_CSR_COMPxEN;

    /* Блокування регістра для захисту від випадкового збою коду */
    COMP1_CSR |= COMP_CSR_LOCK;
}

/* Ініціалізація аварійного гальмування таймера ШІМ */
void tim1_break_init(void) {
    /* Дозвіл Break, полярність High, без авто-перезапуску (Lock), увімкнення виходів */
    TIM1_BDTR |= TIM_BDTR_BKE;
    TIM1_DIER |= TIM_DIER_BIE; /* Дозвіл переривання для діагностики */
    TIM1_BDTR |= TIM_BDTR_MOE; /* Активація виходів ШІМ */
}

/* Ініціалізація аналогового сторожового пса АЦП (AWD) */
void adc_awd_init(void) {
    /* Верхній поріг: 20 А (1.6 В -> код 1985), Нижній поріг: 0.1 В -> код 124 */
    ADC1_TR1 = ((1985UL & 0xFFFUL) << 16) | (124UL & 0xFFFUL);
    
    /* Увімкнення AWD на каналі 3 (ADC1_IN3 - підключеному до OPAMP1_OUT) */
    ADC1_CFGR |= (1UL << 23) | (3UL << 26); /* AWD1EN + канал 3 */
    ADC1_IER  |= (1UL << 7);                 /* Дозвіл переривання AWD1IE */
}

/* Обробник апаратного переривання Break від компаратора */
void TIM1_BRK_IRQHandler(void) {
    if (TIM1_SR & TIM_SR_BIF) {
        /* Аварія надструму: виходи заблоковані апаратно на рівні кремнію */
        TIM1_SR &= ~TIM_SR_BIF; /* Скидання прапорця переривання */
        
        /* Логування та перевірка стану системи */
        /* Повторне увімкнення виходів MOE можливе лише після повної діагностики */
    }
}
