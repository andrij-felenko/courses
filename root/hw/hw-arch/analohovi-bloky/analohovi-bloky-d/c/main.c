#include <stdint.h>
#include <stdbool.h>

/* Адреси регістрів периферії */
#define OPAMP1_CSR_ADDR (*(volatile uint32_t *)0x40007800UL)
#define COMP1_CSR_ADDR  (*(volatile uint32_t *)0x40010200UL)
#define DAC1_DHR12R1_A  (*(volatile uint32_t *)0x40007408UL)
#define DAC1_CR_A       (*(volatile uint32_t *)0x40007400UL)
#define TIM1_BDTR_A     (*(volatile uint32_t *)0x40012C44UL)

/* Ініціалізація повного аналогового захисного тракту */
void hardware_protection_init(void) {
    /* 1. Налаштування порогу ЦАП: 2.0 В (відповідає струму 25 А при Gain=16x, R=5мОм) */
    DAC1_DHR12R1_A = 2482;           /* Код ЦАП для 2.0 В при Vref = 3.3 В */
    DAC1_CR_A |= (1UL << 0);         /* Увімкнення каналу 1 ЦАП */

    /* 2. Конфігурація вбудованого ОП: PGA 16x, внутрішнє з'єднання виходу */
    OPAMP1_CSR_ADDR = (1UL << 30) |  /* OPAMPINTEN: вихід на внутрішню шину */
                      (0x3UL << 14)| /* PGGAIN: 16x */
                      (0x2UL << 5) | /* VM_SEL: внутрішній дільник PGA */
                      (1UL << 0);    /* OPAMPxEN: увімкнення ОП */

    /* 3. Конфігурація компаратора: вхід від OPAMP, поріг від DAC1, гістерезис 20 мВ */
    COMP1_CSR_ADDR = (0x2UL << 16) | /* HYST: 20 мВ */
                     (0x1UL << 7)  | /* INPSEL: підключено до OPAMP1_OUT */
                     (0x4UL << 4)  | /* INMSEL: підключено до DAC1_OUT1 */
                     (1UL << 0);     /* COMPxEN: увімкнення компаратора */

    /* Блокування конфігурації компаратора від модифікацій */
    COMP1_CSR_ADDR |= (1UL << 31);   /* LOCK bit */

    /* 4. Активація захисту Break у таймері ШІМ */
    TIM1_BDTR_A |= (1UL << 12) |     /* BKE: дозвіл входу Break */
                   (1UL << 15);      /* MOE: головний дозвіл виходів */
}
