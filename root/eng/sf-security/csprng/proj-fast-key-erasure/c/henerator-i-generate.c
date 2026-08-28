#include <sys/types.h>
#include <unistd.h>

typedef struct {
    uint8_t key[32];   /* Kᵢ — єдиний секрет генератора */
    pid_t   pid;       /* чий це стан (для виявлення fork) */
} frng;

void frng_init(frng *r, const uint8_t seed[32]) {
    memcpy(r->key, seed, 32);   /* seed ← getrandom() від ядра */
    r->pid = getpid();
}
