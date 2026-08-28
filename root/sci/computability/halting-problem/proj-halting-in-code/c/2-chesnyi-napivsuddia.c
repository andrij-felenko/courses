#include <stdio.h>
#include <stdbool.h>

typedef enum { RUNNING, DONE } Status;
typedef Status (*Step)(long *state);   // один крок: рухає стан; DONE, коли спинилась

typedef enum { HALTS, UNKNOWN } Verdict;   // LOOPS не буває — у цьому вся суть

// Женемо step не більш як budget кроків.
Verdict halts_within(Step step, long init, long budget, long *steps_out) {
    long st = init;
    for (long i = 0; i < budget; i++) {
        if (step(&st) == DONE) {
            *steps_out = i + 1;
            return HALTS;              // достеменно спинилась — ми бачили
        }
    }
    *steps_out = budget;
    return UNKNOWN;                    // бюджет вичерпано — не знаємо
}

Status countdown(long *s) {            // рахує вниз до 0, тоді спиняється
    if (*s <= 0) return DONE;
    (*s)--;
    return RUNNING;
}

Status forever(long *s) {              // вічна
    (void)s;
    return RUNNING;
}

Status heavy(long *s) {                // уся праця — в одному кроці
    long acc = 0;
    for (long k = 0; k < 2000000; k++) acc += k;   // мільйони додавань під одним кроком
    *s = acc;
    return DONE;
}

int main(void) {
    const char *V[] = { "HALTS", "UNKNOWN" };
    long n; Verdict v;

    v = halts_within(countdown, 50,  10000, &n);
    printf("countdown(50),  б=10000 -> %-7s кроків %ld\n", V[v], n);
    v = halts_within(forever,   0,   10000, &n);
    printf("forever,        б=10000 -> %-7s кроків %ld\n", V[v], n);
    v = halts_within(countdown, 500, 100,   &n);
    printf("countdown(500), б=100   -> %-7s кроків %ld\n", V[v], n);
    v = halts_within(countdown, 500, 5000,  &n);
    printf("countdown(500), б=5000  -> %-7s кроків %ld\n", V[v], n);
    v = halts_within(heavy,     0,   5,     &n);
    printf("heavy,          б=5     -> %-7s кроків %ld\n", V[v], n);
    return 0;
}
