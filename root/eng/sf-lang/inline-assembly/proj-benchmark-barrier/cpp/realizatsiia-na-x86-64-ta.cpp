#include <cstdint>
#include <iostream>

/* Ідіоматична C++ обгортка над апаратним таймером процесора */
class CpuCycleTimer {
public:
    static uint64_t now() noexcept {
#if defined(__x86_64__) || defined(_M_X64)
        uint32_t lo = 0, hi = 0;
        asm volatile (
            "lfence\n\t"
            "rdtsc"
            : "=a" (lo), "=d" (hi)
            :
            : "memory"
        );
        return (static_cast<uint64_t>(hi) << 32) | lo;
#elif defined(__aarch64__)
        uint64_t val = 0;
        asm volatile (
            "isb\n\t"
            "mrs %0, cntvct_el0"
            : "=r" (val)
            :
            : "memory"
        );
        return val;
#else
        return 0;
#endif
    }
};

int main() {
    const uint64_t start = CpuCycleTimer::now();
    
    volatile int sum = 0;
    for (int i = 0; i < 1000; ++i) {
        sum += i;
    }
    
    const uint64_t end = CpuCycleTimer::now();
    std::cout << "Витрачено тактів процесора: " << (end - start) << '\n';
}
