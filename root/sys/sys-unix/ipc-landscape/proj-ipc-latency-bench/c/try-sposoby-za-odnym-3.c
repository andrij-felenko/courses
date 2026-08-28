struct chan {
        _Atomic uint32_t to_b;
        unsigned char    pad0[60];
        _Atomic uint32_t to_a;
        unsigned char    pad1[60];
        unsigned char    data[];
};

static int MODE;
enum { M_PIPE, M_SEQ, M_SHM, M_SPIN };

/* Обгортки futex() у glibc немає — тільки через syscall().  FUTEX_PRIVATE_FLAG
   тут ставити НЕ можна: слово лежить у спільному відображенні, і чергу
   очікування ядро мусить шукати за фізичною сторінкою, а не за адресою. */
static long fwait(_Atomic uint32_t *w, uint32_t expect)
{
        return syscall(SYS_futex, (uint32_t *)w, FUTEX_WAIT, expect, NULL, NULL, 0);
}

static void publish(_Atomic uint32_t *w, uint32_t v)
{
        /* Спершу дані, потім слово — і саме release не дає переставити
           їх місцями ні компілятору, ні процесору. */
        atomic_store_explicit(w, v, memory_order_release);
        if (MODE != M_SPIN)
                syscall(SYS_futex, (uint32_t *)w, FUTEX_WAKE, 1, NULL, NULL, 0);
}

static void await_val(_Atomic uint32_t *w, uint32_t v)
{
        uint32_t cur;
        if (MODE == M_SPIN) {
                while (atomic_load_explicit(w, memory_order_acquire) != v)
                        RELAX();
                return;
        }
        /* Цикл обов'язковий: FUTEX_WAIT прокидається й без причини, а якщо
           слово змінилося між читанням і викликом — повертає EAGAIN. */
        while ((cur = atomic_load_explicit(w, memory_order_acquire)) != v)
                fwait(w, cur);
}
