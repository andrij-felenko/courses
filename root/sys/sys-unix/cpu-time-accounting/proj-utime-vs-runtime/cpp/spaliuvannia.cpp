static volatile uint64_t sink;   // щоб оптимізатор не викинув цикл цілком

// Власний код: xorshift64 без жодного звертання до ядра.
static void burn_user(double seconds)
{
    if (seconds <= 0.0) return;
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    uint64_t x = sink | 1u;
    do {
        for (int i = 0; i < 20000; i++) {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
        }
        sink = x;
    } while (steady_clock::now() < deadline);
}

// Код ядра: найдешевший виклик, що ГАРАНТОВАНО перетинає межу.
static void burn_sys(double seconds)
{
    if (seconds <= 0.0) return;
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    do {
        for (int i = 0; i < 64; i++)
            (void)syscall(SYS_getppid);
    } while (steady_clock::now() < deadline);
}

// Спалити ~seconds часу, чергуючи два види роботи скибками по slice секунд.
static void burn_mix(double seconds, double kfrac, double slice)
{
    using namespace std::chrono;
    auto deadline = steady_clock::now() + duration_cast<steady_clock::duration>(duration<double>(seconds));
    kfrac = std::clamp(kfrac, 0.0, 1.0);
    while (steady_clock::now() < deadline) {
        burn_sys(slice * kfrac);
        burn_user(slice * (1.0 - kfrac));
    }
}
