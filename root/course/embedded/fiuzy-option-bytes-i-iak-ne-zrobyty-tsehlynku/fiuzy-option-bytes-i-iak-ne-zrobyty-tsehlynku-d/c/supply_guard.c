#include "supply_guard.h"
#include "stm32g4_regs.h"

/* Компаратор PVD виходить на режим за одиниці мікросекунд. Рахуємо холості
   оберти: точний час тут не потрібен, потрібна гарантія «не раніше». */
#define PVD_SETTLE_LOOPS  4000UL

static int pwr_clock_was_on;

void supply_guard_enable(supply_threshold_t level)
{
    volatile uint32_t readback;
    uint32_t cr2;

    pwr_clock_was_on = ((RCC_APB1ENR1 & RCC_APB1ENR1_PWREN) != 0UL);
    if (!pwr_clock_was_on) {
        RCC_APB1ENR1 |= RCC_APB1ENR1_PWREN;
        /* шина APB підхоплює дозвіл тактування із затримкою — читаємо назад */
        readback = RCC_APB1ENR1;
        (void)readback;
    }

    cr2 = PWR->CR2;
    cr2 &= ~PWR_CR2_PVDLS_MSK;
    cr2 |= ((uint32_t)level << PWR_CR2_PVDLS_POS) & PWR_CR2_PVDLS_MSK;
    cr2 |= PWR_CR2_PVDE;
    PWR->CR2 = cr2;

    for (volatile uint32_t spin = 0; spin < PVD_SETTLE_LOOPS; ++spin) {
    }
}

int supply_guard_above_threshold(void)
{
    /* PVDO = 1 означає «VDD нижче порога» — інверсія, на якій легко спіткнутися */
    return ((PWR->SR2 & PWR_SR2_PVDO) == 0UL) ? 1 : 0;
}

void supply_guard_disable(void)
{
    PWR->CR2 &= ~PWR_CR2_PVDE;

    /* Тактування PWR повертаємо в той стан, у якому знайшли: вимкнути чуже
       живлення периферії — надійний спосіб зламати роботу поруч. */
    if (!pwr_clock_was_on) {
        RCC_APB1ENR1 &= ~RCC_APB1ENR1_PWREN;
    }
}
