static volatile uint64_t sink;   /* щоб оптимізатор не викинув цикл цілком */

/* Власний код: xorshift64 без жодного звертання до ядра. */
static void burn_user(double seconds)
{
    if (seconds <= 0.0) return;
    double deadline = now_mono() + seconds;
    uint64_t x = sink | 1u;
    do {
        for (int i = 0; i < 20000; i++) {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
        }
        sink = x;
    } while (now_mono() < deadline);
}

/* Код ядра: найдешевший виклик, що ГАРАНТОВАНО перетинає межу.
   Через syscall() навмисно — щоб жодна libc не підмінила його кешем. */
static void burn_sys(double seconds)
{
    if (seconds <= 0.0) return;
    double deadline = now_mono() + seconds;
    do {
        for (int i = 0; i < 64; i++)
            (void)syscall(SYS_getppid);
    } while (now_mono() < deadline);
}

/* Спалити ~seconds часу, чергуючи два види роботи скибками по slice секунд.
   Скибка навмисно менша за тик: саме дрібне чергування й робить поділ вибіркою. */
static void burn_mix(double seconds, double kfrac, double slice)
{
    double deadline = now_mono() + seconds;
    if (kfrac < 0.0) kfrac = 0.0;
    if (kfrac > 1.0) kfrac = 1.0;
    while (now_mono() < deadline) {
        burn_sys(slice * kfrac);
        burn_user(slice * (1.0 - kfrac));
    }
}
