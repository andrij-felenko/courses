#include <stdint.h>
#include <string.h>

#define ARW_BITS 64

typedef enum {
    ARW_NEW,        /* новіша за все бачене */
    ARW_LATE,       /* запізніла, але ще не бачена — законна */
    ARW_DUPLICATE,  /* цей номер уже приймали */
    ARW_TOO_OLD     /* позаду вікна — розсудити неможливо */
} arw_verdict;

typedef struct {
    uint32_t top;        /* найбільший прийнятий номер */
    uint32_t first;      /* найменший номер, який ми взагалі бачили */
    uint64_t bits;       /* біт k ⇔ «номер top − k бачили»; біт 0 завжди 1 */
    int      started;    /* чи ініціалізовано першою датаграмою */

    uint64_t accepted;   /* прийнято унікальних номерів */
    uint64_t lost;       /* підтверджені втрати */
    uint64_t duplicate;  /* відкинуто як дублі */
    uint64_t reordered;  /* прийнято не по порядку */
    uint64_t too_old;    /* відкинуто як надто старі */
} arw;

void arw_init(arw *w) { memset(w, 0, sizeof *w); }
