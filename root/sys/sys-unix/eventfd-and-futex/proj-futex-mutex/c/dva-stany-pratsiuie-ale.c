void lock2(int *m)
{
    int c = 0;
    while (!__atomic_compare_exchange_n(m, &c, 1, 0,
                                        __ATOMIC_ACQUIRE, __ATOMIC_RELAXED)) {
        futex(m, FUTEX_WAIT_PRIVATE, 1);   /* спати, поки там 1 */
        c = 0;                             /* CAS затер очікуване значення */
    }
}

void unlock2(int *m)
{
    __atomic_store_n(m, 0, __ATOMIC_RELEASE);
    futex(m, FUTEX_WAKE_PRIVATE, 1);       /* щоразу, наосліп */
}
