#include <stdint.h>
#include <stdio.h>

#define MAX_CRIT   8   /* стеля критеріїв у матриці */
#define MAX_CAND   6   /* стеля кандидатів          */

typedef struct {
    const char *name;      /* назва критерію, напр. "читаність на сонці" */
    uint8_t     weight;    /* вага; шкалу задаємо самі, тут — умовні 0..100 */
} Criterion;

typedef struct {
    const char *name;               /* назва кандидата, напр. "e-ink" */
    uint8_t     score[MAX_CRIT];    /* оцінка 1..5 за кожним критерієм */
} Candidate;
