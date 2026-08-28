#include <stdint.h>

/* Регістри SysTick (усі — volatile, бо їх крутить залізо) */
#define SYST_CSR   (*(volatile uint32_t *)0xE000E010u) /* контроль/статус */
#define SYST_RVR   (*(volatile uint32_t *)0xE000E014u) /* значення перезавантаження */
#define SYST_CVR   (*(volatile uint32_t *)0xE000E018u) /* поточне значення */

#define SYST_ENABLE     (1u << 0)   /* увімкнути лічильник */
#define SYST_CLKSOURCE  (1u << 2)   /* джерело — тактова ядра */

static uint32_t cpu_hz = 168000000u;   /* частота ядра, напр. 168 МГц */

void systick_init(void)
{
    SYST_RVR = 0x00FFFFFFu;                       /* макс. період (24 біти) */
    SYST_CVR = 0u;                                /* скинути лічильник */
    SYST_CSR = SYST_CLKSOURCE | SYST_ENABLE;      /* пуск від тактової ядра */
}

void delay_us(uint32_t us)
{
    /* скільки тактів ядра відповідає заданим мікросекундам */
    uint32_t ticks   = us * (cpu_hz / 1000000u);
    uint32_t start   = SYST_CVR;                  /* знімок лічильника */
    uint32_t elapsed = 0u;

    /* SysTick рахує ВНИЗ і загортається через 0; маска 0xFFFFFF робить
       віднімання коректним і на переході через нуль */
    while (elapsed < ticks) {
        uint32_t now = SYST_CVR;
        elapsed = (start - now) & 0x00FFFFFFu;
    }
}
