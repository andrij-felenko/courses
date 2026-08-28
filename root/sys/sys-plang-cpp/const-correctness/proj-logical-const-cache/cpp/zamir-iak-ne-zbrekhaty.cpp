#include <chrono>
#include <cstdio>

template <class Doc>
void bench(const char* name, const Doc& doc, int reps) {
    doc.word_count();                                   // прогріти кеш

    volatile std::size_t sink = 0;                      // щоб цикл не викинули
    const auto t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < reps; ++i) sink += doc.word_count();
    const auto t1 = std::chrono::steady_clock::now();

    const double ns = std::chrono::duration<double, std::nano>(t1 - t0).count() / reps;
    std::printf("%-34s %7.2f нс/виклик\n", name, ns);
}
