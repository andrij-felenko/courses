#include "hardened_primitives.h"

#define TFC_BASE_ADDR            0x4002B000U
#define TFC_CR                   (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x00U))
#define TFC_IER                  (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x08U))
#define TFC_SR                   (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x04U))
#define TFC_ZCR                  (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x14U))

#define TFC_CONFIG_SECURE_MASK   (0x00000117U) /* Glitch + Clock + Temp + Shield + Zeroize */
#define TFC_INTERRUPT_ENABLE     (0x00000001U) /* NMI Security Interrupt */

void hardware_security_init(void) {
    HARDENED_BARRIER();
    
    /* Крок 1: Увімкнення схеми швидкого розряду захищеної пам'яті ключів */
    TFC_ZCR = 0x000000A5U; /* Ключ активації схеми Zeroization */
    HARDENED_BARRIER();
    
    /* Крок 2: Активація всіх сенсорів моніторингу та активного екрана */
    TFC_CR = TFC_CONFIG_SECURE_MASK;
    HARDENED_BARRIER();
    
    /* Крок 3: Дозвіл генерації немаскованого переривання NMI */
    TFC_IER = TFC_INTERRUPT_ENABLE;
    HARDENED_BARRIER();
    
    /* Верифікація успішного запуску апаратної системи захисту */
    if ((TFC_CR & TFC_CONFIG_SECURE_MASK) != TFC_CONFIG_SECURE_MASK) {
        hardened_panic_lockout();
    }
}

/* Обробник немаскованого переривання апаратної тривоги */
void NMI_Handler(void) {
    HARDENED_BARRIER();
    /* Апаратна схема автоматично очищає ключі, програмний обробник зупиняє ядро */
    while (1) {
        __asm__ volatile("wfi");
    }
}
