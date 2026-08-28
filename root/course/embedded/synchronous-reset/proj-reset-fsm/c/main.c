#include <stdint.h>
#include <stdbool.h>

typedef enum { RST_RESET, RST_WAIT_CLK, RST_SOFT, RST_RUN } reset_state_t;

/* апаратні перевірки/дії (реалізуються під конкретний чип) */
extern bool clock_stable(void);    /* генератор/PLL устаткувався? */
extern bool fault_active(void);    /* просіла напруга / наглядач / аварія? */
extern void outputs_disable(void); /* перевести виходи в безпечний стан */
extern void outputs_enable(void);  /* дозволити виходи у світ */
extern void core_bring_up(void);   /* ініціалізувати підсистеми */

reset_state_t reset_step(reset_state_t s) {
    /* аварія в будь-якому стані — миттєво в безпечний корінь (аналог
       асинхронної гілки у FSM на Verilog) */
    if (fault_active()) {
        outputs_disable();
        return RST_RESET;
    }
    switch (s) {
    case RST_RESET:
        outputs_disable();          /* виходи перекриті — найперше */
        return RST_WAIT_CLK;
    case RST_WAIT_CLK:
        return clock_stable() ? RST_SOFT : RST_WAIT_CLK;  /* чекаємо такт */
    case RST_SOFT:
        core_bring_up();            /* будимо нутрощі, виходи ще тримаємо */
        return RST_RUN;
    case RST_RUN:
        outputs_enable();           /* аж тепер пускаємо у світ */
        return RST_RUN;
    default:
        return RST_RESET;           /* ловець «неможливого» стану */
    }
}
