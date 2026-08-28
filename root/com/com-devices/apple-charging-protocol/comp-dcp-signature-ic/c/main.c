#include <stdbool.h>

#define PORTS      4u
#define BUDGET_HI  3u   /* скільки портів джерело здатне тягти на високій межі */

/* Прошарок заліза: доповідь порту й перемикання його межі струму. */
bool status_asserted(unsigned port);           /* true = порт реально бере багато */
void port_set_high(unsigned port, bool high);  /* true = висока межа, false = низька */

void ppm_poll(void)
{
    unsigned loaded = 0;
    for (unsigned i = 0; i < PORTS; i++)
        if (status_asserted(i))
            loaded++;

    /* Поки навантажених менше за бюджет — хай усі обіцяють багато.
       Щойно бюджет вибрано — ненавантажені зсуваємо на низьку межу. */
    bool tight = (loaded >= BUDGET_HI);

    for (unsigned i = 0; i < PORTS; i++)
        port_set_high(i, status_asserted(i) || !tight);
}
