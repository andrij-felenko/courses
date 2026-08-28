#include <chrono>
#include <cstdint>
#include <iostream>

void bench_cpp(unsigned n) {
    using clock = std::chrono::steady_clock;
    volatile unsigned i = 0;

    const auto start = clock::now();
    for (i = 0; i < n; ++i) {
        if (sigsetjmp(g_resume, 1) == 0) {
            __asm__ volatile ("hlt");
        }
    }
    const auto end = clock::now();

    const auto total_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
    std::cout << "одна відмова ≈ " << (static_cast<double>(total_ns) / n) << " нс\n";
}
