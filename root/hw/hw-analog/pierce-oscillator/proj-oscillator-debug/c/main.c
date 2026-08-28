#include <stdint.h>

/* Регістри беруться з CMSIS-заголовка виробника; тут суть показано
   на STM32-подібному RCC із зовнішнім генератором HSE.               */
#define RCC_CR         (*(volatile uint32_t *)0x40021000u)
#define RCC_CIR        (*(volatile uint32_t *)0x40021008u)
#define RCC_CR_HSEON   (1u << 16)   /* подати накачку на інвертор генератора */
#define RCC_CR_HSERDY  (1u << 17)   /* залізо підняло: «петля стабільна»     */
#define RCC_CR_CSSON   (1u << 19)   /* Clock Security System: стереже зрив   */
#define RCC_CIR_CSSF   (1u << 7)    /* прапор: CSS зловив зрив генератора    */
#define RCC_CIR_CSSC   (1u << 23)   /* запис 1 знімає прапор CSSF            */

/* Скільки разів опитати прапор, перш ніж визнати тишу. Рахувати під
   найгірший кут: висока Q плюс мороз -40 °C дають найдовший розгін.    */
#define HSE_START_TIMEOUT  20000u

typedef enum { OSC_OK, OSC_NO_START } osc_status_t;

/* Самоперевірка на старті: «чи ожила петля?» — машинною відповіддю. */
osc_status_t hse_start(void)
{
    RCC_CR |= RCC_CR_HSEON;                     /* увімкнути генератор */

    /* Чекаємо, поки апаратура САМА підніме прапор стабільності. Лічильник
       обов'язковий: без нього мовчазний кварц підвісив би чип назавжди. */
    uint32_t guard = HSE_START_TIMEOUT;
    while ((RCC_CR & RCC_CR_HSERDY) == 0u) {
        if (guard-- == 0u) {
            RCC_CR &= ~RCC_CR_HSEON;            /* прибрати накачку        */
            return OSC_NO_START;                /* тиша → бенч-діагностика */
        }
    }

    RCC_CR |= RCC_CR_CSSON;   /* завівся: тепер стережемо зрив під час роботи */
    return OSC_OK;
}

void clock_init(void)
{
    if (hse_start() == OSC_OK) {
        clock_switch_to_hse();   /* лише ТЕПЕР чіпляємо ядро, UART, таймери */
    } else {
        flag_oscillator_fault(); /* лишаємось на внутрішньому RC, не зависаємо */
    }
}

/* CSS б'є сюди, коли РОБОЧИЙ генератор раптом замовк (відпаяний кварц,
   тріщина, наводка). Апаратура вже перекинула такт на внутрішній RC.   */
void NMI_Handler(void)
{
    if (RCC_CIR & RCC_CIR_CSSF) {
        RCC_CIR |= RCC_CIR_CSSC;   /* зняти прапор */
        clock_loss_recover();      /* аварійний режим / контрольований рестарт */
    }
}
