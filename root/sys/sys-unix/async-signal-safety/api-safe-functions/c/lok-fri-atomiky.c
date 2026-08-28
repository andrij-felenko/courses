#include <stdatomic.h>

static _Atomic unsigned long long dropped;

/* перевірка на етапі складання: 2 — лок-фрі завжди, 1 — інколи, 0 — ніколи */
_Static_assert(ATOMIC_LLONG_LOCK_FREE == 2, "лічильник не лок-фрі на цій платформі");

static void on_signal(int signo)
{
    (void) signo;
    atomic_fetch_add_explicit(&dropped, 1, memory_order_relaxed);   /* можна з обробника */
}
