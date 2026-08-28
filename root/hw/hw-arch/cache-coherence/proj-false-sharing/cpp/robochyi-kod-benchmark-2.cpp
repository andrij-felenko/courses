// Один потік: ITERS разів нарощує лічильник за адресою p.
// volatile — щоб компілятор не «згорнув» цикл у одне додавання й не викинув його.
static void hammer(volatile int64_t* p) {
    for (int64_t i = 0; i < ITERS; ++i)
        (*p)++;
}

// Прогнати N потоків, кожному дати адресу його лічильника (крок stride байтів
// між сусідніми лічильниками), і повернути час стінного годинника.
template <typename GetPtr>
static double run(GetPtr get_ptr) {
    std::vector<std::thread> pool;
    pool.reserve(N);

    auto t0 = std::chrono::steady_clock::now();
    for (int t = 0; t < N; ++t)
        pool.emplace_back(hammer, get_ptr(t));     // потік t б'є свій лічильник
    for (auto& th : pool)
        th.join();
    auto t1 = std::chrono::steady_clock::now();

    return std::chrono::duration<double>(t1 - t0).count();   // секунди
}

int main() {
    NaiveCounters  naive{};
    std::vector<PaddedCounter> padded(N);          // на купі, вирівнювання типу збережено

    double t_naive  = run([&](int t){ return &naive.v[t];       });
    double t_padded = run([&](int t){ return &padded[t].value;  });

    printf("наївно (в одній лінії):   %.3f c\n", t_naive);
    printf("вирівняно (своя лінія):   %.3f c\n", t_padded);
    printf("прискорення від ліку:     %.2f×\n",  t_naive / t_padded);

    // Довідка: реальний розмір структур — видно, що набивка спрацювала
    printf("sizeof(NaiveCounters)=%zu  sizeof(PaddedCounter)=%zu\n",
           sizeof(NaiveCounters), sizeof(PaddedCounter));
    return 0;
}
