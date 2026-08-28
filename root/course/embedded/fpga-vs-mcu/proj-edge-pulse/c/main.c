#include <stdint.h>

#define NCH 4
volatile uint8_t prev;                  /* попередній стан входів IN0..IN3 */

/* read_inputs(): біти 0..3 = рівні IN0..IN3; pulse_out(ch): імпульс на OUTch */
extern uint8_t read_inputs(void);
extern void    pulse_out(int ch);

void EXTI_IRQHandler(void) {             /* викликається на зміну будь-якого входу */
    uint8_t now  = read_inputs();
    uint8_t rise = now & ~prev;          /* де 0 -> 1: наростальні фронти */
    prev = now;

    for (int ch = 0; ch < NCH; ch++)     /* канали обробляються ПО ЧЕРЗІ */
        if (rise & (1u << ch))
            pulse_out(ch);
}
