/* повертає те, що лежало в *p (як апаратний cmpxchg) */
static inline int cas(int *p, int expected, int desired)
{
    __atomic_compare_exchange_n(p, &expected, desired, 0,
                                __ATOMIC_ACQUIRE, __ATOMIC_RELAXED);
    return expected;   /* при невдачі сюди записано справжнє значення */
}

void mutex_lock(int *m)
{
    int c = cas(m, 0, 1);
    if (c == 0)
        return;                              /* швидкий шлях: у ядро не йдемо */

    do {
        if (c == 2 || cas(m, 1, 2) != 0)     /* позначити: тут є охочі */
            futex(m, FUTEX_WAIT_PRIVATE, 2); /* спати, поки там 2 */
        c = cas(m, 0, 2);                    /* прокинулись — пробуємо взяти */
    } while (c != 0);
}

void mutex_unlock(int *m)
{
    if (__atomic_exchange_n(m, 0, __ATOMIC_RELEASE) == 2)
        futex(m, FUTEX_WAKE_PRIVATE, 1);
}
